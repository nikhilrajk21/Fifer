"""Bounded local WebSocket relay; default provider is a deterministic mock."""
import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import sqlite3
import time
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from live_voice import MODEL, MockLiveProvider, VoiceFailure, audio_message, parse_event, setup_message

ORIGINS = {'http://127.0.0.1:5173', 'http://localhost:5173'}


@dataclass(frozen=True)
class VoiceLimits:
    session: float = 300
    setup: float = 10
    response: float = 15
    utterance: float = 20
    turns: int = 5
    daily: int = 2
    output_bytes: int = 15 * 24000 * 2


def utc_day():
    return datetime.now(timezone.utc).date().isoformat()


def identity(value):
    if not isinstance(value, str):
        raise VoiceFailure('Invalid anonymous browser identity.')
    try:
        parsed = UUID(value)
        if parsed.version != 4:
            raise ValueError()
    except ValueError:
        raise VoiceFailure('Invalid anonymous browser identity.') from None
    return hashlib.sha256(str(parsed).encode()).hexdigest()


def reserve(store, browser, day, limit):
    with store.connection(write=True) as db:
        db.execute('DELETE FROM voice_daily_usage WHERE utc_day < ?', (day,))
        row = db.execute('SELECT sessions FROM voice_daily_usage WHERE browser_hash=? AND utc_day=?', (browser, day)).fetchone()
        used = row['sessions'] if row else 0
        if used >= limit:
            raise VoiceFailure('Daily voice limit reached. No connection was started.')
        db.execute('INSERT INTO voice_daily_usage(browser_hash,utc_day,sessions) VALUES (?,?,1) '
                   'ON CONFLICT(browser_hash,utc_day) DO UPDATE SET sessions=sessions+1', (browser, day))
        return used + 1


def control(raw):
    if not isinstance(raw, str) or len(raw) > 500:
        raise VoiceFailure('Invalid voice control.')
    try:
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError()
        return value
    except (ValueError, TypeError):
        raise VoiceFailure('Invalid voice control.') from None


def install_voice(app, store, provider=None, limits=None, day_clock=utc_day):
    provider = provider or MockLiveProvider()
    limits = limits or VoiceLimits()
    active = set()

    @app.get('/api/voice/config')
    async def config():
        return {'mode': 'mock', 'live_calls_enabled': False, 'planned_model': MODEL,
                'session_seconds': limits.session, 'turns': limits.turns, 'daily_sessions': limits.daily,
                'utterance_seconds': limits.utterance, 'response_audio_seconds': 15,
                'setup_timeout_seconds': limits.setup, 'response_timeout_seconds': limits.response,
                'audio_saved': False, 'transcripts_saved': False}

    @app.websocket('/api/voice')
    async def voice(ws: WebSocket):
        if ws.headers.get('origin') not in ORIGINS:
            await ws.close(code=1008)
            return
        await ws.accept()
        wire = None
        browser = None
        tasks = []
        setup_tasks = []
        started = time.monotonic()
        try:
            message = await asyncio.wait_for(ws.receive(), min(limits.setup, limits.session))
            first = control(message.get('text'))
            if set(first) != {'type', 'browser_id', 'fictional'} or first['type'] != 'start' or first['fictional'] is not True:
                raise VoiceFailure('Confirm fictional, non-emergency voice use first.')
            browser = identity(first['browser_id'])
            if browser in active:
                browser = None  # Do not release another session's reservation.
                raise VoiceFailure('A voice session is already open for this browser.')
            active.add(browser)
            used = reserve(store, browser, day_clock(), limits.daily)
            async def configure():
                nonlocal wire
                wire = await provider.connect()
                await wire.send(setup_message())
                events = parse_event(await wire.recv())
                if events != [('ready', None)]:
                    raise VoiceFailure('Voice setup was not acknowledged.')
            # End/disconnect must cancel an in-flight provider setup, rather
            # than waiting for its timeout or allowing late setup to revive it.
            setup_tasks = [asyncio.create_task(configure()), asyncio.create_task(ws.receive())]
            remaining = max(0, limits.session - (time.monotonic() - started))
            done, _ = await asyncio.wait(setup_tasks, timeout=min(limits.setup, remaining), return_when=asyncio.FIRST_COMPLETED)
            if not done:
                raise TimeoutError()
            if setup_tasks[1] in done:
                early = setup_tasks[1].result()
                if early['type'] == 'websocket.disconnect':
                    return
                if early.get('text') and control(early['text']) == {'type': 'stop'}:
                    return
                raise VoiceFailure('Wait for voice setup before sending input.')
            setup_tasks[0].result()
            setup_tasks[1].cancel()
            await asyncio.gather(setup_tasks[1], return_exceptions=True)
            await ws.send_json({'type': 'ready', 'mode': 'mock', 'daily_used': used,
                                'setup_confirmed': True,
                                'remaining_seconds': max(0, limits.session - (time.monotonic() - started))})
            state = {'phase': 'ready', 'turns': 0, 'deadline': None, 'bytes_in': 0, 'bytes_out': 0}

            async def downstream():
                while True:
                    message = await ws.receive()
                    if message['type'] == 'websocket.disconnect':
                        return
                    pcm = message.get('bytes')
                    if pcm is not None:
                        if state['phase'] != 'recording' or not pcm or len(pcm) % 2 or len(pcm) > 6400:
                            raise VoiceFailure('Invalid microphone frame.')
                        state['bytes_in'] += len(pcm)
                        if state['bytes_in'] > int(limits.utterance * 32000):
                            raise VoiceFailure('User utterance limit reached.')
                        # Bound frame bursts as well as total duration (one second tolerance).
                        elapsed = time.monotonic() - state['recording_started']
                        if state['bytes_in'] > (elapsed + 1) * 32000:
                            raise VoiceFailure('Microphone stream exceeded real-time pacing.')
                        await wire.send(audio_message(pcm))
                        continue
                    value = control(message.get('text'))
                    if set(value) != {'type'}:
                        raise VoiceFailure('Invalid voice control.')
                    kind = value['type']
                    if kind == 'stop':
                        return
                    if kind == 'activity_start' and state['phase'] == 'ready':
                        if state['turns'] >= limits.turns:
                            raise VoiceFailure('Five-turn voice limit reached.')
                        state.update(phase='recording', turns=state['turns']+1, bytes_in=0, bytes_out=0,
                                     recording_started=time.monotonic(), deadline=time.monotonic()+limits.utterance)
                        await wire.send({'realtimeInput': {'activityStart': {}}})
                        await ws.send_json({'type': 'recording', 'turn': state['turns']})
                    elif kind == 'activity_end' and state['phase'] == 'recording':
                        # Even an immediate Mute before the first PCM frame must
                        # close the manual VAD activity, not the voice session.
                        state.update(phase='waiting', deadline=time.monotonic()+limits.response)
                        await ws.send_json({'type': 'waiting'})
                        await wire.send({'realtimeInput': {'activityEnd': {}}})
                    elif kind == 'playback_done' and state['phase'] == 'playback':
                        state.update(phase='ready', deadline=None)
                        await ws.send_json({'type': 'ready', 'mode': 'mock', 'turns_used': state['turns']})
                    else:
                        raise VoiceFailure('Voice control is unavailable in this state.')

            async def upstream():
                while True:
                    events = parse_event(await wire.recv())
                    for kind, data in events:
                        if kind in ('closed', 'interrupted'):
                            await ws.send_json({'type': kind})
                            return  # Close safely rather than keep a potentially active model running.
                        if kind == 'audio':
                            if state['phase'] not in ('waiting', 'speaking'):
                                raise VoiceFailure('Unexpected response audio.')
                            if state['phase'] == 'waiting':
                                state.update(phase='speaking', deadline=time.monotonic()+limits.response)
                            state['bytes_out'] += len(data)
                            if state['bytes_out'] > limits.output_bytes:
                                raise VoiceFailure('Response audio limit reached.')
                            await ws.send_bytes(data)
                        elif kind == 'turn_complete':
                            if state['phase'] not in ('waiting', 'speaking'):
                                raise VoiceFailure('Unexpected voice turn completion.')
                            state.update(phase='playback', deadline=time.monotonic()+limits.response)
                            await ws.send_json({'type': 'turn_complete'})
                        # generation_complete is not playback completion; usage/text are discarded.

            async def watchdog():
                while True:
                    await asyncio.sleep(.025)
                    now = time.monotonic()
                    if now - started >= limits.session:
                        raise VoiceFailure('Voice session time limit reached.')
                    if state['deadline'] and now >= state['deadline']:
                        raise VoiceFailure('Voice turn timed out. No retry was made.')

            tasks = [asyncio.create_task(fn()) for fn in (downstream, upstream, watchdog)]
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
        except (VoiceFailure, TimeoutError, sqlite3.Error, WebSocketDisconnect, RuntimeError, OSError) as error:
            # Never forward exception/provider text, headers, keys or user audio.
            try:
                code = 'limit' if isinstance(error, VoiceFailure) and 'limit reached' in str(error).lower() else 'unavailable'
                await ws.send_json({'type': 'error', 'code': code, 'message': 'Voice stopped or unavailable; a limit, timeout or connection error occurred. No retry was made. Grounding and Emergency Support remain available.'})
            except (RuntimeError, OSError, WebSocketDisconnect):
                pass
        finally:
            for task in tasks + setup_tasks:
                task.cancel()
            await asyncio.gather(*tasks, *setup_tasks, return_exceptions=True)
            if wire:
                try:
                    await asyncio.wait_for(wire.close(), 1)
                except (Exception, asyncio.CancelledError):
                    pass
            if browser:
                active.discard(browser)
            try:
                await ws.close(code=1000)
            except (RuntimeError, OSError, WebSocketDisconnect):
                pass

"""Gemini Live wire contract, exercised ONLY against an in-process mock.

No key loader or network connector is present. Adding a real transport requires
separate authorization. Audio/transcriptions are never logged or persisted.
"""
import asyncio
import base64
import json
import math
import struct

from chat_content import CONTENT

MODEL = 'gemini-3.8-live'
ENDPOINT = 'wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent'
INPUT_RATE = 16000
OUTPUT_RATE = 24000

LIVE_INSTRUCTIONS = (
    'You are the optional voice assistant for Fifer, a coursework skills prototype, not a therapist. '
    'Use a warm, brief, nonjudgmental tone. Ask only one focused question at a time, and only when needed. '
    'Be interruptible: yield immediately when interrupted; never insist on finishing a reply or continuing a session. '
    'Help only with fictional, non-emergency questions about Fifer skills and app usage. '
    'Ground answers in the supplied reviewed app context and the current fictional question. '
    'If the context does not supply an answer, say so rather than inventing information. '
    'Do not invent user records, history, profiles, feelings or observations, or infer surroundings or distress. '
    'Do not diagnose, give medical or treatment advice, assess safety, or claim treatment, clinical benefit, '
    'monitoring or human oversight. '
    'The application alone controls the fixed grounding sequence, its timing, Pause/Resume, Stop/Leave '
    'and independent static Emergency Support. Do not change, generate, advance or override those controls or steps. '
    'Use one Live model only. Do not use tools or a second model; either requires separate approval and implementation. '
    'Do not request recording or retention of audio or transcripts. Fifer does not save voice audio or transcripts; '
    'text saving opt-in does not enable voice recording. '
    'For unrelated requests, briefly explain that this assistant only helps with Fifer. '
    'No automatic emergency calling or messaging.'
)


class VoiceFailure(Exception):
    pass


def setup_message():
    instructions = LIVE_INSTRUCTIONS + '\n\nSupplied reviewed app context:\n' + '\n'.join(doc['text'] for doc in CONTENT)
    return {'setup': {
        'model': 'models/' + MODEL,
        'generationConfig': {'responseModalities': ['AUDIO']},
        'systemInstruction': {'parts': [{'text': instructions}]},
        'realtimeInputConfig': {'automaticActivityDetection': {'disabled': True}},
    }}


def audio_message(pcm):
    return {'realtimeInput': {'audio': {
        'data': base64.b64encode(pcm).decode('ascii'),
        'mimeType': 'audio/pcm;rate=16000',
    }}}


def parse_event(raw):
    """Normalize only approved events; drop all text/transcript fields in memory."""
    if not isinstance(raw, str) or len(raw) > 100000:
        raise VoiceFailure('Invalid voice event.')
    try:
        event = json.loads(raw)
        if not isinstance(event, dict) or 'error' in event or 'toolCall' in event or 'toolCallCancellation' in event:
            raise ValueError()
        result = []
        if 'setupComplete' in event:
            result.append(('ready', None))
        if 'goAway' in event:
            result.append(('closed', None))
        content = event.get('serverContent', {})
        if content.get('interrupted'):
            return [('interrupted', None)]
        for part in content.get('modelTurn', {}).get('parts', []):
            blob = part.get('inlineData')
            if blob is None:
                continue  # Never forward transcripts/text or retain them.
            if blob.get('mimeType') != 'audio/pcm;rate=24000':
                raise ValueError()
            pcm = base64.b64decode(blob['data'], validate=True)
            if not pcm or len(pcm) % 2 or len(pcm) > 48000:
                raise ValueError()
            result.append(('audio', pcm))
        if content.get('generationComplete'):
            result.append(('generation_complete', None))
        if content.get('turnComplete'):
            result.append(('turn_complete', None))
        return result
    except (ValueError, KeyError, TypeError, AttributeError):
        raise VoiceFailure('Invalid voice event.') from None


class MockWire:
    """No speech recognition: discard input and return a short synthetic tone.

    Same JSON event shapes as Live; queue is bounded. No recording, keys or
    network. A tone is deliberately not represented as a generated answer.
    """
    def __init__(self):
        self.queue = asyncio.Queue(maxsize=8)
        self.closed = False

    async def send(self, value):
        if 'setup' in value:
            await self.queue.put(json.dumps({'setupComplete': {}}))
        elif 'activityEnd' in value.get('realtimeInput', {}):
            pcm = b''.join(struct.pack('<h', int(1800 * math.sin(2 * math.pi * 440 * i / OUTPUT_RATE))) for i in range(4800))
            await self.queue.put(json.dumps({'serverContent': {'modelTurn': {'parts': [
                {'inlineData': {'mimeType': 'audio/pcm;rate=24000', 'data': base64.b64encode(pcm).decode('ascii')}}
            ]}, 'generationComplete': True, 'turnComplete': True}}))

    async def recv(self):
        return await self.queue.get()

    async def close(self):
        self.closed = True
        while not self.queue.empty():
            self.queue.get_nowait()


class MockLiveProvider:
    mode = 'mock'

    async def connect(self):
        return MockWire()


class GeminiLiveProvider:
    """Explicit fail-closed boundary; no live implementation is activated in V2."""
    mode = 'disabled'

    async def connect(self):
        # Refuse BEFORE reading a key or creating any network connection.
        raise VoiceFailure('Real Gemini Live calls are not authorized.')

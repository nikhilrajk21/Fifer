import asyncio
import base64
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import threading
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
from main import create_app
from live_voice import ENDPOINT, LIVE_INSTRUCTIONS, MODEL, GeminiLiveProvider, MockWire, VoiceFailure, audio_message, parse_event, setup_message
from chat_content import CONTENT
from voice import VoiceLimits, identity, reserve

ORIGIN = {'origin': 'http://127.0.0.1:5173'}


class Provider:
    def __init__(self, wire=None, fail=False):
        self.wire = wire or MockWire()
        self.calls = 0
        self.fail = fail

    async def connect(self):
        self.calls += 1
        if self.fail:
            raise OSError('private upstream detail must not escape')
        return self.wire


class SilentWire(MockWire):
    async def send(self, value):
        if 'setup' in value:
            await super().send(value)


class BadWire(MockWire):
    async def send(self, value):
        if 'setup' in value:
            await self.queue.put('{invalid')


class LoudWire(MockWire):
    async def send(self, value):
        if 'activityEnd' in value.get('realtimeInput', {}):
            part = {'inlineData': {'mimeType': 'audio/pcm;rate=24000', 'data': base64.b64encode(b'\0' * 200).decode()}}
            await self.queue.put(json.dumps({'serverContent': {'modelTurn': {'parts': [part]}}}))
        else:
            await super().send(value)


class VoiceContract(unittest.TestCase):
    def test_approved_instructions_are_backend_only_and_use_exact_curated_context(self):
        setup = setup_message()['setup']
        prompt = setup['systemInstruction']['parts'][0]['text']
        self.assertEqual(prompt, LIVE_INSTRUCTIONS + '\n\nSupplied reviewed app context:\n' + '\n'.join(doc['text'] for doc in CONTENT))
        for required in ('warm, brief, nonjudgmental', 'one focused question at a time',
                         'Be interruptible', 'coursework skills prototype, not a therapist',
                         'Do not invent user records', 'Do not diagnose, give medical or treatment advice',
                         'independent static Emergency Support', 'Stop/Leave', 'Use one Live model only',
                         'Do not use tools or a second model', 'does not save voice audio or transcripts'):
            self.assertIn(required, prompt)
        self.assertEqual(set(setup), {'model','generationConfig','systemInstruction','realtimeInputConfig'})
        self.assertEqual(setup['model'], 'models/gemini-3.8-live')
        for file in (Path(__file__).parents[2] / 'frontend' / 'src').rglob('*'):
            if file.suffix in {'.js','.vue'}:
                self.assertNotIn(LIVE_INSTRUCTIONS, file.read_text(encoding='utf-8'))

    def test_model_endpoint_setup_and_no_tools_transcription_history(self):
        self.assertEqual(MODEL, 'gemini-3.8-live')
        self.assertEqual(ENDPOINT, 'wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent')
        setup = setup_message()['setup']
        self.assertEqual(setup['model'], 'models/gemini-3.8-live')
        self.assertEqual(setup['generationConfig'], {'responseModalities': ['AUDIO']})
        self.assertTrue(setup['realtimeInputConfig']['automaticActivityDetection']['disabled'])
        self.assertNotIn('tools', setup)
        self.assertNotIn('Transcription', json.dumps(setup))
        self.assertNotIn('thinking', setup)

    def test_input_shape_and_all_output_parts_no_transcripts(self):
        value = audio_message(b'\x01\x00')
        self.assertEqual(value['realtimeInput']['audio']['mimeType'], 'audio/pcm;rate=16000')
        self.assertEqual(base64.b64decode(value['realtimeInput']['audio']['data']), b'\x01\x00')
        part = {'inlineData': {'mimeType': 'audio/pcm;rate=24000', 'data': 'AAA='}}
        events = parse_event(json.dumps({'serverContent': {'modelTurn': {'parts': [part, {'text':'not retained'}, part]},
            'inputTranscription': {'text':'not retained'}, 'generationComplete':True,'turnComplete':True}}))
        self.assertEqual([x[0] for x in events], ['audio','audio','generation_complete','turn_complete'])
        self.assertNotIn('not retained', str(events))

    def test_invalid_audio_tools_and_provider_error_fail_closed(self):
        for value in ('[]', '{bad', json.dumps({'toolCall':{}}), json.dumps({'error':{'message':'secret'}}),
                      json.dumps({'serverContent':{'modelTurn':{'parts':[{'inlineData':{'mimeType':'audio/wav','data':'AAA='}}]}}})):
            with self.subTest(value=value), self.assertRaises(VoiceFailure):
                parse_event(value)
        self.assertEqual(parse_event('{"serverContent":{"interrupted":true}}'), [('interrupted',None)])
        self.assertEqual(parse_event('{"goAway":{}}'), [('closed',None)])

    def test_live_provider_refuses_before_key_or_network(self):
        with patch('gemini_text.load_backend_key', side_effect=AssertionError('key must not be read')):
            with self.assertRaisesRegex(VoiceFailure, 'not authorized'):
                asyncio.run(GeminiLiveProvider().connect())


class VoiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.path = Path(self.temp.name) / 'voice.sqlite3'
        self.browser = str(uuid4())

    def tearDown(self):
        self.temp.cleanup()

    def app(self, provider=None, **limits):
        return create_app(self.path, voice_provider=provider, voice_limits=VoiceLimits(**limits))

    def start(self, ws, **extra):
        ws.send_json({'type':'start','browser_id':self.browser,'fictional':True, **extra})
        return ws.receive_json()

    def turn(self, ws):
        ws.send_json({'type':'activity_start'})
        self.assertEqual(ws.receive_json()['type'], 'recording')
        ws.send_bytes(b'\0' * 640)
        ws.send_json({'type':'activity_end'})
        self.assertEqual(ws.receive_json()['type'], 'waiting')

    def test_mock_turn_explicit_playback_completion_and_stop_cleanup(self):
        provider = Provider()
        with TestClient(self.app(provider)) as client:
            self.assertFalse(client.get('/api/voice/config').json()['live_calls_enabled'])
            with client.websocket_connect('/api/voice', headers=ORIGIN) as ws:
                ack = self.start(ws)
                self.assertEqual(ack['mode'], 'mock')
                self.assertTrue(ack['setup_confirmed'])
                self.turn(ws)
                self.assertEqual(len(ws.receive_bytes()), 9600)
                self.assertEqual(ws.receive_json()['type'], 'turn_complete')
                ws.send_json({'type':'playback_done'})
                self.assertEqual(ws.receive_json()['turns_used'], 1)
                ws.send_json({'type':'stop'})
                self.assertEqual(ws.receive()['type'], 'websocket.close')
            self.assertTrue(provider.wire.closed)
            self.assertEqual(provider.calls, 1)

    def test_daily_quota_survives_clear_and_restart_no_voice_content_saved(self):
        app = self.app()
        with TestClient(app) as client:
            client.patch('/api/settings',json={'history_epoch':0,'message_opt_in':True})
            for _ in range(2):
                with client.websocket_connect('/api/voice',headers=ORIGIN) as ws:
                    self.assertEqual(self.start(ws)['type'],'ready')
                    self.turn(ws); ws.receive_bytes(); ws.receive_json()
                    ws.send_json({'type':'stop'}); ws.receive()
            self.assertEqual(client.delete('/api/history?history_epoch=0').status_code,200)
            with app.state.store.connection() as db:
                self.assertEqual(set(dict(db.execute('SELECT * FROM voice_daily_usage').fetchone())), {'browser_hash','utc_day','sessions'})
                for table in ('messages','chat_messages','sessions','conversations','chat_sessions'):
                    self.assertEqual(db.execute(f'SELECT count(*) FROM {table}').fetchone()[0],0)
        with TestClient(self.app()) as client:
            with client.websocket_connect('/api/voice', headers=ORIGIN) as ws:
                self.assertEqual(self.start(ws)['type'],'error')

    def test_old_quota_removed_on_next_day_request(self):
        app = self.app()
        with TestClient(app):
            store = app.state.store
            reserve(store, identity(self.browser),'2026-01-01',2)
            reserve(store, identity(self.browser),'2026-01-02',2)
            with store.connection() as db:
                self.assertEqual([r['utc_day'] for r in db.execute('SELECT * FROM voice_daily_usage')],['2026-01-02'])

    def test_origin_rejected_before_reserving(self):
        with TestClient(self.app()) as client:
            with self.assertRaises(Exception):
                with client.websocket_connect('/api/voice', headers={'origin':'https://untrusted.example'}):
                    self.fail('Untrusted origin connected')

    def test_client_cannot_override_model_or_instructions(self):
        with TestClient(self.app()) as client:
            with client.websocket_connect('/api/voice', headers=ORIGIN) as ws:
                self.assertEqual(self.start(ws, model='unapproved')['type'], 'error')

    def test_concurrent_browser_rejected_without_releasing_first(self):
        with TestClient(self.app()) as client:
            with client.websocket_connect('/api/voice', headers=ORIGIN) as first:
                self.start(first)
                for _ in range(2):
                    with client.websocket_connect('/api/voice', headers=ORIGIN) as second:
                        self.assertEqual(self.start(second)['type'], 'error')
                first.send_json({'type':'stop'}); first.receive()

    def test_provider_error_invalid_setup_and_setup_timeout_no_retry_or_detail(self):
        class HangingWire(MockWire):
            async def send(self, value): pass
        for provider in (Provider(fail=True), Provider(BadWire()), Provider(HangingWire())):
            with self.subTest(provider=provider), TestClient(self.app(provider, setup=.05)) as client:
                self.browser = str(uuid4())
                with client.websocket_connect('/api/voice', headers=ORIGIN) as ws:
                    result = self.start(ws)
                    self.assertEqual(result['type'],'error')
                    self.assertNotIn('private',str(result))
                self.assertEqual(provider.calls,1)

    def test_response_timeout_and_audio_cap(self):
        for provider, limits in ((Provider(SilentWire()),{'response':.05}), (Provider(LoudWire()),{'output_bytes':100})):
            with self.subTest(limits=limits), TestClient(self.app(provider,**limits)) as client:
                self.browser = str(uuid4())
                with client.websocket_connect('/api/voice',headers=ORIGIN) as ws:
                    self.start(ws); self.turn(ws)
                    self.assertEqual(ws.receive_json()['type'],'error')
                self.assertTrue(provider.wire.closed)

    def test_provider_interruption_drops_same_event_audio_and_closes_cleanly(self):
        class InterruptedWire(MockWire):
            async def send(self, value):
                if 'activityEnd' in value.get('realtimeInput', {}):
                    await self.queue.put(json.dumps({'serverContent': {'interrupted': True,
                        'modelTurn': {'parts': [{'inlineData': {'mimeType':'audio/pcm;rate=24000','data':'AAA='}}]}}}))
                else:
                    await super().send(value)
        provider = Provider(InterruptedWire())
        with TestClient(self.app(provider)) as client:
            with client.websocket_connect('/api/voice', headers=ORIGIN) as ws:
                self.start(ws); self.turn(ws)
                self.assertEqual(ws.receive_json()['type'], 'interrupted')
                self.assertEqual(ws.receive()['type'], 'websocket.close')
            self.assertTrue(provider.wire.closed)

    def test_session_utterance_deadlines_and_pcm_limit(self):
        for limits, record in (({'session':.05},False), ({'utterance':.05},True)):
            with self.subTest(limits=limits), TestClient(self.app(**limits)) as client:
                self.browser = str(uuid4())
                with client.websocket_connect('/api/voice',headers=ORIGIN) as ws:
                    self.start(ws)
                    if record:
                        ws.send_json({'type':'activity_start'}); ws.receive_json()
                    self.assertEqual(ws.receive_json()['type'],'error')

    def test_five_turns_and_invalid_frame(self):
        with TestClient(self.app()) as client:
            with client.websocket_connect('/api/voice',headers=ORIGIN) as ws:
                self.start(ws)
                for _ in range(5):
                    self.turn(ws); ws.receive_bytes(); ws.receive_json()
                    ws.send_json({'type':'playback_done'}); ws.receive_json()
                ws.send_json({'type':'activity_start'})
                self.assertEqual(ws.receive_json()['type'],'error')
            self.browser = str(uuid4())
            with client.websocket_connect('/api/voice',headers=ORIGIN) as ws:
                self.start(ws); ws.send_bytes(b'odd')
                self.assertEqual(ws.receive_json()['type'],'error')

    def test_no_provider_network_or_key_on_normal_mock(self):
        with patch('gemini_text.load_backend_key',side_effect=AssertionError('no key')), patch('websockets.asyncio.client.connect',side_effect=AssertionError('no provider')):
            with TestClient(self.app()) as client:
                with client.websocket_connect('/api/voice',headers=ORIGIN) as ws:
                    self.assertEqual(self.start(ws)['type'],'ready')
                    ws.send_json({'type':'stop'}); ws.receive()

    def test_mute_without_first_pcm_frame_keeps_session_and_sends_manual_vad_end(self):
        class RecordingWire(MockWire):
            def __init__(self):
                super().__init__(); self.events=[]
            async def send(self,value):
                self.events.append(value)
                await super().send(value)
        provider=Provider(RecordingWire())
        with TestClient(self.app(provider)) as client:
            with client.websocket_connect('/api/voice',headers=ORIGIN) as ws:
                self.start(ws)
                ws.send_json({'type':'activity_start'});ws.receive_json()
                ws.send_json({'type':'activity_end'})
                self.assertEqual(ws.receive_json()['type'],'waiting')
                self.assertEqual(len(ws.receive_bytes()),9600)
                self.assertEqual(ws.receive_json()['type'],'turn_complete')
                self.assertFalse(provider.wire.closed)
                ws.send_json({'type':'playback_done'})
                self.assertEqual(ws.receive_json()['type'],'ready')
                ws.send_json({'type':'stop'});ws.receive()
            self.assertEqual(sum('activityEnd' in e.get('realtimeInput',{}) for e in provider.wire.events),1)
            self.assertNotIn('audioStreamEnd',str(provider.wire.events))
            self.assertTrue(provider.wire.closed)

    def test_end_during_provider_setup_cancels_setup_and_closes_wire(self):
        entered=threading.Event()
        class WaitingWire(MockWire):
            async def send(self,value):
                if 'setup' in value: entered.set()  # Deliberately never acknowledge.
        provider=Provider(WaitingWire())
        with TestClient(self.app(provider)) as client:
            with client.websocket_connect('/api/voice',headers=ORIGIN) as ws:
                ws.send_json({'type':'start','browser_id':self.browser,'fictional':True})
                self.assertTrue(entered.wait(1))
                ws.send_json({'type':'stop'})
                self.assertEqual(ws.receive()['type'],'websocket.close')
            self.assertTrue(provider.wire.closed)
            self.assertEqual(provider.calls,1)

    def test_disconnect_during_setup_closes_wire_and_allows_fresh_session(self):
        class WaitingWire(MockWire):
            async def send(self,value):
                if 'setup' in value:
                    await asyncio.Event().wait()
        class DisconnectingSocket:
            headers=ORIGIN
            def __init__(self):
                self.incoming=asyncio.Queue()
                self.sent=[]
            async def accept(self): pass
            async def receive(self): return await self.incoming.get()
            async def send_json(self,value): self.sent.append(value)
            async def send_bytes(self,value): self.sent.append(value)
            async def close(self,code=1000): self.sent.append({'type':'websocket.close','code':code})
        provider=Provider(WaitingWire())
        app=self.app(provider)
        app.state.store.initialize()
        endpoint=next(route.endpoint for route in app.routes if getattr(route,'path',None)=='/api/voice')
        async def disconnect_during_setup():
            socket=DisconnectingSocket()
            await socket.incoming.put({'type':'websocket.receive','text':json.dumps({
                'type':'start','browser_id':self.browser,'fictional':True})})
            await socket.incoming.put({'type':'websocket.disconnect','code':1000})
            await endpoint(socket)
            self.assertEqual(socket.sent[-1]['type'],'websocket.close')
        asyncio.run(disconnect_during_setup())
        self.assertTrue(provider.wire.closed)
        self.assertEqual(provider.calls,1)
        provider.wire=MockWire()
        with TestClient(app) as client:
            with client.websocket_connect('/api/voice',headers=ORIGIN) as ws:
                self.assertEqual(self.start(ws)['daily_used'],2)
                ws.send_json({'type':'stop'});ws.receive()
            self.assertTrue(provider.wire.closed)

    def test_backend_maximum_independent_of_client_closes_upstream(self):
        provider=Provider()
        with TestClient(self.app(provider,session=.06)) as client:
            with client.websocket_connect('/api/voice',headers=ORIGIN) as ws:
                self.start(ws)
                self.assertEqual(ws.receive_json()['type'],'error')
                self.assertEqual(ws.receive()['type'],'websocket.close')
            self.assertTrue(provider.wire.closed)

    def test_end_cancels_pending_provider_connect_without_late_ready(self):
        entered=threading.Event()
        canceled=threading.Event()
        class PendingProvider:
            async def connect(self):
                entered.set()
                try:
                    await asyncio.Event().wait()
                finally:
                    canceled.set()
        with TestClient(self.app(PendingProvider())) as client:
            with client.websocket_connect('/api/voice',headers=ORIGIN) as ws:
                ws.send_json({'type':'start','browser_id':self.browser,'fictional':True})
                self.assertTrue(entered.wait(1))
                ws.send_json({'type':'stop'})
                self.assertEqual(ws.receive()['type'],'websocket.close')
            self.assertTrue(canceled.is_set())

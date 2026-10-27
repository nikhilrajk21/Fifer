import asyncio
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import replace
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from uuid import uuid4

import httpx
from chat import ModelRequest, FALLBACK, MockTextProvider
from chat_content import retrieve
from gemini_text import GeminiTextProvider, ProviderUnavailable, load_backend_key, ENDPOINT
from main import create_app, runtime_chat_provider


class GeminiAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = TemporaryDirectory()
        self.calls = []
        self.entered = asyncio.Event()
        self.release = None
        self.delay = False
        self.response_status = 200
        self.response_body = None
        self.transport = httpx.MockTransport(self.handle)
        self.provider = GeminiTextProvider(key_source=lambda:'offline-fixture-only', transport=self.transport)
        self.app = create_app(Path(self.temp.name)/'adapter.sqlite3',chat_provider=self.provider)
        self.life = self.app.router.lifespan_context(self.app)
        await self.life.__aenter__()
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='http://fifer.test')
        self.identity = {'browser_id':str(uuid4()),'history_epoch':0}
        self.session_id=(await self.client.post('/api/chat/sessions',json=self.identity)).json()['id']

    async def asyncTearDown(self):
        await self.client.aclose()
        await self.life.__aexit__(None,None,None)
        self.temp.cleanup()

    def good_response(self, request):
        payload=json.loads(request.content)
        document=json.loads(payload['contents'][0]['parts'][0]['text'])['approved_content'][0]
        selected={'answer':document['text'],'source_id':document['id']}
        return {'candidates':[{'finishReason':'STOP','content':{'role':'model','parts':[{'text':json.dumps(selected)}]}}],
                'usageMetadata':{'candidatesTokenCount':80}}

    async def handle(self, request):
        # HTTPX MockTransport intercepts the request before any socket/DNS use.
        self.calls.append(request)
        self.entered.set()
        if self.release is not None:
            await self.release.wait()
        if self.delay:
            await asyncio.Event().wait()
        body=self.good_response(request) if self.response_body is None else self.response_body
        return httpx.Response(self.response_status,json=body)

    async def send(self):
        return await self.client.post(f'/api/chat/sessions/{self.session_id}/messages',json={
            **self.identity,'request_id':str(uuid4()),'question':'How do I pause Fifer?', 'fictional':True})

    async def test_success_through_fastapi_uses_header_only_key_and_bounded_packet(self):
        output=StringIO()
        with redirect_stdout(output),redirect_stderr(output):
            health=(await self.client.get('/api/health')).json()
            config=(await self.client.get('/api/chat/config',params={'browser_id':self.identity['browser_id']})).json()
            result=(await self.send()).json()
        self.assertTrue(health['model_enabled'])
        self.assertEqual(config['mode'],'gemini')
        self.assertTrue(config['live_calls_enabled'])
        self.assertEqual(result['mode'],'gemini')
        self.assertFalse(result['fallback'])
        self.assertIn('Pause keeps your place',result['answer'])
        self.assertFalse(result['saved'])
        self.assertEqual(len(self.calls),1)
        request=self.calls[0]
        self.assertEqual(str(request.url),ENDPOINT)
        self.assertNotIn('key=',str(request.url))
        self.assertIn('x-goog-api-key',request.headers)
        self.assertEqual(request.headers['x-goog-api-key'],'offline-fixture-only')
        payload=json.loads(request.content)
        self.assertEqual(payload['generationConfig']['maxOutputTokens'],300)
        self.assertEqual(payload['generationConfig']['candidateCount'],1)
        self.assertEqual(payload['generationConfig']['responseMimeType'],'application/json')
        self.assertNotIn('tools',payload)
        data=json.loads(payload['contents'][0]['parts'][0]['text'])
        self.assertEqual(set(data),{'fictional_app_question','approved_content','explicitly_shared_context'})
        self.assertEqual(data['explicitly_shared_context'],{})
        self.assertEqual(set(data['approved_content'][0]),{'id','title','text'})
        self.assertTrue(all(value==15 for value in request.extensions['timeout'].values()))
        self.assertNotIn('offline-fixture-only',output.getvalue())
        self.assertNotIn('offline-fixture-only',json.dumps(result))

    async def test_missing_key_produces_fixed_fallback_without_a_transport_request(self):
        self.provider._key_source=lambda:''
        result=(await self.send()).json()
        self.assertTrue(result['fallback'])
        self.assertEqual(result['answer'],FALLBACK)
        self.assertEqual(self.calls,[])

    async def test_provider_error_and_rate_limit_are_sanitized_and_never_retried(self):
        for status in (403,429,500):
            self.response_status=status
            self.response_body={'error':{'message':'offline-fixture-only must never be shown'}}
            before=len(self.calls)
            result=(await self.send()).json()
            self.assertEqual(result['answer'],FALLBACK)
            self.assertTrue(result['fallback'])
            self.assertEqual(len(self.calls),before+1)
            self.assertNotIn('offline-fixture-only',json.dumps(result))

    async def test_invalid_json_source_tools_and_truncated_outputs_are_rejected(self):
        document=retrieve('How to pause?')[0]
        def response(text, reason='STOP', parts=None):
            return {'candidates':[{'finishReason':reason,'content':{'role':'model','parts':parts or [{'text':text}]}}]}
        invalid=[response('not JSON'),
                 response(json.dumps({'answer':'Invented treatment advice','source_id':document['id']})),
                 response(json.dumps({'answer':document['text'],'source_id':'invented-source'})),
                 response('{}',parts=[{'functionCall':{'name':'change_step'}}]),
                 response(json.dumps({'answer':document['text'],'source_id':document['id']}),'MAX_TOKENS')]
        for body in invalid:
            with self.subTest(body=body):
                self.response_body=body
                self.assertTrue((await self.send()).json()['fallback'])
        self.assertEqual(len(self.calls),5)

    async def test_reported_token_overrun_or_oversize_body_is_rejected(self):
        request=ModelRequest('How to pause?',retrieve('How to pause?'),{})
        async def overrun(outgoing):
            body=self.good_response(outgoing)
            body['usageMetadata']['candidatesTokenCount']=301
            return httpx.Response(200,json=body)
        for handler in (overrun,lambda _request:httpx.Response(200,content=b'x'*65537)):
            provider=GeminiTextProvider(key_source=lambda:'offline-fixture-only',transport=httpx.MockTransport(handler))
            with self.assertRaises(ProviderUnavailable):
                await provider.reply(request)

    async def test_timeout_is_finite_and_has_no_retry(self):
        self.delay=True
        with patch('gemini_text.TIMEOUT_SECONDS',0.01):
            result=(await self.send()).json()
        self.assertTrue(result['fallback'])
        self.assertEqual(len(self.calls),1)

    async def test_late_transport_result_after_stop_does_not_return_or_save_answer(self):
        await self.client.patch('/api/settings',json={'history_epoch':0,'message_opt_in':True})
        self.release=asyncio.Event()
        pending=asyncio.create_task(self.send())
        await self.entered.wait()
        await self.client.post(f'/api/chat/sessions/{self.session_id}/stop',json=self.identity)
        self.release.set()
        result=await pending
        self.assertEqual(result.status_code,409)
        self.assertNotIn('answer',result.json())
        review=(await self.client.get(f'/api/chat/sessions/{self.session_id}')).json()
        self.assertEqual(review['messages'],[])

    async def test_valid_reply_saving_requires_existing_optin(self):
        self.assertFalse((await self.send()).json()['saved'])
        await self.client.patch('/api/settings',json={'history_epoch':0,'message_opt_in':True})
        self.assertTrue((await self.send()).json()['saved'])
        await self.client.patch('/api/settings',json={'history_epoch':0,'message_opt_in':False})
        self.assertFalse((await self.send()).json()['saved'])
        review=(await self.client.get(f'/api/chat/sessions/{self.session_id}')).json()
        self.assertEqual(len(review['messages']),2)
        self.assertNotIn('offline-fixture-only',json.dumps(review))

    async def test_unapproved_context_or_model_is_rejected_before_http(self):
        good=ModelRequest('How to pause?',retrieve('How to pause?'),{})
        for request in (replace(good,model='unapproved-model'),replace(good,max_output_tokens=301),
                        replace(good,context={'sensory_narrative':'not permitted'}),
                        replace(good,documents=[{'id':'private-file','text':'not permitted'}])):
            with self.assertRaises(ProviderUnavailable):
                await self.provider.reply(request)
        self.assertEqual(self.calls,[])

    async def test_no_authorization_means_no_key_read_or_network_and_default_app_stays_mock(self):
        def forbidden():
            raise AssertionError('Key loader must not run before authorization')
        provider=GeminiTextProvider(key_source=forbidden)
        with self.assertRaisesRegex(ProviderUnavailable,'separate authorization'):
            await provider.reply(ModelRequest('How to pause?',retrieve('How to pause?'),{}))
        default=create_app(Path(self.temp.name)/'default.sqlite3')
        self.assertIsInstance(default.state.chat_provider,MockTextProvider)

    async def test_runtime_selection_requires_both_explicit_server_gates(self):
        self.assertIsNone(runtime_chat_provider({}))
        self.assertIsNone(runtime_chat_provider({'FIFER_TEXT_PROVIDER':'mock'}))
        for values in ({'FIFER_TEXT_PROVIDER':'gemini'},
                       {'FIFER_TEXT_PROVIDER':'mock','FIFER_TEXT_LIVE_AUTHORIZED':'true'},
                       {'FIFER_TEXT_PROVIDER':'other','FIFER_TEXT_LIVE_AUTHORIZED':'true'}):
            with self.subTest(values=values), self.assertRaisesRegex(RuntimeError,'not authorized'):
                runtime_chat_provider(values)
        with patch('gemini_text.load_backend_key',side_effect=AssertionError('selection must stay lazy')):
            provider=runtime_chat_provider({'FIFER_TEXT_PROVIDER':'gemini','FIFER_TEXT_LIVE_AUTHORIZED':'true'})
        self.assertIsInstance(provider,GeminiTextProvider)
        self.assertTrue(provider.live_calls_enabled)

    async def test_loader_uses_only_temporary_fixture_and_existing_key_name(self):
        fixture=Path(self.temp.name)/'.env'
        fixture.write_text('# fictional fixture only\nGEMINI_API_KEY=fixture-only\n',encoding='utf8')
        self.assertEqual(load_backend_key(env={},path=fixture),'fixture-only')
        self.assertEqual(load_backend_key(env={'GEMINI_API_KEY':'env-fixture-only'},path=fixture),'env-fixture-only')
        for env in ({'GEMINI_API_KEY':''},{'GEMINI_API_KEY':'invalid\nvalue'}):
            with self.assertRaises(ProviderUnavailable):
                load_backend_key(env=env,path=fixture)
        fixture.write_text('GEMINI_API_KEY=\n',encoding='utf8')
        with self.assertRaises(ProviderUnavailable):
            load_backend_key(env={},path=fixture)

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
from gemini_text import (GeminiTextProvider, ProviderUnavailable, load_backend_key,
                         ENDPOINT, _record_failure, _record_response_diagnostics, request_payload,
                         status_reason, validated_answer)
from main import create_app, runtime_chat_provider


class GeminiDiagnosticTests(unittest.TestCase):
    def test_configured_model_and_generate_content_endpoint(self):
        from gemini_text import MODEL
        self.assertEqual(MODEL, "gemini-3.5-flash-lite")
        self.assertEqual(ENDPOINT,
                         "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent")

    def test_http_status_categories_are_fixed_and_404_is_generic(self):
        expected={401:'upstream_authentication',403:'upstream_permission',429:'upstream_quota',
                  400:'upstream_bad_request',404:'upstream_not_found',408:'upstream_timeout',
                  500:'upstream_server_error',418:'upstream_http_error'}
        for status,category in expected.items():
            with self.subTest(status=status):
                self.assertEqual(status_reason(status),category)

    def test_diagnostic_log_contains_only_model_numeric_status_and_category(self):
        with self.assertLogs('gemini_text',level='WARNING') as diagnostics:
            _record_failure('upstream_not_found',404)
        self.assertEqual(diagnostics.output,
                         ['WARNING:gemini_text:gemini_text_failure model_id=gemini-3.5-flash-lite http_status=404 category=upstream_not_found'])

    def test_diagnostic_fields_reject_unbounded_or_untrusted_values(self):
        with patch('gemini_text.MODEL','x'*65+'\nprivate-model-suffix'), \
                self.assertLogs('gemini_text',level='WARNING') as diagnostics:
            _record_failure('private-category-marker', '404 private-status-marker')
        self.assertEqual(diagnostics.output,
                         ['WARNING:gemini_text:gemini_text_failure model_id=unknown http_status=none category=provider_unavailable'])


class GeminiResponseContractTests(unittest.TestCase):
    def response(self, answer, source_id, *, extra=None):
        value={"answer":answer,"source_id":source_id}
        if extra:
            value.update(extra)
        return {"candidates":[{"finishReason":"STOP","content":{"role":"model","parts":[
            {"text":json.dumps(value)}]}}]}

    def test_valid_concise_paraphrase_requires_matching_single_source_id(self):
        document=retrieve('How do I pause Fifer?')[0]
        answer="Pause keeps your place; choose Resume when you are ready. Stop/Leave exits immediately."
        self.assertEqual(validated_answer(self.response(answer,document['id']),[document]),answer)
        with self.assertRaises(ProviderUnavailable) as caught:
            validated_answer(self.response(answer,'different-source'),[document])
        self.assertEqual(caught.exception.reason_code,'invalid_output')

    def test_text_part_with_or_without_thought_signature_is_accepted_without_exposing_it(self):
        document=retrieve('How do I pause Fifer?')[0]
        answer='Pause keeps your place; choose Resume when you are ready.'
        text=json.dumps({'answer':answer,'source_id':document['id']})
        for part in ({'text':text},
                     {'text':text,'thoughtSignature':'private-signature-marker'}):
            with self.subTest(signature='thoughtSignature' in part):
                body={'candidates':[{'finishReason':'STOP','content':{'role':'model','parts':[part]}}]}
                result=validated_answer(body,[document])
                self.assertEqual(result,answer)
                self.assertNotIn('private-signature-marker',result)

    def test_thought_signature_value_is_not_written_to_safe_diagnostics(self):
        document=retrieve('How do I pause Fifer?')[0]
        signature='private-signature-marker'
        answer='Pause keeps your place; choose Resume when you are ready.'
        body={'candidates':[{'finishReason':'STOP','content':{'role':'model','parts':[
            {'text':json.dumps({'answer':answer,'source_id':document['id']}),
             'thoughtSignature':signature}]}}]}
        diagnostics={}
        with self.assertLogs('gemini_text',level='WARNING') as captured:
            result=validated_answer(body,[document],diagnostics)
            _record_response_diagnostics(diagnostics,'accepted')
        self.assertEqual(result,answer)
        self.assertIn('content_part_types=text+thoughtSignature',captured.output[0])
        self.assertNotIn(signature,captured.output[0])

    def test_text_part_rejects_invalid_text_signature_unknown_keys_and_extra_parts(self):
        document=retrieve('How do I pause Fifer?')[0]
        text=json.dumps({'answer':'A concise answer.','source_id':document['id']})
        invalid_parts=(
            {'thoughtSignature':'signature-without-text'},
            {'text':None},
            {'text':17},
            {'text':text,'thoughtSignature':17},
            {'text':text,'thoughtSignature':None},
            {'text':text,'unknownField':'private-extra-marker'},
            {'text':text,'thoughtSignature':'private-signature-marker','unknownField':True},
        )
        invalid_bodies=[{'candidates':[{'finishReason':'STOP','content':{
            'role':'model','parts':[part]}}]} for part in invalid_parts]
        invalid_bodies.append({'candidates':[{'finishReason':'STOP','content':{
            'role':'model','parts':[{'text':text},{'text':text}]}}]})
        for body in invalid_bodies:
            with self.subTest(parts=body['candidates'][0]['content']['parts']), \
                    self.assertRaises(ProviderUnavailable) as caught:
                validated_answer(body,[document])
            self.assertEqual(caught.exception.reason_code,'invalid_output')

    def test_validator_rejects_malformed_empty_oversized_and_extra_output(self):
        document=retrieve('How do I pause Fifer?')[0]
        invalid=(None, {}, self.response('',document['id']),
                 self.response('x'*301,document['id']),
                 self.response('A short answer.',document['id'],extra={'tool_call':'pause'}),
                 {"candidates":[{"finishReason":"STOP","content":{"role":"model","parts":[
                     {"text":"not-json"}]}}]})
        for body in invalid:
            with self.subTest(body=body), self.assertRaises(ProviderUnavailable) as caught:
                validated_answer(body,[document])
            self.assertEqual(caught.exception.reason_code,'invalid_output')

    def test_out_of_scope_question_has_no_source_and_never_enters_provider_path(self):
        self.assertEqual(retrieve('What is the current weather in Paris?'),[])

    def test_shape_and_source_validator_cannot_prove_semantic_entailment(self):
        # This deliberately unsupported mock sentence demonstrates a limitation:
        # the validator proves output shape/source ID, not that a paraphrase is true.
        document=retrieve('How do I pause Fifer?')[0]
        unsupported='Fifer also has a hidden aquarium.'
        self.assertEqual(validated_answer(self.response(unsupported,document['id']),[document]),unsupported)

    def test_request_contains_only_one_curated_source_and_optional_approved_context(self):
        document=retrieve('How do I pause Fifer?')[0]
        request=ModelRequest('How do I pause Fifer?',[document],{})
        payload=request_payload(request)
        sent=json.loads(payload['contents'][0]['parts'][0]['text'])
        self.assertEqual(sent['approved_content'],[{key:document[key] for key in ('id','title','text')}])
        self.assertEqual(sent['explicitly_shared_context'],{})
        self.assertEqual(payload['generationConfig']['responseJsonSchema']['properties']['answer'],
                         {'type':'string'})
        self.assertEqual(payload['generationConfig']['responseJsonSchema']['properties']['source_id']['enum'],
                         [document['id']])
        self.assertIn('cannot determine the history because it was not shared',request.instructions)
        self.assertIn('do not replace that answer with a generic skill description',request.instructions)
        self.assertIn('actual completed-session count, recent completed skill, and optional',request.instructions)
        self.assertIn('paraphrase',payload['systemInstruction']['parts'][0]['text'])
        instruction=payload['systemInstruction']['parts'][0]['text']
        self.assertIn('cannot determine the history because context sharing is off',instruction)
        self.assertIn('do not substitute a generic skill description',instruction)
        self.assertIn('completed-session count, recent completed skill, and',instruction)
        approved={'completed_sessions':2,'recent_completed_skill':'5-4-3-2-1',
                  'latest_completed_checkin':'A little better'}
        shared=json.loads(request_payload(replace(request,context=approved))['contents'][0]['parts'][0]['text'])
        self.assertEqual(shared['explicitly_shared_context'],approved)
        for invalid_context in ({'profile':'fictional'}, {'sensory_answers':['blue']},
                                {'completed_sessions':2}):
            with self.subTest(context=invalid_context), self.assertRaises(ProviderUnavailable):
                request_payload(replace(request,context=invalid_context))


class GeminiAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = TemporaryDirectory()
        self.calls = []
        self.entered = asyncio.Event()
        self.release = None
        self.delay = False
        self.transport_error = None
        self.response_status = 200
        self.response_body = None
        self.response_raw = None
        self.transport = httpx.MockTransport(self.handle)
        self.provider = GeminiTextProvider(key_source=lambda:'offline-fixture-only', transport=self.transport)
        self.answer_override = None
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

    def good_response(self, request, answer=None, source_id=None):
        payload=json.loads(request.content)
        document=json.loads(payload['contents'][0]['parts'][0]['text'])['approved_content'][0]
        selected={'answer':answer if answer is not None else document['text'],
                  'source_id':source_id if source_id is not None else document['id']}
        return {'candidates':[{'finishReason':'STOP','content':{'role':'model','parts':[{'text':json.dumps(selected)}]}}],
                'usageMetadata':{'candidatesTokenCount':80}}

    async def handle(self, request):
        # HTTPX MockTransport intercepts the request before any socket/DNS use.
        self.calls.append(request)
        self.entered.set()
        if self.transport_error is not None:
            raise self.transport_error
        if self.release is not None:
            await self.release.wait()
        if self.delay:
            await asyncio.Event().wait()
        if self.response_raw is not None:
            return httpx.Response(self.response_status, content=self.response_raw,
                                  headers={'content-type':'application/json'})
        body=self.good_response(request,answer=self.answer_override) if self.response_body is None else self.response_body
        return httpx.Response(self.response_status,json=body)

    async def send(self, *, share_context=False, question='How do I pause Fifer?'):
        return await self.client.post(f'/api/chat/sessions/{self.session_id}/messages',json={
            **self.identity,'request_id':str(uuid4()),'question':question,'fictional':True,
            'share_context':share_context})

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
        self.assertIsNone(result['reason_code'])
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
        schema=payload['generationConfig']['responseJsonSchema']
        self.assertEqual(schema['type'],'object')
        self.assertEqual(schema['properties']['answer']['type'],'string')
        self.assertNotIn('enum',schema['properties']['answer'])
        self.assertFalse(schema['additionalProperties'])
        self.assertNotIn('responseSchema',payload['generationConfig'])
        self.assertNotIn('tools',payload)
        data=json.loads(payload['contents'][0]['parts'][0]['text'])
        self.assertEqual(set(data),{'fictional_app_question','approved_content','explicitly_shared_context'})
        self.assertEqual(data['explicitly_shared_context'],{})
        self.assertEqual(set(data['approved_content'][0]),{'id','title','text'})
        self.assertTrue(all(value==15 for value in request.extensions['timeout'].values()))
        self.assertNotIn('offline-fixture-only',output.getvalue())
        self.assertNotIn('offline-fixture-only',json.dumps(result))

    async def test_concise_paraphrase_is_returned_with_the_single_retrieved_source(self):
        paraphrase='Pause keeps your place; choose Resume when you are ready. Stop/Leave exits immediately.'
        self.answer_override=paraphrase
        result=(await self.send()).json()
        self.assertEqual(result['answer'],paraphrase)
        self.assertFalse(result['fallback'])
        self.assertEqual([source['id'] for source in result['sources']],['controls'])
        payload=json.loads(self.calls[0].content)
        prompt=payload['systemInstruction']['parts'][0]['text']
        self.assertIn('plain-language paraphrase',prompt)
        self.assertIn('single supplied approved paragraph',prompt)
        self.assertIn('directly relevant',prompt)

    async def test_context_off_and_explicitly_shared_summary_are_the_only_context_sent(self):
        first=(await self.send(share_context=False)).json()
        self.assertEqual(first['context_shared'],{})
        first_payload=json.loads(self.calls[-1].content)
        first_data=json.loads(first_payload['contents'][0]['parts'][0]['text'])
        self.assertEqual(first_data['explicitly_shared_context'],{})
        with self.app.state.store.connection(write=True) as db:
            values=('fictional-session','5-4-3-2-1','2026-10-26T12:00:00Z',
                    '2026-10-26T12:01:00Z','2026-10-26T12:01:00Z','completed',
                    'complete','A little better',0,1000,0,0,8)
            db.execute('INSERT INTO sessions VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',values)
        second=(await self.send(share_context=True)).json()
        expected={'completed_sessions':1,'recent_completed_skill':'5-4-3-2-1',
                  'latest_completed_checkin':'A little better'}
        self.assertEqual(second['context_shared'],expected)
        second_data=json.loads(json.loads(self.calls[-1].content)['contents'][0]['parts'][0]['text'])
        self.assertEqual(second_data['explicitly_shared_context'],expected)
        self.assertNotIn('fictional-session',str(second_data))
        self.assertNotIn('sensory',str(second_data).casefold())
        third=(await self.send(share_context=False)).json()
        self.assertEqual(third['context_shared'],{})
        third_data=json.loads(json.loads(self.calls[-1].content)['contents'][0]['parts'][0]['text'])
        self.assertEqual(third_data['explicitly_shared_context'],{})

    async def test_missing_key_produces_fixed_fallback_without_a_transport_request(self):
        self.provider._key_source=lambda:''
        result=(await self.send()).json()
        self.assertTrue(result['fallback'])
        self.assertEqual(result['answer'],FALLBACK)
        self.assertEqual(result['reason_code'],'configuration_missing')
        self.assertEqual(self.calls,[])

    async def test_upstream_status_categories_are_sanitized_and_never_retried(self):
        categories={401:'upstream_authentication',403:'upstream_permission',429:'upstream_quota',
                    400:'upstream_bad_request',404:'upstream_not_found',
                    500:'upstream_server_error',418:'upstream_http_error'}
        for status,category in categories.items():
            self.session_id=(await self.client.post('/api/chat/sessions',json=self.identity)).json()['id']
            self.response_status=status
            self.response_body={'error':{'message':'mock-private-provider-detail must never be shown'}}
            before=len(self.calls)
            with self.assertLogs('gemini_text',level='WARNING') as diagnostics:
                result=(await self.send()).json()
            self.assertEqual(result['answer'],FALLBACK)
            self.assertTrue(result['fallback'])
            self.assertEqual(result['reason_code'],category)
            self.assertEqual(len(self.calls),before+1)
            self.assertNotIn('mock-private-provider-detail',json.dumps(result))
            self.assertEqual(len(diagnostics.records),1)
            log=diagnostics.output[0]
            self.assertIn('model_id=gemini-3.5-flash-lite',log)
            self.assertIn(f'http_status={status}',log)
            self.assertIn(f'category={category}',log)
            self.assertNotIn('mock-private-provider-detail',log)

    async def test_connection_and_timeout_errors_have_fixed_codes_without_retries(self):
        for error,category in ((httpx.ConnectError('mock-secret-detail'),'connection_error'),
                               (httpx.ReadTimeout('mock-secret-detail'),'timeout')):
            self.session_id=(await self.client.post('/api/chat/sessions',json=self.identity)).json()['id']
            self.transport_error=error
            before=len(self.calls)
            with self.assertLogs('gemini_text',level='WARNING') as diagnostics:
                result=(await self.send()).json()
            self.assertTrue(result['fallback'])
            self.assertEqual(result['reason_code'],category)
            self.assertEqual(len(self.calls),before+1)
            self.assertNotIn('mock-secret-detail',json.dumps(result))
            self.assertEqual(len(diagnostics.records),1)
            self.assertIn('model_id=gemini-3.5-flash-lite',diagnostics.output[0])
            self.assertIn('http_status=none',diagnostics.output[0])
            self.assertIn(f'category={category}',diagnostics.output[0])
            self.assertNotIn('mock-secret-detail',diagnostics.output[0])
            self.transport_error=None

    async def test_diagnostic_log_contains_only_bounded_allowlisted_metadata(self):
        secret_markers=('private-key-marker','private-question-marker','private-provider-body-marker')
        self.provider._key_source=lambda:secret_markers[0]
        self.response_status=404
        self.response_body={'error':{'message':secret_markers[2]}}
        request=ModelRequest(secret_markers[1],retrieve('How to pause?'),{})
        with self.assertLogs('gemini_text',level='WARNING') as diagnostics:
            with self.assertRaises(ProviderUnavailable):
                await self.provider.reply(request)
        self.assertEqual(len(diagnostics.records),1)
        log=diagnostics.output[0]
        self.assertIn('model_id=gemini-3.5-flash-lite',log)
        self.assertIn('http_status=404',log)
        self.assertIn('category=upstream_not_found',log)
        for marker in secret_markers:
            self.assertNotIn(marker,log)

    async def test_response_diagnostics_capture_safe_structure_for_valid_output(self):
        document=retrieve('How do I pause Fifer?')[0]
        request=ModelRequest('How do I pause Fifer?', [document], {})
        with self.assertLogs('gemini_text',level='WARNING') as diagnostics:
            answer=await self.provider.reply(request)
        self.assertEqual(answer,document['text'])
        self.assertEqual(len(diagnostics.output),1)
        log=diagnostics.output[0]
        self.assertRegex(log,r'http_status=200 elapsed_ms=\d+')
        self.assertIn('candidate_count=1',log)
        self.assertIn('finish_reason=STOP',log)
        self.assertIn('content_part_count=1 content_part_types=text',log)
        self.assertIn(f'text_length={len(json.dumps({"answer":document["text"],"source_id":document["id"]}))}',log)
        self.assertIn('outer_json=ok answer_json=ok required_fields=pass',log)
        self.assertIn('required_answer=present required_source_id=present',log)
        self.assertIn(f'answer_length={len(document["text"])} answer_length_ok=true',log)
        self.assertIn('source_id_match=true failure_stage=none category=accepted',log)
        self.assertNotIn(document['text'],log)
        self.assertNotIn(document['id'],log)
        self.assertNotIn('How do I pause Fifer?',log)
        self.assertNotIn('offline-fixture-only',log)

    async def test_response_diagnostics_classify_parse_shape_and_source_stages(self):
        document=retrieve('How do I pause Fifer?')[0]
        valid_answer='A brief fictional diagnostic answer.'
        selected={'answer':valid_answer,'source_id':document['id']}
        base={'candidates':[{'finishReason':'STOP','content':{'role':'model','parts':[
            {'text':json.dumps(selected)}]}}]}
        cases=[
            ('outer_json',None,b'private-raw-provider-body-marker',
             ('outer_json=invalid','failure_stage=outer_json')),
            ('candidate_count',{'candidates':[]},None,
             ('candidate_count=0','failure_stage=candidate_count')),
            ('finish_reason',{'candidates':[{'finishReason':'private-finish-marker',
             'content':{'role':'model','parts':[{'text':json.dumps(selected)}]}}]},None,
             ('finish_reason=OTHER','failure_stage=finish_reason')),
            ('thought_signature',{'candidates':[{'finishReason':'STOP','content':{'role':'model','parts':[
             {'text':json.dumps(selected),'thoughtSignature':'private-thought-signature-marker'}]}}]},None,
             ('content_part_types=text+thoughtSignature','failure_stage=content_parts')),
            ('content_parts',{'candidates':[{'finishReason':'STOP','content':{'role':'model','parts':[
             {'functionCall':{'name':'private-tool-marker'}}]}}]},None,
             ('content_part_types=functionCall','failure_stage=content_parts')),
            ('answer_json',{'candidates':[{'finishReason':'STOP','content':{'role':'model','parts':[
             {'text':'private-answer-marker is not JSON'}]}}]},None,
             ('answer_json=invalid','failure_stage=answer_json')),
            ('required_fields',{'candidates':[{'finishReason':'STOP','content':{'role':'model','parts':[
             {'text':json.dumps({'source_id':document['id']})}]}}]},None,
             ('required_fields=missing','required_answer=missing required_source_id=present')),
            ('answer_length',{'candidates':[{'finishReason':'STOP','content':{'role':'model','parts':[
             {'text':json.dumps({'answer':'x'*301,'source_id':document['id']})}]}}]},None,
             ('answer_length=301 answer_length_ok=false','failure_stage=answer_length')),
            ('source_id',{'candidates':[{'finishReason':'STOP','content':{'role':'model','parts':[
             {'text':json.dumps({'answer':valid_answer,'source_id':'private-source-marker'})}]}}]},None,
             ('source_id_match=false','failure_stage=source_id')),
        ]
        for stage, body, raw, expected in cases:
            with self.subTest(stage=stage):
                self.session_id=(await self.client.post('/api/chat/sessions',json=self.identity)).json()['id']
                self.response_body=body
                self.response_raw=raw
                with self.assertLogs('gemini_text',level='WARNING') as diagnostics:
                    result=(await self.send()).json()
                self.assertTrue(result['fallback'])
                self.assertEqual(result['reason_code'],'invalid_output')
                self.assertEqual(len(diagnostics.output),1)
                log=diagnostics.output[0]
                self.assertIn('http_status=200',log)
                self.assertIn('category=invalid_output',log)
                for field in expected:
                    self.assertIn(field,log)
                for marker in ('private-raw-provider-body-marker','private-finish-marker',
                               'private-thought-signature-marker','private-tool-marker',
                               'private-answer-marker','private-source-marker'):
                    self.assertNotIn(marker,log)
                self.response_body=None
                self.response_raw=None

    async def test_invalid_json_source_tools_and_truncated_outputs_are_rejected(self):
        document=retrieve('How to pause?')[0]
        def response(text, reason='STOP', parts=None):
            return {'candidates':[{'finishReason':reason,'content':{'role':'model','parts':parts or [{'text':text}]}}]}
        invalid=[response('not JSON'),
                 response(json.dumps({'answer':document['text'],'source_id':'invented-source'})),
                 response(json.dumps({'answer':'x'*301,'source_id':document['id']})),
                 response('{}',parts=[{'functionCall':{'name':'change_step'}}]),
                 response(json.dumps({'answer':document['text'],'source_id':document['id']}),'MAX_TOKENS')]
        for body in invalid:
            with self.subTest(body=body):
                self.response_body=body
                with self.assertLogs('gemini_text',level='WARNING') as diagnostics:
                    result=(await self.send()).json()
                self.assertTrue(result['fallback'])
                self.assertEqual(result['reason_code'],'invalid_output')
                self.assertEqual(len(diagnostics.records),1)
                self.assertIn('http_status=200',diagnostics.output[0])
                self.assertIn('category=invalid_output',diagnostics.output[0])
        self.assertEqual(len(self.calls),5)

    async def test_reported_token_overrun_or_oversize_body_is_rejected(self):
        request=ModelRequest('How to pause?',retrieve('How to pause?'),{})
        async def overrun(outgoing):
            body=self.good_response(outgoing)
            body['usageMetadata']['candidatesTokenCount']=301
            return httpx.Response(200,json=body)
        for handler in (overrun,lambda _request:httpx.Response(200,content=b'x'*65537)):
            provider=GeminiTextProvider(key_source=lambda:'offline-fixture-only',transport=httpx.MockTransport(handler))
            with self.assertRaises(ProviderUnavailable) as caught:
                await provider.reply(request)
            self.assertEqual(caught.exception.reason_code,'invalid_output')

    async def test_timeout_is_finite_and_has_no_retry(self):
        self.delay=True
        with patch('gemini_text.TIMEOUT_SECONDS',0.01), \
                self.assertLogs('gemini_text',level='WARNING') as diagnostics:
            result=(await self.send()).json()
        self.assertTrue(result['fallback'])
        self.assertEqual(result['reason_code'],'timeout')
        self.assertEqual(len(self.calls),1)
        self.assertIn('http_status=none',diagnostics.output[0])
        self.assertIn('category=timeout',diagnostics.output[0])

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

    async def test_thought_signature_never_reaches_answer_storage_or_logs(self):
        document=retrieve('How do I pause Fifer?')[0]
        answer='Pause keeps your place; choose Resume when you are ready.'
        signature='private-signature-marker'
        selected={'answer':answer,'source_id':document['id']}
        self.response_body={'candidates':[{'finishReason':'STOP','content':{
            'role':'model','parts':[{'text':json.dumps(selected),
                                     'thoughtSignature':signature}]}}],
            'usageMetadata':{'candidatesTokenCount':30}}
        await self.client.patch('/api/settings',json={'history_epoch':0,'message_opt_in':True})
        with self.assertLogs('gemini_text',level='WARNING') as diagnostics:
            result=(await self.send()).json()
        self.assertEqual(result['answer'],answer)
        self.assertTrue(result['saved'])
        history=(await self.client.get(f'/api/chat/sessions/{self.session_id}')).json()
        serialized=' '.join((json.dumps(result),json.dumps(history),' '.join(diagnostics.output)))
        self.assertNotIn(signature,serialized)
        self.assertIn('content_part_types=text+thoughtSignature',diagnostics.output[0])

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
        with self.assertRaisesRegex(ProviderUnavailable,'separate authorization') as caught:
            await provider.reply(ModelRequest('How to pause?',retrieve('How to pause?'),{}))
        self.assertEqual(caught.exception.reason_code,'live_not_authorized')
        default=create_app(Path(self.temp.name)/'default.sqlite3')
        self.assertIsInstance(default.state.chat_provider,MockTextProvider)

    async def test_runtime_selection_requires_both_explicit_server_gates(self):
        self.assertIsNone(runtime_chat_provider({}))
        self.assertIsNone(runtime_chat_provider({'FIFER_TEXT_PROVIDER':'mock'}))
        self.assertIsNone(runtime_chat_provider({'FIFER_TEXT_PROVIDER':'mock','FIFER_TEXT_LIVE_AUTHORIZED':'false'}))
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

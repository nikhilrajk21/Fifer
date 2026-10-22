import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4
from httpx import ASGITransport, AsyncClient
from main import create_app


class ApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = TemporaryDirectory()
        self.path = Path(self.temp.name) / 'test.sqlite3'
        self.app = create_app(self.path)
        self.life = self.app.router.lifespan_context(self.app)
        await self.life.__aenter__()
        self.client = AsyncClient(transport=ASGITransport(app=self.app), base_url="http://fifer.test")
        self.id = str(uuid4())
        self.value = {"history_epoch": 0, "skill": "5-4-3-2-1", "started_at": "2026-10-22T12:00:00Z",
                      "ended_at": None, "status": "active", "current_step": "see", "checkin": None,
                      "setup_ms": 1000, "active_ms": 0, "paused_ms": 0, "support_ms": 0,
                      "revision": 1, "event": "begin"}

    async def asyncTearDown(self):
        await self.client.aclose()
        await self.life.__aexit__(None, None, None)
        self.temp.cleanup()

    async def save(self, **changes):
        self.value.update(changes)
        response = await self.client.put(f"/api/sessions/{self.id}", json=self.value)
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    async def advance(self, step, **changes):
        return await self.save(current_step=step, event="progress", revision=self.value["revision"] + 1,
                               active_ms=self.value["active_ms"] + 1000, **changes)

    async def completed(self):
        await self.save()
        for step in ("feel", "checkin", "hear", "smell", "taste", "complete"):
            await self.advance(step)
        return await self.save(status="completed", event="finish", revision=8,
                               ended_at="2026-10-22T12:01:00Z")

    async def optin(self, enabled, epoch=0):
        response = await self.client.patch('/api/settings', json={"message_opt_in": enabled, "history_epoch": epoch})
        self.assertEqual(response.status_code, 200)
        return response.json()

    async def message(self, content="A fictional student notices a window."):
        return await self.client.post(f'/api/sessions/{self.id}/messages', json={
            "id": str(uuid4()), "role": "user", "content": content, "fictional": True, "history_epoch": 0})

    async def test_health_is_stateless_and_reports_disabled_integrations(self):
        response = await self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "ok",
            "coursework_prototype": True,
            "persistence_enabled": True,
            "model_enabled": False,
        })

    async def test_no_model_or_emergency_action_endpoints(self):
        for path in ("/api/model", "/api/emergency"):
            with self.subTest(path=path):
                self.assertEqual((await self.client.post(path)).status_code, 404)

    async def test_fixed_flow_only_explicit_finish_sets_recent(self):
        await self.save()
        for step in ("feel", "checkin", "hear", "smell", "taste", "complete"):
            await self.advance(step, checkin="A little better" if step in ("hear", "smell", "taste", "complete") else None)
        self.assertIsNone((await self.client.get('/api/history')).json()['recent_completed'])
        await self.save(status='completed', event='finish', revision=8, ended_at='2026-10-22T12:01:00Z')
        recent = (await self.client.get('/api/history')).json()['recent_completed']
        self.assertEqual(recent['id'], self.id)
        self.assertEqual(recent['checkin'], 'A little better')
        self.assertNotIn('selections', recent)
        self.assertEqual(recent['active_ms'], 6000)

    async def test_pause_resume_separate_durations_and_stopped_never_completed(self):
        await self.save()
        await self.save(status='paused', event='pause', revision=2, active_ms=500)
        await self.save(status='active', event='resume', revision=3, paused_ms=3000)
        await self.advance('feel')
        await self.save(status='paused', event='pause', revision=5, support_ms=4000)
        record = await self.save(status='stopped', event='stop', revision=6, ended_at='2026-10-22T12:01:00Z')
        self.assertEqual((record['active_ms'],record['paused_ms'],record['support_ms'],record['setup_ms']), (1500,3000,4000,1000))
        self.assertEqual(record['current_step'], 'feel')
        self.assertIsNone((await self.client.get('/api/history')).json()['recent_completed'])
        bad = {**self.value, 'status': 'completed', 'event': 'finish', 'current_step': 'complete', 'revision': 7}
        self.assertEqual((await self.client.put(f'/api/sessions/{self.id}',json=bad)).status_code,409)

    async def test_schema_repeat_and_new_app_preserve_resume_and_messages(self):
        await self.save()
        await self.advance('feel')
        await self.save(status='paused',event='pause',revision=3,paused_ms=1700)
        await self.optin(True)
        self.assertEqual((await self.message()).status_code, 200)
        self.app.state.store.initialize()
        restarted = create_app(self.path)
        async with restarted.router.lifespan_context(restarted):
            async with AsyncClient(transport=ASGITransport(app=restarted),base_url='http://fifer.test') as client:
                record = (await client.get(f'/api/sessions/{self.id}')).json()
                self.assertEqual(record['session']['current_step'],'feel')
                self.assertEqual(record['session']['paused_ms'],1700)
                self.assertEqual(len(record['messages']),1)
                self.assertTrue((await client.get('/api/history')).json()['settings']['message_opt_in'])

    async def test_messages_optin_default_off_and_turning_off_keeps_existing(self):
        await self.save()
        self.assertFalse((await self.client.get('/api/history')).json()['settings']['message_opt_in'])
        self.assertEqual((await self.message()).status_code,403)
        await self.optin(True)
        self.assertEqual((await self.message()).status_code,200)
        await self.optin(False)
        self.assertEqual((await self.message()).status_code,403)
        self.assertEqual(len((await self.client.get(f'/api/sessions/{self.id}')).json()['messages']),1)

    async def test_session_delete_cascades_and_removes_recent(self):
        await self.completed()
        await self.optin(True)
        await self.message()
        response = await self.client.delete(f'/api/sessions/{self.id}?history_epoch=0')
        self.assertEqual(response.status_code,200)
        history = (await self.client.get('/api/history')).json()
        self.assertEqual(history['sessions'],[])
        self.assertIsNone(history['recent_completed'])
        self.assertTrue(history['settings']['message_opt_in'])
        with self.app.state.store.connection() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM messages').fetchone()[0],0)
            self.assertEqual(db.execute('SELECT count(*) FROM conversations').fetchone()[0],0)

    async def test_clear_resets_optin_and_fences_late_writes(self):
        await self.completed()
        await self.optin(True)
        await self.message()
        cleared = await self.client.delete('/api/history?history_epoch=0')
        self.assertEqual(cleared.status_code,200)
        self.assertFalse(cleared.json()['message_opt_in'])
        self.assertEqual(cleared.json()['history_epoch'],1)
        self.assertEqual((await self.client.put(f'/api/sessions/{self.id}',json=self.value)).status_code,409)
        self.assertEqual((await self.message()).status_code,409)
        history = (await self.client.get('/api/history')).json()
        self.assertEqual(history['sessions'],[])
        self.assertIsNone(history['recent_completed'])
        with self.app.state.store.connection() as db:
            for table in ('sessions','conversations','messages'):
                self.assertEqual(db.execute(f'SELECT count(*) FROM {table}').fetchone()[0],0)

    async def test_idempotent_retries_and_conflicting_revision(self):
        original = await self.save()
        self.assertEqual((await self.client.put(f'/api/sessions/{self.id}',json=self.value)).json(), original)
        bad = {**self.value,'active_ms':99}
        self.assertEqual((await self.client.put(f'/api/sessions/{self.id}',json=bad)).status_code,409)
        self.assertEqual(len((await self.client.get('/api/history')).json()['sessions']),1)

    async def test_invalid_steps_completion_and_extra_private_fields_rejected(self):
        await self.save()
        for changes in ({'current_step':'taste','revision':2,'event':'progress'},
                        {'status':'completed','ended_at':'2026-10-22T12:01:00Z','revision':2},
                        {'selections':['A window']},{'personal_narrative':'not allowed'},
                        {'active_ms':-1}, {'started_at':'2026-10-22T12:00:00'}):
            with self.subTest(changes=changes):
                self.assertEqual((await self.client.put(f'/api/sessions/{self.id}',json={**self.value,**changes})).status_code,422)

    async def test_sql_injection_text_is_literal_fictional_message(self):
        await self.save()
        await self.optin(True)
        text = "Fictional example: '); DROP TABLE sessions; --"
        self.assertEqual((await self.message(text)).status_code,200)
        review = (await self.client.get(f'/api/sessions/{self.id}')).json()
        self.assertEqual(review['messages'][0]['content'],text)
        self.assertEqual(len((await self.client.get('/api/history')).json()['sessions']),1)

    async def test_database_failure_returns_unsaved_service_error(self):
        await self.save()
        self.app.state.store.path = Path(self.temp.name) / 'missing-directory' / 'unavailable.sqlite3'
        response = await self.client.put(f'/api/sessions/{self.id}',json=self.value)
        self.assertEqual(response.status_code,503)
        self.assertIn('No save was confirmed',response.json()['detail'])
        self.assertEqual((await self.client.delete('/api/history?history_epoch=0')).status_code,503)
        self.app.state.store.path = self.path
        self.assertEqual(len((await self.client.get('/api/history')).json()['sessions']),1)


if __name__ == "__main__":
    unittest.main()


"""Local fictional coursework history. No model or emergency-contact integration."""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3
from typing import Annotated, Literal
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from storage import Store, session, settings


STEPS = ("see", "feel", "checkin", "hear", "smell", "taste", "complete")
Count = Annotated[int, Field(strict=True, ge=0, le=9007199254740991)]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Epoch(Input):
    history_epoch: Count


class SessionWrite(Epoch):
    skill: Literal["5-4-3-2-1"]
    started_at: datetime
    ended_at: datetime | None = None
    status: Literal["active", "paused", "stopped", "completed"]
    current_step: Literal["see", "feel", "checkin", "hear", "smell", "taste", "complete"]
    checkin: Literal["A little better", "About the same", "A little harder", "Not sure"] | None = None
    setup_ms: Count
    active_ms: Count
    paused_ms: Count
    support_ms: Count
    revision: Annotated[int, Field(strict=True, ge=1)]
    event: Literal["begin", "progress", "pause", "resume", "checkpoint", "finish", "stop"]

    @field_validator("started_at", "ended_at")
    @classmethod
    def aware_time(cls, value):
        if value is not None:
            if value.tzinfo is None:
                raise ValueError("A timezone is required")
            return value.astimezone(timezone.utc)
        return value

    @model_validator(mode="after")
    def consistent(self):
        terminal = self.status in ("stopped", "completed")
        if terminal != (self.ended_at is not None):
            raise ValueError("Only stopped/completed sessions have an end time")
        if self.ended_at and self.ended_at < self.started_at:
            raise ValueError("End precedes start")
        if self.status == "completed" and (self.event != "finish" or self.current_step != "complete"):
            raise ValueError("Completion requires explicit Finish at the final screen")
        if self.status == "stopped" and self.event != "stop":
            raise ValueError("Stopped sessions require Stop")
        if self.checkin is not None and STEPS.index(self.current_step) < 2:
            raise ValueError("Check-in is only after Feel")
        return self


class Preferences(Epoch):
    message_opt_in: bool


class Message(Epoch):
    id: UUID
    role: Literal["user", "assistant"]
    content: Annotated[str, Field(min_length=1, max_length=1000)]
    fictional: Literal[True]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def require_epoch(db, expected):
    if settings(db)["history_epoch"] != expected:
        raise HTTPException(409, "History changed or was cleared. Reload before saving new activity.")


def create_app(db_path=None):
    path = Path(db_path or os.environ.get("FIFER_DB_PATH") or Path(__file__).parent / "data" / "fifer.sqlite3")
    store = Store(path)

    @asynccontextmanager
    async def lifespan(_):
        store.initialize()
        yield

    app = FastAPI(title="Fifer coursework prototype", docs_url=None, redoc_url=None,
                  openapi_url=None, lifespan=lifespan)
    app.state.store = store

    @app.exception_handler(sqlite3.Error)
    async def storage_error(_, __):
        return JSONResponse(status_code=503, content={"detail": "Local storage is unavailable. No save was confirmed."})

    @app.get("/api/health")
    async def health():
        return {"status": "ok", "coursework_prototype": True,
                "persistence_enabled": True, "model_enabled": False}

    @app.get("/api/history")
    def history():
        with store.connection() as db:
            rows = [dict(row) for row in db.execute("SELECT * FROM sessions ORDER BY started_at DESC, id DESC")]
            recent = db.execute("SELECT * FROM sessions WHERE status = 'completed' ORDER BY ended_at DESC, id DESC LIMIT 1").fetchone()
            return {"settings": settings(db), "sessions": rows,
                    "recent_completed": dict(recent) if recent else None}

    @app.put("/api/sessions/{session_id}")
    def save_session(session_id: UUID, value: SessionWrite):
        with store.connection(write=True) as db:
            require_epoch(db, value.history_epoch)
            old = session(db, session_id)
            if old and value.revision == old["revision"]:
                replay = {key: getattr(value, key) for key in
                          ("skill", "status", "current_step", "checkin", "setup_ms", "active_ms", "paused_ms", "support_ms")}
                replay["started_at"] = value.started_at.isoformat()
                replay["ended_at"] = value.ended_at.isoformat() if value.ended_at else None
                if all(old[key] == item for key, item in replay.items()):
                    return old  # Identical retry after a lost acknowledgement.
                raise HTTPException(409, "This session changed. Reload history before continuing.")
            if old is None:
                if value.event != "begin" or value.revision != 1 or value.status != "active" or value.current_step != "see":
                    raise HTTPException(409, "Begin a new session before updating it.")
            else:
                if old["status"] in ("completed", "stopped"):
                    raise HTTPException(409, "A finished or stopped session cannot be changed.")
                if value.revision != old["revision"] + 1:
                    raise HTTPException(409, "A newer session revision is required. Reload history.")
                if value.started_at.isoformat() != old["started_at"]:
                    raise HTTPException(422, "Session start time cannot change.")
                previous, current = STEPS.index(old["current_step"]), STEPS.index(value.current_step)
                if current not in (previous, previous + 1):
                    raise HTTPException(422, "Keep the fixed grounding sequence.")
                if current != previous and (value.event != "progress" or old["status"] != "active"):
                    raise HTTPException(422, "Resume before advancing one step.")
                if value.status == "completed" and old["current_step"] != "complete":
                    raise HTTPException(422, "Reach completion before Finish.")
                if any(getattr(value, name) < old[name] for name in ("setup_ms", "active_ms", "paused_ms", "support_ms")):
                    raise HTTPException(422, "Duration counters cannot decrease.")
            values = (str(session_id), value.skill, value.started_at.isoformat(),
                      value.ended_at.isoformat() if value.ended_at else None, utc_now(), value.status,
                      value.current_step, value.checkin, value.setup_ms, value.active_ms,
                      value.paused_ms, value.support_ms, value.revision)
            db.execute("""INSERT INTO sessions
                (id,skill,started_at,ended_at,updated_at,status,current_step,checkin,setup_ms,active_ms,paused_ms,support_ms,revision)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET ended_at=excluded.ended_at,updated_at=excluded.updated_at,
                status=excluded.status,current_step=excluded.current_step,checkin=excluded.checkin,
                setup_ms=excluded.setup_ms,active_ms=excluded.active_ms,paused_ms=excluded.paused_ms,
                support_ms=excluded.support_ms,revision=excluded.revision""", values)
            return session(db, session_id)

    @app.get("/api/sessions/{session_id}")
    def review_session(session_id: UUID):
        with store.connection() as db:
            record = session(db, session_id)
            if record is None:
                raise HTTPException(404, "Session not found")
            conversation = db.execute("SELECT * FROM conversations WHERE session_id = ?", (str(session_id),)).fetchone()
            messages = [dict(row) for row in db.execute("""SELECT messages.* FROM messages
                JOIN conversations ON conversations.id = messages.conversation_id
                WHERE conversations.session_id = ? ORDER BY messages.created_at, messages.id""", (str(session_id),))]
            return {"session": record, "conversation": dict(conversation) if conversation else None, "messages": messages}

    @app.patch("/api/settings")
    def preferences(value: Preferences):
        with store.connection(write=True) as db:
            require_epoch(db, value.history_epoch)
            db.execute("UPDATE settings SET message_opt_in = ? WHERE id = 1", (int(value.message_opt_in),))
            return settings(db)

    @app.post("/api/sessions/{session_id}/messages")
    def save_message(session_id: UUID, value: Message):
        with store.connection(write=True) as db:
            require_epoch(db, value.history_epoch)
            if not settings(db)["message_opt_in"]:
                raise HTTPException(403, "Message saving is OFF. Explicit opt-in is required.")
            if session(db, session_id) is None:
                raise HTTPException(404, "Session not found")
            conversation = db.execute("SELECT id FROM conversations WHERE session_id = ?", (str(session_id),)).fetchone()
            conversation_id = conversation["id"] if conversation else str(uuid4())
            if conversation is None:
                db.execute("INSERT INTO conversations(id, session_id, created_at) VALUES (?,?,?)",
                           (conversation_id, str(session_id), utc_now()))
            old = db.execute("SELECT * FROM messages WHERE id = ?", (str(value.id),)).fetchone()
            if old:
                if old["conversation_id"] != conversation_id or old["role"] != value.role or old["content"] != value.content:
                    raise HTTPException(409, "Message ID already used")
                return dict(old)
            db.execute("INSERT INTO messages(id, conversation_id, role, content, created_at) VALUES (?,?,?,?,?)",
                       (str(value.id), conversation_id, value.role, value.content, utc_now()))
            return dict(db.execute("SELECT * FROM messages WHERE id = ?", (str(value.id),)).fetchone())

    @app.delete("/api/sessions/{session_id}")
    def delete_session(session_id: UUID, history_epoch: int):
        with store.connection(write=True) as db:
            require_epoch(db, history_epoch)
            db.execute("DELETE FROM sessions WHERE id = ?", (str(session_id),))
            db.execute("UPDATE settings SET history_epoch = history_epoch + 1 WHERE id = 1")
            return settings(db)

    @app.delete("/api/history")
    def clear_history(history_epoch: int):
        with store.connection(write=True) as db:
            require_epoch(db, history_epoch)
            db.execute("DELETE FROM sessions")  # Foreign keys cascade conversations/messages.
            db.execute("UPDATE settings SET message_opt_in = 0, history_epoch = history_epoch + 1 WHERE id = 1")
            return settings(db)

    return app


app = create_app()


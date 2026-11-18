"""API en lecture seule d'EyesOnMe : gestes, actions et réglages d'un profil."""
import os
import re
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

PROFILE_NAME_PATTERN = r"^[a-z][a-z0-9_-]{0,63}$"
POOL_MAX_SIZE = 3  # machine à 1 Go de RAM : peu de connexions


def _allowed_origins() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "")
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    if "*" in origins:
        raise RuntimeError("CORS_ORIGINS ne doit pas contenir '*'")
    return origins


def _make_pool() -> ConnectionPool:
    return ConnectionPool(
        os.environ["DATABASE_URL"],
        min_size=1,
        max_size=POOL_MAX_SIZE,
        kwargs={"row_factory": dict_row},
        open=False,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = _make_pool()
    pool.open(wait=True, timeout=10)
    app.state.pool = pool
    yield
    pool.close()


app = FastAPI(title="EyesOnMe API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_methods=["GET"],
    allow_headers=[],
)


def get_pool() -> ConnectionPool:
    return app.state.pool


Pool = Annotated[ConnectionPool, Depends(get_pool)]


def _fetch(pool: ConnectionPool, query: str, params: tuple = ()) -> list[dict]:
    # Requêtes toujours paramétrées : jamais de valeur concaténée dans le SQL.
    with pool.connection() as conn:
        return conn.execute(query, params).fetchall()


@app.get("/health")
def health(pool: Pool) -> dict:
    _fetch(pool, "SELECT 1")
    return {"status": "ok"}


@app.get("/gestures")
def list_gestures(pool: Pool) -> list[dict]:
    return _fetch(pool, "SELECT code, label, description FROM gesture ORDER BY code")


@app.get("/actions")
def list_actions(pool: Pool) -> list[dict]:
    return _fetch(
        pool,
        "SELECT code, label, description, params_schema FROM action_type ORDER BY code",
    )


@app.get("/profiles/{name}/bindings")
def list_bindings(
    pool: Pool, name: Annotated[str, Path(pattern=PROFILE_NAME_PATTERN)]
) -> dict:
    if not _fetch(pool, "SELECT 1 FROM profile WHERE name = %s", (name,)):
        raise HTTPException(status_code=404, detail="Profil inconnu")
    bindings = _fetch(
        pool,
        """SELECT gesture_code AS gesture, hand, trigger, action_code AS action, params
           FROM binding WHERE profile_name = %s
           ORDER BY gesture_code, hand, trigger""",
        (name,),
    )
    return {"profile": name, "bindings": bindings}

"""
依存注入 (DI) で Psycopg3 の非同期接続を提供する。

考え方:
- リクエストごとに接続をプールから借用し、処理終了時に返却する（yield依存）。
- 書込み系の `commit/rollback` の責務はルーター側に置き、CRUD層は純粋操作に集中する。
- 型注釈は `AsyncIterator[AsyncConnection]` を使うと、`yield` 依存の意図をツールが理解しやすい。
"""

from typing import AsyncIterator
from psycopg import AsyncConnection  # 型ヒント用途
from .db import pool

async def get_conn() -> AsyncIterator[AsyncConnection]:
    async with pool.connection() as conn:
        # 依存関数で `yield` を使うことで、FastAPI が終了時に後処理（ここではプールへの返却）を行う
        yield conn

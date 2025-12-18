"""
DB CRUD 操作を Psycopg3 (Async) で実装。

方針:
- 依存注入で受け取る `AsyncConnection` を用いて、シンプルな SQL を実行する。
- 返却値は辞書（dict）として構築し、FastAPI が `response_model` に従って整形する。
- コミットはルーター側で行う（書き込み系）。

Psycopg 使用のポイント:
- パラメータ化: `WHERE id = %s` のようにプレースホルダを使い、値はタプルで渡す（SQLインジェクション対策）。
- RETURNING: `INSERT/UPDATE ... RETURNING` で変更後の行を即取得でき、Pydanticレスポンスへ自然に渡せる。
- カーソル: `async with conn.cursor()` で非同期カーソルを安全に扱う（クローズが自動）。
- 更新SQLの動的生成: 更新対象のみ `SET` に含める。空更新の場合は現状値を返すなど、API自然な挙動にする。

SQL解説（このファイルで使うクエリの背景）:
- SELECT + ORDER BY: 並び順の安定性を確保するため主キーでの `ORDER BY id` を利用。大量件数ではインデックス利用で効率化。
- ページネーション: 学習では全件取得。実務では `LIMIT/OFFSET` か、より高速なキーセット方式（`WHERE id > :last ORDER BY id LIMIT :n`）。
- INSERT: 既定値（`DEFAULT`）の適用や自動採番はサーバ側で行われる。`RETURNING` で確定値を取得。
- UPSERT: 一意制約と併用して `INSERT ... ON CONFLICT (...) DO UPDATE SET ...` を使うと同時実行に強い。
- UPDATE: 影響行数が0なら「対象なし」。同時更新対策では `FOR UPDATE` の悲観ロックや、バージョン列の楽観ロックが有効。
- DELETE: 参照整合性の設計次第で `ON DELETE CASCADE/RESTRICT` を使う。ハードデリートの代わりに「削除フラグ」運用も一般的。
"""

from typing import Optional
from psycopg import AsyncConnection

# 一覧取得
async def list_todos(conn: AsyncConnection):
    """Todo を ID 順で全件取得する。"""
    async with conn.cursor() as cur:
        # ORDER BY は安定した並びを保証する。大規模では LIMIT/OFFSET かキーセット式を検討。
        await cur.execute("SELECT id, title, completed FROM todos ORDER BY id")
        rows = await cur.fetchall()
        return [{"id": r[0], "title": r[1], "completed": r[2]} for r in rows]

# 単体取得
async def get_todo(conn: AsyncConnection, todo_id: int):
    """ID で 1 件を取得。見つからなければ None を返す。"""
    async with conn.cursor() as cur:
        # 主キー検索はインデックス利用で高速。
        await cur.execute("SELECT id, title, completed FROM todos WHERE id = %s", (todo_id,))
        row = await cur.fetchone()
        if not row:
            return None
        return {"id": row[0], "title": row[1], "completed": row[2]}

# 追加
async def create_todo(conn: AsyncConnection, title: str):
    """新規 Todo を追加し、最新状態を返す。"""
    async with conn.cursor() as cur:
        await cur.execute(
            "INSERT INTO todos (title, completed) VALUES (%s, %s) RETURNING id, title, completed",
            (title, False),
        )
        row = await cur.fetchone()
        return {"id": row[0], "title": row[1], "completed": row[2]}

# 更新（部分）
async def update_todo(conn: AsyncConnection, todo_id: int, title: Optional[str] = None, completed: Optional[bool] = None):
    """ID 指定で部分更新。存在しなければ None。"""
    fields = []
    params = []
    if title is not None:
        fields.append("title = %s")
        params.append(title)
    if completed is not None:
        fields.append("completed = %s")
        params.append(completed)
    if not fields:
        # 変更指示がなければ現状を返す（PATCHの自然な挙動）
        return await get_todo(conn, todo_id)

    params.append(todo_id)
    sql = f"UPDATE todos SET {', '.join(fields)} WHERE id = %s RETURNING id, title, completed"
    async with conn.cursor() as cur:
        # RETURNING により更新後の確定値を1往復で取得可能。
        await cur.execute(sql, tuple(params))
        row = await cur.fetchone()
        if not row:
            return None
        return {"id": row[0], "title": row[1], "completed": row[2]}

# 削除
async def delete_todo(conn: AsyncConnection, todo_id: int):
    """ID 指定で削除。存在しなければ False。"""
    async with conn.cursor() as cur:
        await cur.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
        # rowcount は影響行数。0なら対象なし（404相当）。
        return cur.rowcount > 0

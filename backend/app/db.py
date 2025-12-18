"""
Psycopg3（非同期）を用いた DB 初期化/接続モジュール。

概要（Psycopg3のポイント）:
- モダン: libpqに依存せず「C拡張なし/純Pythonのbinary配布」も選べる。Windowsでも導入容易。
- 非同期対応: `psycopg.AsyncConnection` / `psycopg_pool.AsyncConnectionPool` により、async/awaitでDB操作可能。
- パラメータバインディング: クエリは `... WHERE id = %s` のように書き、実引数はタプルで渡す。SQLインジェクション対策として必須。
- RETURNING: `INSERT/UPDATE ... RETURNING ...` で挿入/更新後の行を即取得できる（自動採番IDの取得などに便利）。
- Rowファクトリ: `conn.cursor(row_factory=psycopg.rows.dict_row)` とすれば、行を辞書で受け取れる（本サンプルはタプルで実装）。
- トランザクション: 既定はトランザクション境界内（autocommit=False）。変更系は `await conn.commit()`、失敗時は `await conn.rollback()` を行う設計が望ましい。

構成:
- `DATABASE_URL`: 接続文字列。例: `postgresql://postgres:postgres@localhost:5432/appdb`
- `pool`: 非同期接続プール。各リクエストが接続を借用し、終了時に返却される。

運用・設計のポイント（Psycopg + PostgreSQL）:
- コネクションプーリング: `min_size`/`max_size` を負荷に応じて調整。大量同時接続が見込まれる場合は監視・チューニングが必要。
- ステートメントキャッシュ: Psycopgは内部に準備済みステートメントのキャッシュを持ち、同種SQLの繰り返しが高速化される。
- アイソレーションレベル: 既定は `READ COMMITTED`。競合が懸念される箇所では `FOR UPDATE` や適切なユニーク制約・インデックスの設計が重要。
- マイグレーション: 学習用の `CREATE TABLE IF NOT EXISTS` で始め、実務では Alembic 等でスキーマ差分を管理する。
- I/O表現: テキスト/バイナリの扱い、型マッピング（boolean, timestamp 等）はPsycopgが適切に変換。必要に応じてアダプタを定義可能。
        - DDL設計の要点: NOT NULL/DEFAULT/PRIMARY KEY/UNIQUE/CHECK/FOREIGN KEY を適切に組み合わせ、整合性と性能を両立する。
            例（拡張の参考・コメント）:
                # ALTER TABLE todos ADD CONSTRAINT todos_title_unique UNIQUE (title);
                # ALTER TABLE todos ADD CONSTRAINT todos_title_nonempty CHECK (length(title) > 0);
                # CREATE INDEX idx_todos_completed ON todos (completed);
"""
import os
import asyncio
from dotenv import load_dotenv
from psycopg_pool import AsyncConnectionPool
import psycopg

"""
Psycopg3 の非同期プールを使った DB 初期化/接続モジュール。

構成:
- `DATABASE_URL`: 接続文字列。例: `postgresql://postgres:postgres@localhost:5432/appdb`
- `pool`: AsyncConnectionPool。各リクエストから接続を借用してクエリ実行。

運用・設計のポイント（PostgreSQL + Psycopg Async）:
- コネクションプーリング: `min_size`/`max_size` を負荷に合わせて調整。`open=True` で即時オープン。
- トランザクション境界: ルーターで `await conn.commit()` を明示。失敗時は `await conn.rollback()` を行う設計が望ましい。
- アイソレーションレベル: 同時更新が懸念される場合は `SELECT ... FOR UPDATE` などを活用。
- マイグレーション: 学習用の `CREATE TABLE IF NOT EXISTS`。実務は Alembic で管理する。
"""

load_dotenv()
# 環境変数から接続文字列を読み取る。未設定時はローカルのPostgreSQLに接続。
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/appdb")

# 非同期コネクションプールの作成
# open=True で即時オープン（起動時のDDL実行に備える）。必要に応じてクローズ/再オープン可能。
pool = AsyncConnectionPool(DATABASE_URL, min_size=1, max_size=10, open=True)

async def init_db(max_tries: int = 10, initial_delay: float = 1.0):
    """
    学習用: アプリ起動時にテーブルを作成する。
    DBが起動直後で接続が失敗するケースに備えて、リトライを行う。
    """
    delay = initial_delay
    last_exc: Exception | None = None
    for _ in range(max_tries):
        try:
            async with pool.connection() as conn:
                # dict_row を使いたい場合:
                # from psycopg.rows import dict_row
                # async with conn.cursor(row_factory=dict_row) as cur:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS todos (
                          id SERIAL PRIMARY KEY,
                          title VARCHAR(200) NOT NULL,
                          completed BOOLEAN NOT NULL DEFAULT FALSE
                        )
                        """
                    )
                                        # 上記DDLの意図:
                                        # - id: 連番主キー。検索/更新/削除の主キーに使用。
                                        # - title: 必須（NOT NULL）で、長さ上限を明示（VARCHAR(200)）。
                                        # - completed: 必須で、既定値FALSE。ブール型はPsycopgで自動変換される。
                                        # 拡張する場合は UNIQUE/INDEX/CHECK/FK などを追加し、クエリ計画（EXPLAIN）で検証する。
                    await conn.commit()
            return
        except Exception as exc:
            last_exc = exc
            await asyncio.sleep(delay)
            delay = min(delay * 1.5, 5.0)
    if last_exc:
        raise last_exc

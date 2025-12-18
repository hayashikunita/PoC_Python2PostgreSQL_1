"""
FastAPI アプリのエントリポイント。

役割:
- CORS 設定により、フロントエンド (http://localhost:5173) からのブラウザアクセスを許可。
- アプリ起動時イベントで `init_db()` を呼び、SQLAlchemy のメタデータに基づいてテーブルを作成。
- `todos` ルーターを `/api/todos` にマウントして REST エンドポイントを提供。

ポイント:
- CORS の `allow_credentials=True` は cookie 送信等の認証情報送信を許可するための設定。今回は認証を使っていないが、学習用途として残している。
- 例外時の挙動や詳細なログは uvicorn 側のログで確認できる。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db
from .routers import todos

# 学習用: FastAPIのエントリポイント。
# - CORS設定でフロント(5173)からのアクセスを許可
# - 起動時にDBのテーブルを作成（init_db）
# - /api/todos にTodo用のルーターをマウント

app = FastAPI(title="FastAPI + PostgreSQL Tutorial App")

origins = ["http://localhost:5173"]  # フロントの開発サーバーURL
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 指定したオリジンからのアクセスのみ許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    # アプリ起動時にDBメタデータからテーブルを作成する（必要に応じてリトライあり）
    await init_db()

app.include_router(todos.router, prefix="/api/todos", tags=["todos"])  # ルーティングの登録

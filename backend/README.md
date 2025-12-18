# Backend (FastAPI)

## セットアップ

1. Python仮想環境を作成して有効化
2. 依存関係をインストール
3. `.env` を作成 ( `.env.example` をコピー )
4. PostgreSQL を起動 (ルートの docker-compose.yml を使用)
5. API を起動

## コマンド例 (PowerShell)

```powershell
# ルートでDB起動 (要 Docker Desktop)
docker compose up -d

# backend ディレクトリへ
cd backend

# 依存インストール
python -m pip install -r requirements.txt

# .env 用意
Copy-Item .env.example .env

# API 起動
python -m uvicorn app.main:app --reload --port 8000
```

## エンドポイント
- GET /api/todos
- GET /api/todos/{id}
- POST /api/todos { title }
- PATCH /api/todos/{id} { title?, completed? }
- DELETE /api/todos/{id}

# Python + PostgreSQL 学習用フルスタックアプリ

FastAPI (Python) と React (TypeScript) を使って、PostgreSQL と連携するシンプルな Todo アプリです。学習用に構成をわかりやすく分割し、Windowsでのセットアップ手順を詳しく用意しています。
## スタック
- **Backend**: FastAPI, Psycopg3(Async) + psycopg_pool
- **Frontend**: React + TypeScript (Vite)
- **DB**: PostgreSQL (docker-compose)

## セットアップ手順（DockerでDB+APIを起動）
1) ルートでDBとバックエンドAPIを起動

```powershell
# ルート (このREADMEのある場所)
docker compose up -d
```

2) API疎通確認（HTTPで確認）

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/todos" -UseBasicParsing
```

3) フロントエンドの依存インストールと起動（別ターミナル推奨）

```powershell
cd frontend
npm install
npm run dev
```

起動後、ブラウザで http://localhost:5173 を開くとフロントエンドが表示されます。バックエンド API は http://localhost:8000 で動作します。

4) 停止（必要時）

```powershell
docker compose down
```
docker compose up -d
```

2) バックエンドの依存インストールと起動

```powershell
cd backend
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

3) フロントエンドの依存インストールと起動（別ターミナル推奨）

```powershell
cd frontend
npm install
npm run dev
```

起動後、ブラウザで `http://localhost:5173` を開くとフロントエンドが表示されます。バックエンド API は `http://localhost:8000` で動作します。

## API エンドポイント
- GET /api/todos — 一覧取得
- GET /api/todos/{id} — 単体取得
- POST /api/todos — 追加（JSON: `{ "title": "..." }`）
- PATCH /api/todos/{id} — 更新（JSON: `{ "title?": "...", "completed?": true }`）
- DELETE /api/todos/{id} — 削除

## よくあるハマりどころ
- Docker Desktop を起動し、Linuxコンテナモード・WSL2エンジンを有効にしてください。
- DB が起動していないと API 接続エラーになります。先に `docker compose up -d` を実行してください。
- フロントの API ベースURLは [frontend/src/api.ts](frontend/src/api.ts) の `BASE` で指定しています。ポートを変更した場合はそこも調整してください。

## 学習ポイント
- FastAPI のルーター分割、Pydantic スキーマ、Psycopg3 Async の基本
- CORS の設定（[backend/app/main.py](backend/app/main.py)）
- React の状態管理とシンプルな API 呼び出し
- docker-compose でのサービス連携（`backend` は [docker-compose.yml](docker-compose.yml) の `DATABASE_URL=...@db:5432/appdb` を使用して `db` サービスへ接続）

## Psycopg3 + SQL 設計の要点（コードの読み方ガイド）
学習・実務の双方で役に立つ設計ポイントを、コードコメントとして詳しく記載しています。以下を起点に参照してください。

- 接続とプーリング: [backend/app/db.py](backend/app/db.py)
	- 非同期プール `AsyncConnectionPool` の使い方（`min_size/max_size/open`）。
	- トランザクションは既定で有効。書込み時はルーターで `await conn.commit()`、失敗時は `rollback`。
	- `RETURNING` や row factory（`dict_row`）のヒント、ステートメントキャッシュの考え方。
- CRUDのSQL背景: [backend/app/crud.py](backend/app/crud.py)
	- SELECTの並び順（`ORDER BY id`）とページネーション（`LIMIT/OFFSET` やキーセット方式）。
	- INSERTでの `RETURNING` による確定値取得、UPSERT（`ON CONFLICT ... DO UPDATE`）の設計。
	- UPDATEの部分更新（動的に`SET`生成）と同時更新対策（`FOR UPDATE`/楽観ロック）。
	- DELETEの `rowcount` の意味、参照整合性（`CASCADE/RESTRICT`）や論理削除の選択肢。
- 依存注入（DI）: [backend/app/deps.py](backend/app/deps.py)
	- FastAPIの `yield` 依存で接続を借用・返却。型注釈は `AsyncIterator[AsyncConnection]`。
- ルーター: [backend/app/routers/todos.py](backend/app/routers/todos.py)
	- `response_model` によりレスポンス整形。書込み後に `conn.commit()` を明示する設計。

### すぐ試す（PowerShell）
```powershell
docker compose build --no-cache
docker compose up -d
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/todos" -UseBasicParsing
```

### よくある拡張
- ページネーションAPI: `GET /api/todos?limit=20&after_id=...`（キーセット方式推奨）。
- UPSERTエンドポイント: 一意制約＋`ON CONFLICT`で同時実行に強い設計。
- 辞書行の返却: `dict_row` row factoryを使って可読性を高める。

# Python2PostgreSQL
学習用

"""
Pydantic スキーマ定義。

用途:
- リクエスト/レスポンスの型安全とバリデーションを担う。
- FastAPI は `response_model=TodoRead` を指定することで、返却データをスキーマ準拠で整形する。

設計:
- `TodoCreate`: 新規作成に必要な最小限のフィールド。
- `TodoUpdate`: 部分更新に対応するため、すべて任意フィールド（None可）。
- `TodoRead`: クライアントへ返す最終形。`from_attributes=True` で ORM モデルからの変換を許可。
"""

from pydantic import BaseModel

# 学習用: 入出力のデータ形（Pydantic）を定義。APIのI/Oを明確化する。
class TodoCreate(BaseModel):
    title: str  # 追加時に必要なフィールド

class TodoUpdate(BaseModel):
    title: str | None = None      # 部分更新: タイトル（任意）
    completed: bool | None = None # 部分更新: 完了フラグ（任意）

class TodoRead(BaseModel):
    id: int
    title: str
    completed: bool
    class Config:
        # SQLAlchemyモデルから属性を読み込むための設定（ORMモード相当）
        from_attributes = True

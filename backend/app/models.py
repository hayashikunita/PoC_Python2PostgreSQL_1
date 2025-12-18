"""
SQLAlchemy モデル定義。

`Todo` テーブル:
- `id`: 主キー（自動採番）。`index=True` で検索効率の向上。
- `title`: 必須の短いテキスト。`String(200)` で最大長を制限。
- `completed`: 完了フラグ。既定値 False。

ポイント:
- Pydantic の `TodoRead` とは属性名を一致させておくと、`from_attributes=True` 設定で
    ORM モデルから直接シリアライズできる。

DB設計上の考慮:
- 文字列長: `String(200)` は UI 想定に合わせた上限制約。長文があり得る場合は `Text` 型や別テーブル管理を検討。
- インデックス: 検索パターンに応じて複合インデックスを設計（例: `completed, id`）。
- 一意性: タイトルのユニーク制約は要件次第。重複許容なら不要、禁止なら `UniqueConstraint` を付与。
- 監査: 実務では `created_at`/`updated_at` のタイムスタンプ列を設け、更新履歴管理を行う。
- 参照整合性: 他テーブルとリレーションする場合、外部キー制約を設定し `ON DELETE` ポリシーを設計。
"""

from sqlalchemy import Column, Integer, String, Boolean
from .db import Base

# 学習用: SQLAlchemyモデル。DBのテーブル構造を表現する。
class Todo(Base):
        __tablename__ = "todos"
        id = Column(Integer, primary_key=True, index=True)  # 主キー
        title = Column(String(200), nullable=False)         # タイトル（必須）
        completed = Column(Boolean, default=False)          # 完了フラグ

"""
Todo に関する REST ルーター。

エンドポイント設計:
- GET /api/todos: 一覧取得 (200)
- GET /api/todos/{id}: 単体取得 (200) / 見つからなければ 404
- POST /api/todos: 追加 (201) / バリデーション失敗時は 422 (FastAPI 標準)
- PATCH /api/todos/{id}: 部分更新 (200) / 見つからなければ 404
- DELETE /api/todos/{id}: 削除 (204) / 見つからなければ 404

注意:
- Psycopgは既定でトランザクション内にいるため、書込み系では `await conn.commit()` を明示的に実行する（失敗時はrollbackする設計が望ましい）。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import AsyncConnection
from ..deps import get_conn
from .. import crud
from ..schemas import TodoCreate, TodoUpdate, TodoRead

router = APIRouter()

@router.get("/", response_model=list[TodoRead])
async def list_todos(conn: AsyncConnection = Depends(get_conn)):
    """Todo一覧を取得するエンドポイント"""
    return await crud.list_todos(conn)

@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(todo_id: int, conn: AsyncConnection = Depends(get_conn)):
    """指定IDのTodoを1件取得。存在しない場合は404"""
    todo = await crud.get_todo(conn, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Not found")
    return todo

@router.post("/", response_model=TodoRead, status_code=201)
async def create_todo(payload: TodoCreate, conn: AsyncConnection = Depends(get_conn)):
    """Todoを新規作成して返す。201 Created"""
    todo = await crud.create_todo(conn, title=payload.title)
    await conn.commit()
    return todo

@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo(todo_id: int, payload: TodoUpdate, conn: AsyncConnection = Depends(get_conn)):
    """Todoを部分更新（title/completed）。存在しなければ404"""
    todo = await crud.update_todo(conn, todo_id=todo_id, title=payload.title, completed=payload.completed)
    if not todo:
        raise HTTPException(status_code=404, detail="Not found")
    await conn.commit()
    return todo

@router.delete("/{todo_id}", status_code=204)
async def delete_todo(todo_id: int, conn: AsyncConnection = Depends(get_conn)):
    """Todoを削除。存在しなければ404。204 No Content"""
    ok = await crud.delete_todo(conn, todo_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    await conn.commit()
    return None

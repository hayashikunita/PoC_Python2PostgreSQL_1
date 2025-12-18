import type { Todo } from './types'

/**
 * フロントエンドからバックエンドの REST API を呼び出すクライアント。
 * 
 * 設計:
 * - BASE は固定 URL。環境変数化したい場合は Vite の `import.meta.env` を利用する。
 * - fetch の `res.ok` を都度検査し、失敗時は Error を投げて上位でハンドリングする。
 * - 返却値は JSON をパースして `Todo` 型として扱う（実際はランタイムの型検証はないため、バックエンド側のスキーマ整合が重要）。
 */
const BASE = 'http://localhost:8000/api/todos' // バックエンドのベースURL

/** Todo一覧を取得（GET /api/todos） */
export async function listTodos(): Promise<Todo[]> {
  const res = await fetch(BASE)
  if (!res.ok) throw new Error('Failed to fetch todos')
  return res.json()
}

/** Todoを追加（POST /api/todos） */
export async function createTodo(title: string): Promise<Todo> {
  const res = await fetch(BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  })
  if (!res.ok) throw new Error('Failed to create')
  return res.json()
}

/** Todoを部分更新（PATCH /api/todos/{id}） */
export async function updateTodo(id: number, data: Partial<Pick<Todo, 'title' | 'completed'>>): Promise<Todo> {
  const res = await fetch(`${BASE}/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  if (!res.ok) throw new Error('Failed to update')
  return res.json()
}

/** Todoを削除（DELETE /api/todos/{id}） */
export async function deleteTodo(id: number): Promise<void> {
  const res = await fetch(`${BASE}/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete')
}

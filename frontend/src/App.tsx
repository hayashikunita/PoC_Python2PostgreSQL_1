import { useEffect, useState } from 'react'
import TodoForm from './components/TodoForm'
import TodoList from './components/TodoList'
import { listTodos } from './api'
import type { Todo } from './types'

/**
 * 画面のトップコンポーネント。
 * 
 * 構成:
 * - `todos`: 表示用の一覧状態
 * - `loading`: 通信中フラグ（UX向上）
 * - `error`: エラー文字列（失敗時に表示）
 * 
 * フロー:
 * - 初回マウントで一覧取得
 * - 追加/更新/削除の完了後は一覧を再取得し、最新状態を反映
 */
export default function App() {
  const [todos, setTodos] = useState<Todo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 一覧を読み込む（通信状態とエラーハンドリングを管理）
  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await listTodos()
      setTodos(data)
    } catch (e: any) {
      setError(e?.message ?? '読み込みに失敗しました')
    } finally {
      setLoading(false)
    }
  }

  // 初回マウント時に読み込み
  useEffect(() => {
    load()
  }, [])

  return (
    <div className="container">
      <h1>学習用 Todo アプリ</h1>
      <p className="muted">FastAPI + PostgreSQL + React (TS)</p>

      {/* 追加フォーム。追加成功時に一覧再取得 */}
      <TodoForm onCreated={load} />

      {loading ? (
        <p>読み込み中...</p>
      ) : error ? (
        <p className="error">{error}</p>
      ) : (
        // Todoリスト。チェックや削除で変更後は一覧再取得
        <TodoList items={todos} onChanged={load} />
      )}
    </div>
  )
}

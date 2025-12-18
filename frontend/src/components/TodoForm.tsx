import { useState } from 'react'
import { createTodo } from '../api'

// 学習用: 新規Todoを追加するフォーム。
// props: onCreated - 追加成功後に一覧再取得を依頼するコールバック
export default function TodoForm({ onCreated }: { onCreated: () => void }) {
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(false)

  // フォーム送信ハンドラ（空文字は無視）
  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return
    setLoading(true)
    try {
      await createTodo(title.trim())
      setTitle('')
      onCreated()
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={submit} className="row">
      <input
        value={title}
        onChange={e => setTitle(e.target.value)}
        placeholder="新しいTodoのタイトル"
      />
      <button type="submit" disabled={loading}>
        追加
      </button>
    </form>
  )
}

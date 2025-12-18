import type { Todo } from '../types'
import { deleteTodo, updateTodo } from '../api'

// 学習用: Todo一覧の表示と操作（チェック・削除）を担当
export default function TodoList({ items, onChanged }: { items: Todo[]; onChanged: () => void }) {
  // 完了フラグのトグル
  const toggle = async (t: Todo) => {
    await updateTodo(t.id, { completed: !t.completed })
    onChanged()
  }
  // 削除
  const remove = async (id: number) => {
    await deleteTodo(id)
    onChanged()
  }

  return (
    <ul className="list">
      {items.map(t => (
        <li key={t.id}>
          <label>
            <input type="checkbox" checked={t.completed} onChange={() => toggle(t)} />
            <span className={t.completed ? 'done' : ''}>{t.title}</span>
          </label>
          <button className="danger" onClick={() => remove(t.id)}>削除</button>
        </li>
      ))}
    </ul>
  )
}

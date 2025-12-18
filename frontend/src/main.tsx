import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles.css'

// 学習用: Viteのエントリ。Reactコンポーネントを#rootにマウントする。
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)

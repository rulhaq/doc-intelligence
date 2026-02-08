import React from 'react'
import ReactDOM from 'react-dom'
import './index.css'
import './i18n/config'
import App from './App'

// Set initial language and direction
const savedLang = localStorage.getItem('i18nextLng') || 'en';
document.documentElement.dir = savedLang === 'ar' ? 'rtl' : 'ltr';
document.documentElement.lang = savedLang;

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
)

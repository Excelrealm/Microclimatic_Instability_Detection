import { useState, useEffect } from 'react';
import './ThemeToggle.css';

function ThemeToggle() {
  const [dark, setDark] = useState(() => {
    return localStorage.getItem('theme') === 'dark';
  });

  useEffect(() => {
    if (dark) {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('theme', 'light');
    }
  }, [dark]);

  return (
    <button onClick={() => setDark(!dark)} className="theme-toggle" title="Toggle theme">
      {dark ? '☀️ Light' : '🌙 Dark'}
    </button>
  );
}

export default ThemeToggle;
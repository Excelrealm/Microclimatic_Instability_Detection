import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ThemeToggle from './ThemeToggle';
import InfoModal from './InfoModal';
import './Header.css';

function Header() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formattedDate = currentTime.toLocaleDateString('en-NG', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  const formattedTime = currentTime.toLocaleTimeString('en-NG', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
  });

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-title">
          <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
            <h1>🌦️ Microclimate Monitoring</h1>
            <p>Atmospheric Instability Detection System</p>
          </Link>
        </div>
        <div className="header-time">
          <div className="date">{formattedDate}</div>
          <div className="time">{formattedTime}</div>
        </div>
        <div className="header-actions">
          <Link to="/" className="nav-link">🏠 Home</Link>
          <Link to="/learn" className="nav-link">📚 Learn</Link>
          <InfoModal />
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}

export default Header;
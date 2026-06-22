import { useState, useEffect } from 'react';
import { REFRESH_INTERVAL } from '../config';
import './RefreshTimer.css';

function RefreshTimer() {
  const [secondsLeft, setSecondsLeft] = useState(REFRESH_INTERVAL / 1000);

  useEffect(() => {
    const timer = setInterval(() => {
      setSecondsLeft((prev) => (prev <= 1 ? REFRESH_INTERVAL / 1000 : prev - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const minutes = Math.floor(secondsLeft / 60);
  const seconds = secondsLeft % 60;

  return (
    <span className="refresh-timer">
      Next refresh in: {minutes}:{seconds.toString().padStart(2, '0')}
    </span>
  );
}

export default RefreshTimer;
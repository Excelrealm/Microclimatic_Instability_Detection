import { useState, useEffect } from 'react';
import { fetchCurrentConditions } from '../services/api';
import './StatusBadge.css';

function StatusBadge() {
  const [status, setStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [lastReading, setLastReading] = useState<string | null>(null);
  const [staleMinutes, setStaleMinutes] = useState<number>(0);

  useEffect(() => {
    const check = async () => {
      try {
        const response = await fetchCurrentConditions();
        if (response.status === 'success' && response.data) {
          const lastTimestamp = new Date(response.data.timestamp);
          const now = new Date();
          const diffMinutes = Math.floor((now.getTime() - lastTimestamp.getTime()) / 60000);

          setStaleMinutes(diffMinutes);
          setLastReading(lastTimestamp.toLocaleTimeString('en-NG'));

          // Offline if last reading is more than 3 minutes old
          if (diffMinutes > 3) {
            setStatus('offline');
          } else {
            setStatus('online');
          }
        } else {
          setStatus('offline');
        }
      } catch {
        setStatus('offline');
      }
    };

    check();
    const interval = setInterval(check, 30000); // check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const config = {
    online: { color: '#28a745', text: 'System Online', icon: '🟢' },
    offline: { color: '#dc3545', text: `ESP Offline (${staleMinutes}m)`, icon: '🔴' },
    checking: { color: '#ffc107', text: 'Checking...', icon: '🟡' },
  };

  const c = config[status];

  return (
    <div className="status-badge" style={{ borderColor: c.color }}>
      <span className="status-icon">{c.icon}</span>
      <div>
        <span className="status-text">{c.text}</span>
        {lastReading && (
          <span className="status-time">Last reading: {lastReading}</span>
        )}
      </div>
    </div>
  );
}

export default StatusBadge;
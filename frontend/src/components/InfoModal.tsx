import { useState } from 'react';
import './InfoModal.css';

function InfoModal() {
  const [open, setOpen] = useState(false);

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="info-trigger" title="About this system">
        ℹ️ About
      </button>
    );
  }

  return (
    <div className="modal-overlay" onClick={() => setOpen(false)}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={() => setOpen(false)}>✕</button>
        <h2>About This System</h2>

        <h3>📡 Overview</h3>
        <p>
          This is a low-cost IoT-based microclimate monitoring and atmospheric instability
          detection system developed at Covenant University. It combines real-time sensor data
          with thermodynamic analysis to provide accessible weather intelligence.
        </p>

        <h3>🔬 Methodology</h3>
        <ul>
          <li><strong>Sensor:</strong> BME280 — temperature, humidity, pressure</li>
          <li><strong>Microcontroller:</strong> ESP32 with WiFi connectivity</li>
          <li><strong>Dew Point:</strong> Magnus-Tetens formula (Magnus, 1844)</li>
          <li><strong>Theta-E:</strong> Equivalent potential temperature (Bolton, 1980)</li>
          <li><strong>LI Proxy:</strong> Surface-based lifted index approximation</li>
          <li><strong>Remote Data:</strong> Open-Meteo API for station comparison</li>
        </ul>

        <h3>📊 Instability Indicators</h3>
        <ul>
          <li><strong>Dew Point Spread</strong> &lt; 2°C → near saturation, fog/rain possible</li>
          <li><strong>LI Proxy</strong> &lt; −2 → unstable atmosphere, convection likely</li>
          <li><strong>Theta-E</strong> &gt; 350 K → high moist static energy</li>
          <li><strong>Falling Pressure</strong> + high humidity → potential disturbance</li>
        </ul>

        <h3>🎓 Academic Context</h3>
        <p>
          This project addresses SDG 13 (Climate Action) by democratizing access to
          environmental monitoring tools. It is designed for educational institutions,
          small-scale researchers, and communities with limited access to meteorological
          infrastructure.
        </p>

        <p className="modal-footer">
          Covenant University • Computer Engineering • 2025<br />
          Supervisor: Dr. Olowoleni Joseph
        </p>
      </div>
    </div>
  );
}

export default InfoModal;
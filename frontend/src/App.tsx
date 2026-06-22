import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import LearnPage from './components/LearnPage';
import AIChat from './components/AIChat';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Header />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/learn" element={<LearnPage />} />
      </Routes>
      <footer className="footer">
        <p>Low-Cost IoT-Based Microclimate Monitoring &amp; Atmospheric Instability Detection System</p>
        <p className="footer-sub">Covenant University &bull; Computer Engineering &bull; 2025</p>
      </footer>
      <AIChat />
    </BrowserRouter>
  );
}

export default App;
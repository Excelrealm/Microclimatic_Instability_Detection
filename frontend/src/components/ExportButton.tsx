import type { ProcessedReading } from '../types';
import './ExportButton.css';

interface Props {
  historyData: ProcessedReading[];
}

function ExportButton({ historyData }: Props) {
  if (!historyData || historyData.length === 0) return null;

  const handleExport = () => {
    const link = document.createElement('a');
    link.href = 'http://localhost:8000/api/export/csv';
    link.download = `microclimate-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
  };

  return (
    <button onClick={handleExport} className="export-btn">
      📥 Export CSV records
    </button>
  );
}

export default ExportButton;
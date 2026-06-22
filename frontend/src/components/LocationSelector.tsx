import { useState, useEffect, useRef } from 'react';
import { fetchRemoteWeather } from '../services/api';
import type { RemoteWeatherData } from '../services/api';
import './LocationSelector.css';

interface Location {
  name: string;
  lat: number;
  lon: number;
  country: string;
  admin1?: string;
}

interface Props {
  onWeatherReceived: (data: RemoteWeatherData) => void;
}

function LocationSelector({ onWeatherReceived }: Props) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<Location[]>([]);
  const [loading, setLoading] = useState(false);
  const [fetchingWeather, setFetchingWeather] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const debounceRef = useRef<number | null>(null);

  useEffect(() => {
    if (debounceRef.current !== null) clearTimeout(debounceRef.current);

    if (query.trim().length < 2) {
      setSuggestions([]);
      setShowDropdown(false);
      return;
    }

    debounceRef.current = window.setTimeout(async () => {
      setLoading(true);
      try {
        const searchQuery = query.trim();
        
        // Request more results and let Open-Meteo's ranking do the work
        const res = await fetch(
          `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(searchQuery)}&count=10&language=en&format=json`
        );
        if (!res.ok) throw new Error('Geocoding failed');
        const data = await res.json();
        
        if (data.results) {
          const seen = new Set<string>();
          const unique: Location[] = [];
          for (const item of data.results) {
            const key = `${item.name}::${item.admin1 || ''}::${item.country}`;
            if (!seen.has(key)) {
              seen.add(key);
              unique.push({
                name: item.name,
                lat: item.latitude,
                lon: item.longitude,
                country: item.country || '',
                admin1: item.admin1 || '',
              });
              if (unique.length === 5) break;
            }
          }
          setSuggestions(unique);
        } else {
          setSuggestions([]);
        }
        setShowDropdown(true);
      } catch {
        setError('Could not search locations.');
        setSuggestions([]);
        setShowDropdown(true);
      } finally {
        setLoading(false);
      }
    }, 400);

    return () => {
      if (debounceRef.current !== null) {
        clearTimeout(debounceRef.current);
        debounceRef.current = null;
      }
    };
  }, [query]);

  const handleSelect = async (location: Location) => {
    const label = location.admin1
      ? `${location.name}, ${location.admin1}, ${location.country}`
      : `${location.name}, ${location.country}`;
    setQuery(label);
    setShowDropdown(false);
    setSuggestions([]);
    setFetchingWeather(true);
    setError(null);

    try {
      const data = await fetchRemoteWeather(location.lat, location.lon, label);
      onWeatherReceived(data);
    } catch {
      setError('Failed to fetch weather for selected location.');
    } finally {
      setFetchingWeather(false);
    }
  };

  const getLocationLabel = (loc: Location) => {
    if (loc.admin1) {
      return `${loc.name}, ${loc.admin1}, ${loc.country}`;
    }
    return `${loc.name}, ${loc.country}`;
  };

  return (
    <div className="location-selector">
      <h3>📍 Remote Weather Station</h3>
      <p className="selector-subtitle">Search for any city worldwide</p>
      <div className="search-container">
        <input
          type="text"
          className="location-search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., London, Lagos, Ota, Tokyo..."
          disabled={fetchingWeather}
        />
        {loading && <span className="search-spinner">⏳</span>}
        {showDropdown && suggestions.length > 0 && (
          <ul className="suggestions-list">
            {suggestions.map((loc, idx) => (
              <li
                key={idx}
                onClick={() => handleSelect(loc)}
                className="suggestion-item"
              >
                {getLocationLabel(loc)}
              </li>
            ))}
          </ul>
        )}
        {showDropdown && suggestions.length === 0 && !loading && (
          <ul className="suggestions-list">
            <li className="suggestion-item no-results">
              No results. Try adding country, e.g., "Ota, Nigeria" or "London, UK"
            </li>
          </ul>
        )}
      </div>
      {fetchingWeather && <p className="loading-text">Fetching weather data…</p>}
      {error && <p className="error-text">{error}</p>}
    </div>
  );
}

export default LocationSelector;
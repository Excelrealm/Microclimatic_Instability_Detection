"""
AI Weather Assistant using local Ollama model.
Provides plain-language explanations of atmospheric conditions.
"""

import requests
from typing import Optional


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:1b"


def build_weather_context(current_data: dict) -> str:
    """Build a concise weather summary for the AI to reference."""
    alerts_text = (
        ", ".join(current_data.get("alerts", []))
        if current_data.get("alerts")
        else "None"
    )

    return f"""
Current atmospheric conditions at this microclimate station:
- Temperature: {current_data.get('temperature', 'N/A')}°C
- Humidity: {current_data.get('humidity', 'N/A')}%
- Atmospheric Pressure: {current_data.get('pressure', 'N/A')} hPa
- Dew Point: {current_data.get('dew_point', 'N/A')}°C
- Dew Point Spread: {current_data.get('dew_point_spread', 'N/A')}°C
- Pressure Tendency: {current_data.get('pressure_tendency_label', 'N/A')}
- Lifted Index Proxy: {current_data.get('li_proxy', 'N/A')}°C
- Theta-E: {current_data.get('theta_e', 'N/A')} K
- CAPE Proxy: {current_data.get('cape_proxy', 'N/A')} J/kg
- Convective Temperature: {current_data.get('convective_temperature', 'N/A')}°C
- Rainfall Probability: {current_data.get('rainfall_probability', 'N/A')}%
- Active Alerts: {alerts_text}
- Anomaly Detected: {current_data.get('anomaly_detected', 'N/A')}
- Weather Pattern: {current_data.get('weather_pattern_label', 'N/A')}
"""


def ask_weather_assistant(
    question: str,
    current_data: Optional[dict] = None,
) -> dict:
    """Ask the AI assistant about current weather conditions."""

    system_prompt = """You are a helpful meteorological assistant for a microclimate 
monitoring system developed at Covenant University. You explain atmospheric 
conditions in simple, educational terms. You are encouraging and patient. 
When explaining concepts, relate them to what the user can observe or expect. 
Keep answers concise — 2 to 4 sentences unless asked for detail.
You can reference the specific weather data provided to give personalized answers."""

    context = ""
    if current_data:
        context = build_weather_context(current_data)

    full_prompt = f"""System: {system_prompt}

Weather Context:
{context}

User Question: {question}

Assistant:"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 300,
                },
            },
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "answer": result.get("response", "").strip(),
                "model": MODEL,
                "success": True,
            }
        else:
            return {
                "answer": "I'm having trouble connecting to the AI model. Please ensure Ollama is running.",
                "success": False,
            }

    except requests.exceptions.ConnectionError:
        return {
            "answer": "The AI assistant is currently unavailable. Please start Ollama with 'ollama serve'.",
            "success": False,
        }
    except Exception as e:
        return {
            "answer": "An error occurred while processing your question. Please try again.",
            "success": False,
        }


def get_weather_summary(current_data: dict) -> str:
    """Generate an auto-summary of current conditions using AI."""
    question = (
        "In 2-3 sentences, summarize the current weather conditions "
        "and what someone should expect in the near future."
    )
    result = ask_weather_assistant(question, current_data)
    return result.get("answer", "Summary unavailable.")
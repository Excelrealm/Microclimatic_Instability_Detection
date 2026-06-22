#type: ignore
"""
AI Weather Assistant using Google Gemini (free tier).
"""

import os
import google.generativeai as genai
from typing import Optional

API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY environment variable is not set")

genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash"


def build_weather_context(current_data: dict) -> str:
    return f"""
Current atmospheric conditions at this microclimate station:
- Temperature: {current_data.get('temperature', 'N/A')}°C
- Humidity: {current_data.get('humidity', 'N/A')}%
- Pressure: {current_data.get('pressure', 'N/A')} hPa
- Dew Point: {current_data.get('dew_point', 'N/A')}°C
- Dew Point Spread: {current_data.get('dew_point_spread', 'N/A')}°C
- Pressure Tendency: {current_data.get('pressure_tendency_label', 'N/A')}
- Lifted Index Proxy: {current_data.get('li_proxy', 'N/A')}°C
- Theta-E: {current_data.get('theta_e', 'N/A')} K
- CAPE Proxy: {current_data.get('cape_proxy', 'N/A')} J/kg
- Rainfall Probability: {current_data.get('rainfall_probability', 'N/A')}%
- ML Instability Score: {current_data.get('composite_instability_score', 'N/A')}
- Alerts: {', '.join(current_data.get('alerts', [])) if current_data.get('alerts') else 'None'}
"""


def ask_weather_assistant(question: str, current_data: Optional[dict] = None) -> dict:
    system_prompt = """You are a helpful meteorological and agricultural assistant.
Explain weather concepts in simple terms, suitable for students and farmers.
Relate current readings to practical farming decisions and climate awareness.
Be educational and encouraging. Keep answers 2-4 sentences unless asked for detail."""

    context = build_weather_context(current_data) if current_data else ""
    full_prompt = f"System: {system_prompt}\n\nContext:\n{context}\n\nUser: {question}\n\nAssistant:"

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=300,
                temperature=0.7,
            )
        )
        return {"answer": response.text.strip(), "model": MODEL_NAME, "success": True}
    except Exception as e:
        return {"answer": f"Sorry, I couldn't process your request. Error: {str(e)}", "success": False}
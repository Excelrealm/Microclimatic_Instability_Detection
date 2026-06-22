###
# """
# AI Weather Assistant using local Ollama model.
# Provides plain-language explanations of atmospheric conditions.
# """

# import requests
# from typing import Optional


# OLLAMA_URL = "http://localhost:11434/api/generate"
# MODEL = "llama3.2:1b"


# def build_weather_context(current_data: dict) -> str:
#     """Build a concise weather summary for the AI to reference."""
#     alerts_text = (
#         ", ".join(current_data.get("alerts", []))
#         if current_data.get("alerts")
#         else "None"
#     )

#     return f"""
# Current atmospheric conditions at this microclimate station:
# - Temperature: {current_data.get('temperature', 'N/A')}°C
# - Humidity: {current_data.get('humidity', 'N/A')}%
# - Atmospheric Pressure: {current_data.get('pressure', 'N/A')} hPa
# - Dew Point: {current_data.get('dew_point', 'N/A')}°C
# - Dew Point Spread: {current_data.get('dew_point_spread', 'N/A')}°C
# - Pressure Tendency: {current_data.get('pressure_tendency_label', 'N/A')}
# - Lifted Index Proxy: {current_data.get('li_proxy', 'N/A')}°C
# - Theta-E: {current_data.get('theta_e', 'N/A')} K
# - CAPE Proxy: {current_data.get('cape_proxy', 'N/A')} J/kg
# - Convective Temperature: {current_data.get('convective_temperature', 'N/A')}°C
# - Rainfall Probability: {current_data.get('rainfall_probability', 'N/A')}%
# - Active Alerts: {alerts_text}
# - Anomaly Detected: {current_data.get('anomaly_detected', 'N/A')}
# - Weather Pattern: {current_data.get('weather_pattern_label', 'N/A')}
# """


# def ask_weather_assistant(
#     question: str,
#     current_data: Optional[dict] = None,
# ) -> dict:
#     """Ask the AI assistant about current weather conditions."""

#     system_prompt = """You are a helpful meteorological assistant for a microclimate 
# monitoring system developed at Covenant University. You explain atmospheric 
# conditions in simple, educational terms. You are encouraging and patient. 
# When explaining concepts, relate them to what the user can observe or expect. 
# Keep answers concise — 2 to 4 sentences unless asked for detail.
# You can reference the specific weather data provided to give personalized answers."""

#     context = ""
#     if current_data:
#         context = build_weather_context(current_data)

#     full_prompt = f"""System: {system_prompt}

# Weather Context:
# {context}

# User Question: {question}

# Assistant:"""

#     try:
#         response = requests.post(
#             OLLAMA_URL,
#             json={
#                 "model": MODEL,
#                 "prompt": full_prompt,
#                 "stream": False,
#                 "options": {
#                     "temperature": 0.7,
#                     "max_tokens": 300,
#                 },
#             },
#             timeout=30,
#         )

#         if response.status_code == 200:
#             result = response.json()
#             return {
#                 "answer": result.get("response", "").strip(),
#                 "model": MODEL,
#                 "success": True,
#             }
#         else:
#             return {
#                 "answer": "I'm having trouble connecting to the AI model. Please ensure Ollama is running.",
#                 "success": False,
#             }

#     except requests.exceptions.ConnectionError:
#         return {
#             "answer": "The AI assistant is currently unavailable. Please start Ollama with 'ollama serve'.",
#             "success": False,
#         }
#     except Exception as e:
#         return {
#             "answer": "An error occurred while processing your question. Please try again.",
#             "success": False,
#         }


# def get_weather_summary(current_data: dict) -> str:
#     """Generate an auto-summary of current conditions using AI."""
#     question = (
#         "In 2-3 sentences, summarize the current weather conditions "
#         "and what someone should expect in the near future."
#     )
#     result = ask_weather_assistant(question, current_data)
#     return result.get("answer", "Summary unavailable.")


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
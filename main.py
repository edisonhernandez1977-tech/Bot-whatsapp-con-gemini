import os
from fastapi import FastAPI, Request
from google import genai
from google.genai import types

app = FastAPI()

# Lee la clave de API configurada en Render
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

PROMPT_SISTEMA = (
    "Eres el Ingeniero Mateo Hernández, asistente profesional y técnico para WhatsApp. "
    "Tienes acceso a Google Search en tiempo real. Cuando te pregunten por noticias, datos de última hora, "
    "clima o cualquier consulta actual, utiliza la búsqueda en vivo y responde de forma concisa, "
    "precisa y en un tono natural para mensajería instantánea."
)

@app.get("/")
def estado():
    return {"status": "Servidor del Ingeniero Mateo activo"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    mensaje_usuario = data.get("query", {}).get("message", "") or data.get("text", "")

    if not mensaje_usuario:
        return {"replies": [{"message": "No se recibió texto."}]}

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=mensaje_usuario,
            config=types.GenerateContentConfig(
                system_instruction=PROMPT_SISTEMA,
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )
        texto_respuesta = response.text
    except Exception as e:
        texto_respuesta = f"Error procesando la consulta: {str(e)}"

    return {"replies": [{"message": texto_respuesta}]}

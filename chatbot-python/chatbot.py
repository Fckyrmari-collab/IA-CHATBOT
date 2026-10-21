
import random
import re
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from iagenerativa import generar_respuestas

app = FastAPI(title="Chatbot básico - Shena", version="1.0.0")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: List[Dict[str, str]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str



def responder(mensaje: str) -> str:
    ruta_datos = Path(__file__).with_name("datos.txt")

    try:
        with open(ruta_datos, "r", encoding="utf-8") as archivo:
            datos = archivo.read().splitlines()
        print("Datos leídos")
    except FileNotFoundError:
        datos = []
        print("No se encontró el archivo datos.txt")

    modelo = {}

    for frase in datos:
        palabras = re.findall(r"\w+", frase.lower())

        for i in range(len(palabras) - 1):
            actual = palabras[i]
            siguiente = palabras[i + 1]

            if actual not in modelo:
                modelo[actual] = []

            modelo[actual].append(siguiente)

    print("\nModelo construido")

    for palabra, siguientes in modelo.items():
        print(palabra, "->", siguientes)

    texto = mensaje.strip().lower()

    if not texto:
        return "Por favor escribe un mensaje. No puedo responder a mensajes vacíos."

    if len(texto) < 2:
        return "¿Podrías escribir un mensaje más largo? Tu mensaje es muy corto."

    if any(saludo in texto for saludo in ("hola", "buenas", "hey")):
        return "¡Hola! Soy Shena, tu asistente virtual SENA. ¿En qué puedo ayudarte?"

    if "nombre" in texto:
        return "Soy Shena, un chatbot básico hecho con Python."

    if any(palabra in texto for palabra in ("adiós", "chao", "hasta luego")):
        return "¡Hasta luego! Que tengas un buen día."

    if "ayuda" in texto:
        return "Puedo responder preguntas sobre programas, inscripciones, contacto, requisitos y contratos de aprendizaje. ¿Qué necesitas?"

    if any(palabra in texto for palabra in ("oferta", "carreras", "cursos", "que hay", "qué hay", "programas", "estudiar")):
        return (
            "Las ofertas disponibles para estudiar son:\n"
            "Tecnólogo ADSO\n"
            "Multimedia\n"
            "Animación 3D\n"
            "Desarrollo de medios visuales\n"
            "Consulta la oferta vigente en https://betowa.sena.edu.co/"
        )

    if any(palabra in texto for palabra in ("inscripciones", "fechas", "fecha", "inicio")):
        return (
            "Consulta las fechas de inscripción y las convocatorias vigentes "
            "en https://betowa.sena.edu.co/"
        )

    if any(palabra in texto for palabra in ("contacto", "telefono", "teléfono", "datos", "correo")):
        return (
            "Información de contacto registrada:\n"
            "Nombre: Claudia Marcela Estupiñán Gómez\n"
            "Rol: Coordinadora grupo de Administración Administrativa\n"
            "Correo: cmestupinan@sena.edu.co\n"
            "Centro: Centro para la Industria de la Comunicación Gráfica\n"
            "Regional: Regional Distrito Capital\n"
            "Dirección: Calle 15 No. 31-42, Bogotá D.C., Colombia"
        )

    if "contrato" in texto:
        return (
            "Aquí puedes consultar información sobre el contrato de aprendizaje:\n"
            "https://comunicaciongraficasena.blogspot.com/p/contrato-de-aprendizaje.html"
        )

    if any(palabra in texto for palabra in ("requisitos", "papel", "documentos", "diploma")):
        return (
            "Los requisitos dependen del programa y la convocatoria. "
            "Consulta la información vigente en:\n"
            "https://betowa.sena.edu.co/"
        )

    palabras_usuario = re.findall(r"\w+", texto)

    palabras_vacias = {
        "que", "qué", "como", "cómo", "es", "el", "la", "los", "las",
        "un", "una", "del", "en", "y", "a", "me", "puedes", "dime",
        "sobre", "por", "favor", "de", "se", "mi", "tu"
    }

    candidatas = [
        palabra for palabra in palabras_usuario
        if palabra in modelo and palabra not in palabras_vacias
    ]

    if not candidatas:
        return (
            "No encuentro una palabra conocida en tu consulta.\n"
            "Prueba con aprendiz, estudiante, Python, Flask, React o MySQL."
        )

    actual = candidatas[-1]
    frase_generada = [actual]

    for _ in range(7):
        if actual not in modelo or not modelo[actual]:
            break

        siguiente = random.choice(modelo[actual])
        frase_generada.append(siguiente)
        actual = siguiente

    # devolver las respuesta

    respuesta = " ".join(frase_generada)

    print("\n=== RESPUESTA GENERADA ===")
    print(respuesta)

    return "Segun los patrones de mis datos: " + respuesta


@app.get("/", response_class=HTMLResponse)
def pagina() -> str:
    return HTML


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    respuesta = await generar_respuestas(request.message)

    return ChatResponse(reply=respuesta)



HTML = r"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Chatbot básico - Shena</title>
  <style>
    body { font: 16px system-ui, sans-serif; max-width: 680px; margin: 3rem auto; padding: 0 1rem; color: #202124; }
    #chat { min-height: 260px; border: 1px solid #ddd; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; }
    .message { margin: .6rem 0; white-space: pre-wrap; }
    form { display: flex; gap: .5rem; }
    input { flex: 1; padding: .8rem; border: 1px solid #aaa; border-radius: 8px; }
    button { padding: .8rem 1rem; border: 0; border-radius: 8px; background: #1459c7; color: white; cursor: pointer; }
  </style>
</head>
<body>
  <h1>Chatbot básico - Shena</h1>
  <div id="chat" aria-live="polite"><p class="message">Bot: ¡Hola! Escribe un mensaje para empezar.</p></div>
  <form id="form">
    <input id="message" autocomplete="off" placeholder="Escribe tu mensaje…" required maxlength="2000">
    <button type="submit">Enviar</button>
  </form>
  <script>
    const chat = document.querySelector('#chat');
    const form = document.querySelector('#form');
    const input = document.querySelector('#message');

    function addMessage(who, text) {
      const p = document.createElement('p');
      p.className = 'message';
      p.textContent = `${who}: ${text}`;
      chat.appendChild(p);
      chat.scrollTop = chat.scrollHeight;
    }

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const message = input.value.trim();
      if (!message) return;

      addMessage('Tú', message);
      input.value = '';

      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message })
        });

        if (!response.ok) throw new Error('No se pudo obtener una respuesta.');

        const data = await response.json();
        addMessage('Bot', data.reply);
      } catch (error) {
        addMessage('Bot', `Error: ${error.message}`);
      }
    });
  </script>
</body>
</html>"""

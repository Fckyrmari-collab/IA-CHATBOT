
import random
import re
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from iagenerativa import generar_respuestas

app = FastAPI(title="Chatbot básico - Sena", version="1.0.0")


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


@app.get("/")
def pagina():
    return FileResponse(Path(__file__).with_name("index.html"))


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    respuesta = await generar_respuestas(request.message)

    return ChatResponse(reply=respuesta)




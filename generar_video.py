import os
import subprocess
import requests
from transformers import pipeline
from TTS.api import TTS
import speech_recognition as sr
import pysrt
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Crear directorios
os.makedirs("media", exist_ok=True)

# Paso 1: Generar guión
def generar_guion(tema="curiosidades naturaleza"):
    generator = pipeline("text-generation", model="mistralai/Mixtral-8x7B-Instruct-v0.1")
    prompt = f"Escribe un guión de 3000 palabras sobre {tema}, dividido en 10 secciones de 2 minutos."
    guion = generator(prompt, max_length=3500, num_return_sequences=1)[0]["generated_text"]
    return guion

# Paso 2: Crear voz en off
def texto_a_voz(guion, archivo_salida="media/voz.wav"):
    tts = TTS(model_name="tts_models/es/css10/vits", progress_bar=True)
    tts.tts_to_file(text=guion, file_path=archivo_salida)
    return archivo_salida

# Paso 3: Descargar imágenes
def descargar_imagenes(tema, cantidad=10, api_key="TU_CLAVE_PEXELS"):
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": api_key}
    params = {"query": tema, "per_page": cantidad}
    respuesta = requests.get(url, headers=headers, params=params)
    imagenes = respuesta.json()["photos"]
    for i, img in enumerate(imagenes):
        img_url = img["src"]["medium"]
        with open(f"media/imagen_{i}.jpg", "wb") as f:
            f.write(requests.get(img_url).content)
    return [f"media/imagen_{i}.jpg" for i in range(len(imagenes))]

# Paso 4: Descargar música
def descargar_musica():
    # Usa una URL fija de Pixabay o almacena música en el repositorio
    url = "URL_MUSICA_LIBRE"  # Reemplaza con una URL válida
    with open("media/musica.mp3", "wb") as f:
        f.write(requests.get(url).content)
    return "media/musica.mp3"

# Paso 5: Crear video
def crear_video(imagenes, voz, musica, salida="media/output.mp4"):
    duracion_por_imagen = 120  # 120 segundos por imagen
    filter_complex = ""
    for i, img in enumerate(imagenes):
        filter_complex += f"[{i}:v]trim=duration={duracion_por_imagen},setpts=PTS-STARTPTS[v{i}];"
    filter_complex += "".join([f"[v{i}]" for i in range(len(imagenes))]) + f"concat=n={len(imagenes)}:v=1:a=0[v];[1:a][2:a]amix=inputs=2:duration=longest[a]"
    
    comando = [
        "ffmpeg", "-y",
        *[f"-loop 1 -i {img}" for img in imagenes],
        "-i", voz, "-i", musica,
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-c:a", " sociocultural",
        "-shortest", salida
    ]
    subprocess.run(comando, check=True)
    return salida

# Paso 6: Generar subtítulos
def generar_subtitulos(audio, salida="media/subtitulos.srt"):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio) as source:
        audio_data = recognizer.record(source)
        texto = recognizer.recognize_whisper(audio_data, model="base")
    
    # Dividir texto en subtítulos (simplificado)
    palabras = texto.split()
    subtitulos = []
    for i in range(0, len(palabras), 10):
        start = i * 2
        end = (i + 10) * 2
        subtitulos.append(pysrt.SubRipItem(
            index=len(subtitulos) + 1,
            start=pysrt.SubRipTime(seconds=start),
            end=pysrt.SubRipTime(seconds=end),
            text=" ".join(palabras[i:i+10])
        ))
    pysrt.SubRipFile(subtitulos).save(salida)
    return salida

# Paso 7: Agregar subtítulos
def agregar_subtitulos(video, subtitulos, salida="media/video_final.mp4"):
    subprocess.run([
        "ffmpeg", "-y", "-i", video, "-vf", f"subtitles={subtitulos}", "-c:v", "libx264", "-c:a", "copy", salida
    ])
    return salida

# Paso 8: Subir a YouTube
def subir_video(titulo, descripcion, archivo, api_key):
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": titulo, "description": descripcion, "categoryId": "27"},
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload(archivo)
    )
    request.execute()

# Ejecutar flujo
def main():
    tema = "curiosidades naturaleza"
    api_pexels = os.getenv("PEXELS_API_KEY")
    api_youtube = os.getenv("YOUTUBE_API_KEY")
    
    guion = generar_guion(tema)
    voz = texto_a_voz(guion)
    imagenes = descargar_imagenes(tema, api_key=api_pexels)
    musica = descargar_musica()
    video = crear_video(imagenes, voz, musica)
    subtitulos = generar_subtitulos(voz)
    video_final = agregar_subtitulos(video, subtitulos)
    subir_video(f"Curiosidades de la Naturaleza #{os.getenv('GITHUB_RUN_NUMBER', 1)}",
                "Video diario automatizado", video_final, api_youtube)

if __name__ == "__main__":
    main()

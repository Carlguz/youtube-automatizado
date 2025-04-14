import os
import subprocess
import requests
from transformers import pipeline
from TTS.api import TTS
import speech_recognition as sr
import pysrt

# Crear directorio temporal
os.makedirs("media", exist_ok=True)

# Paso 1: Generar guión
def generar_guion(tema="curiosidades naturaleza"):
    generator = pipeline("text-generation", model="mistralai/Mixtral-8x7B-Instruct-v0.1")
    prompt = f"Escribe un guión breve de 150 palabras sobre {tema} para un video de 1 minuto."
    guion = generator(prompt, max_length=200, num_return_sequences=1)[0]["generated_text"]
    return guion.strip()

# Paso 2: Crear voz en off
def texto_a_voz(guion, archivo_salida="media/voz.wav"):
    tts = TTS(model_name="tts_models/es/css10/vits", progress_bar=True)
    tts.tts_to_file(text=guion, file_path=archivo_salida)
    return archivo_salida

# Paso 3: Descargar imágenes (Unsplash Source, sin API)
def descargar_imagenes(tema="nature", cantidad=3):
    imagenes = []
    for i in range(cantidad):
        url = f"https://source.unsplash.com/1920x1080/?{tema}&sig={i}"
        archivo = f"media/imagen_{i}.jpg"
        try:
            respuesta = requests.get(url, stream=True, timeout=10)
            if respuesta.status_code == 200:
                with open(archivo, "wb") as f:
                    f.write(respuesta.content)
                imagenes.append(archivo)
            else:
                raise Exception("Error al descargar")
        except Exception as e:
            print(f"Error en imagen {i}: {e}")
            # Fallback: Imagen negra
            subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=1920x1080:d=20", "-c:v", "libx264", archivo])
            imagenes.append(archivo)
    return imagenes

# Paso 4: Obtener música
def obtener_musica():
    # URL pública de música libre (Pixabay, reemplaza con una válida)
    url = "https://cdn.pixabay.com/audio/2022/03/15/audio_1a2b3c4d5e.mp3"  # Cambia por una pista real
    archivo = "media/musica.mp3"
    try:
        respuesta = requests.get(url, stream=True, timeout=10)
        if respuesta.status_code == 200:
            with open(archivo, "wb") as f:
                f.write(respuesta.content)
            return archivo
    except Exception:
        # Fallback: Silencio
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100", "-t", "60", archivo])
        return archivo

# Paso 5: Crear video
def crear_video(imagenes, voz, musica, salida="media/output.mp4"):
    duracion_por_imagen = 20  # 20 segundos por imagen (1 min / 3)
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
        "-c:v", "libx264", "-c:a", "aac",
        "-shortest", salida
    ]
    subprocess.run(comando, check=True)
    return salida

# Paso 6: Generar subtítulos
def generar_subtitulos(audio, salida="media/subtitulos.srt"):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio) as source:
        audio_data = recognizer.record(source)
        texto = recognizer.recognize_whisper(audio_data, model="tiny")
    
    # Subtítulos simplificados
    palabras = texto.split()
    subtitulos = []
    for i in range(0, len(palabras), 5):
        start = i * 0.5
        end = min((i + 5) * 0.5, 60)
        subtitulos.append(pysrt.SubRipItem(
            index=len(subtitulos) + 1,
            start=pysrt.SubRipTime(seconds=start),
            end=pysrt.SubRipTime(seconds=end),
            text=" ".join(palabras[i:i+5])
        ))
    pysrt.SubRipFile(subtitulos).save(salida)
    return salida

# Paso 7: Agregar subtítulos
def agregar_subtitulos(video, subtitulos, salida="media/video_final.mp4"):
    subprocess.run([
        "ffmpeg", "-y", "-i", video, "-vf", f"subtitles={subtitulos}", "-c:v", "libx264", "-c:a", "copy", salida
    ])
    return salida

# Flujo principal
def main():
    tema = "nature"
    guion = generar_guion(tema)
    voz = texto_a_voz(guion)
    imagenes = descargar_imagenes(tema)
    musica = obtener_musica()
    video = crear_video(imagenes, voz, musica)
    subtitulos = generar_subtitulos(voz)
    video_final = agregar_subtitulos(video, subtitulos)
    print(f"Video generado: {video_final}")

if __name__ == "__main__":
    main()

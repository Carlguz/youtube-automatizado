import os
from moviepy.editor import *

# Imágenes de fondo
image = ImageClip("assets/images/bg.jpg", duration=30)

# Audio generado
audio = AudioFileClip("output/audio.mp3")

# Música de fondo
music = AudioFileClip("assets/music/music.mp3").volumex(0.2)

# Combinar audios
final_audio = CompositeAudioClip([audio, music])

# Crear video final
video = image.set_audio(final_audio)
video.write_videofile("output/final_video.mp4", fps=24)

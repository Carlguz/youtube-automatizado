from moviepy.editor import *

# Cargar imagen de fondo
img = ImageClip("assets/images/bg.jpg", duration=10)

# Cargar audio principal
audio = AudioFileClip("output/audio.mp3")

# Música de fondo opcional
music = AudioFileClip("assets/music/music.mp3").volumex(0.1)

# Mezclar música de fondo con voz en off
final_audio = CompositeAudioClip([audio, music])

# Montar video
video = img.set_audio(final_audio)
video.write_videofile("output/final_video.mp4", fps=24)

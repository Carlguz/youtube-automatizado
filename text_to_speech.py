from gtts import gTTS

with open("output/script.txt", "r") as f:
    text = f.read()

tts = gTTS(text=text, lang='es')
tts.save("output/audio.mp3")


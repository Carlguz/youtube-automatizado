from gtts import gTTS
text = open("output/script.txt").read()

tts = gTTS(text=text, lang='es')
tts.save("output/audio.mp3")

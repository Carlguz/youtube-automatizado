import whisper
model = whisper.load_model("base")
result = model.transcribe("output/audio.mp3")

with open("output/subtitles.srt", "w") as f:
    f.write(result["text"])

# Por ahora genera subtítulo como texto plano
with open("output/script.txt", "r") as f:
    text = f.read()

with open("output/subtitles.srt", "w") as f:
    f.write("00:00:00,000 --> 00:00:10,000\n")
    f.write(text)

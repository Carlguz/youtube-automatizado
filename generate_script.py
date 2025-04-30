import openai

with open('input/topics.txt', 'r') as f:
    topic = f.readline().strip()

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": f"Escribe un guion de 300 palabras sobre {topic}."}]
)

script = response.choices[0].message.content

with open("output/script.txt", "w") as f:
    f.write(script)

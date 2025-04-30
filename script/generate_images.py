import requests

# Imagen relacionada al tema de las abejas
url = "https://source.unsplash.com/1280x720/?bee,honey"

response = requests.get(url)
with open("assets/images/bg.jpg", "wb") as f:
    f.write(response.content)

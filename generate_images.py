import requests

topic = open("input/topics.txt").read().strip()
img_url = f"https://source.unsplash.com/1280x720/?{topic}"
img_data = requests.get(img_url).content

with open("assets/images/bg.jpg", "wb") as f:
    f.write(img_data)

# Adapted from OpenAI's Vision example 
from openai import OpenAI
import base64
import requests

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

# Ask the user for a path on the filesystem:
# path = input("Enter a local filepath to an image: ")

path = "erreur.jpg"
# Read the image and encode it to base64:
base64_image = ""
try:
  image = open(path.replace("'", ""), "rb").read()
  base64_image = base64.b64encode(image).decode("utf-8")
except:
  print("Couldn't read the image. Make sure the path is correct and the file exists.")
  exit()

completion = client.chat.completions.create(
  model="local-model", # not used
  messages=[
    {
      "role": "system",
      "content": "Vous êtes un ingénieur construction qui analyse des images.",
    },
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Lister les non conformités sur cette image ?"},
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
          },
        },
      ],
    }
  ],
  max_tokens=1000,
  stream=True
)

for chunk in completion:
  if chunk.choices[0].delta.content:
    print(chunk.choices[0].delta.content, end="", flush=True)
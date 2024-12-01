# Chat with an intelligent assistant in your terminal
import json
from openai import OpenAI

gray_color = "\033[90m"
blue_color = "\033[93m"
reset_color = "\033[0m"
    
# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

history = [
    {"role": "system", "content": "Vous êtes un ingénieur assistant français. Réponsez à mes Questions en français, de manière concise et en tenant compte de l'Historique de la conversations"},
    {"role": "user", "content": "Salut, présente toi en deux phrases comme tu le ferais à quelqu'un qui ouvre ce programme pour la première fois."},
]

while True:
    completion = client.chat.completions.create(
        model="local-model", # this field is currently unused
        messages=history,
        temperature=0.7,
        stream=True,
    )

    new_message = {"role": "assistant", "content": ""}
    print(f"{blue_color}")
    for chunk in completion:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            new_message["content"] += chunk.choices[0].delta.content
    print(f"{reset_color}")
    history.append(new_message)
    
    
    """print(f"{gray_color}\n{'-'*20} History dump {'-'*20}\n")
    print(json.dumps(history, indent=2))
    print(f"\n{'-'*55}\n{reset_color}")
"""
    print()
    q=input("> ")
    #print(f"{blue_color}\n {q}\n{reset_color}")
    
    history.append({"role": "user", "content": q})
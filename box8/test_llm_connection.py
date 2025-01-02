if False:
    # marche bien
    from openai import OpenAI
    client = OpenAI(
        base_url="https://3376i2qt2in9ep-8000.proxy.runpod.net/v1",
        api_key="token-abc123",
    )

    completion = client.chat.completions.create(
    model="cognitivecomputations/dolphin-2.9-llama3-8b",
    messages=[
        {"role": "user", "content": "Who is Victor Hugo? Summarize his life and works."}
    ]
    )

    print(completion.choices[0].message.content)







    
if False:
    import requests

    # URL du serveur vLLM
    base_url = "https://3376i2qt2in9ep-8000.proxy.runpod.net/v1/completions"

    # Corps de la requête
    payload = {
        "prompt": "Who is Victor Hugo? Summarize his life and works.",
        "max_tokens": 100,  # Remplacez par la limite de tokens souhaitée
        "temperature": 0.7  # Valeur entre 0 et 1 pour le contrôle de la créativité
    }

    headers = {"Content-Type": "application/json"}

    # Envoyer la requête
    response = requests.post(base_url, json=payload, headers=headers)

    # Afficher les résultats
    if response.status_code == 200:
        print("Réponse du serveur :", response.json())
    else:
        print(f"Erreur {response.status_code}: {response.text}")







if True:
    from crewai import Agent, LLM, Task, Crew
    from CrewAIFunctions import ChooseLLM


    agent = Agent(
        role='Customized LLM Expert',
        goal='Provide tailored responses',
        backstory="An AI assistant with custom LLM settings.",
        llm=ChooseLLM("hosted"),
        verbose=True
    )
    task = Task(
        description="Who is François Mitterand ? Give me a summary of his life and work",
        expected_output="A response",
        agent = agent
    )

    crew = Crew(
        agents=[agent],
        tasks=[task]
    )
    response = crew.kickoff()
    print(response.raw)





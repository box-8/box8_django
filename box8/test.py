import json
import os
from crewai import Agent, Crew, Process, Task, LLM
from box8.CrewAIFunctions import (choose_tool, ChooseLLM,resetChroma)
from box8.utils_pdf import (extractPageTextFromFile)

def determine_branches_and_nodes(data):
    nodes = {node['key']: node for node in data['nodes']}
    links = data['links']

    branches = []
    visited = set()

    def dfs(current_node, path):
        if current_node in visited:
            return
        visited.add(current_node)
        path.append(current_node)

        # Find all nodes connected from the current node
        connected_nodes = [link['to'] for link in links if link['from'] == current_node]
        if not connected_nodes:
            branches.append(list(path))
        else:
            for next_node in connected_nodes:
                dfs(next_node, path)

        path.pop()
        visited.remove(current_node)

    # Identify nodes with multiple incoming links
    incoming_links = {node_key: 0 for node_key in nodes.keys()}
    for link in links:
        incoming_links[link['to']] += 1

    # Nodes with multiple incoming links
    multi_incoming_nodes = {node_key for node_key, count in incoming_links.items() if count > 1}

    # Start DFS from every node that is not a destination in any link (potential root nodes)
    potential_roots = set(nodes.keys()) - {link['to'] for link in links}
    for root in potential_roots:
        dfs(root, [])

    # Map branches to their corresponding nodes
    branch_details = []
    for branch in branches:
        branch_nodes = [nodes[node_key] for node_key in branch]
        branch_details.append(branch_nodes)

    return branch_details, multi_incoming_nodes



# launch process 
def crewai_launch_process2(request, folder, llm="openai"):
    Verbose = False
    resetChroma()
    try:
        data = json.loads(request.body)
        branches, multi_incoming_nodes = determine_branches_and_nodes(data)
        all_results = []

        agents_dict = {}
        for node in data['nodes']:
            agents_dict[node['key']] = Agent(
                role=node.get('role', ''),
                goal=node.get('goal', ''),
                backstory=node.get('backstory', ''),
                verbose=Verbose,
                llm=ChooseLLM(llm)
            )
            file = node.get('file', '')
            if file:
                src = os.path.join(folder, file)
                if os.path.exists(src):
                    agents_dict[node['key']].tools = [choose_tool(src=src)]
                    backstory_file = crewai_summarize_ifnotexists(pdf=src, llm=llm)
                    # print(f"Backstory for {node['role']}:\n\n{backstory_file}")
                    agents_dict[node['key']].backstory += f"""\n\nContexte du Fichier {file}: \n\n{backstory_file}"""
                    print(f"\033[93m Backstory for AGENT {node['role']}:\n\n{agents_dict[node['key']].backstory}\033[0m")

        for multi_node in multi_incoming_nodes:
            backstory_concat = ""

            for link in data['links']:
                if link['to'] == multi_node:
                    from_agent = agents_dict[link['from']]
                    to_agent = agents_dict[link['to']]

                    task = Task(
                        description=link['description'],
                        agent=from_agent,
                        expected_output=link.get('expected_output', ''),
                        tools=from_agent.tools
                    )
                    try:
                        crew = Crew(
                            agents=[from_agent],
                            tasks=[task]
                        )
                        print(f"Kickoff for link: {from_agent.role} -> {to_agent.role}")
                        print(f"{link['description']}")
                        kickoff_result = crew.kickoff()

                        backstory_concat += f"""\n\n{from_agent.role} :\n\n {kickoff_result.raw}"""
                        result = ""
                        result += f"\n\n***\n\n"
                        result += f"\n\n## {task.output.agent}\n\n"
                        result += f"\n\n### {task.output.description}\n\n"
                        result += f"\n\n{task.output.raw}\n\n"
                        #all_results.append(result)
                        # print(result)
                    except Exception as e:
                        print("Error in process: " + str(e))
                        continue
            
            agents_dict[multi_node].backstory += "\n\n Informations supplémentaires : "+backstory_concat
            print(f"\033[95m BACKSTORY FOR STAR AGENT {agents_dict[multi_node].role}:\n\n\033[0m")
            
            print(f"\033[94m{agents_dict[multi_node].backstory}\033[0m")

        for branch in branches:
            # all_results.append(result)
            tasks = []
            list_agents = []

            for i in range(len(branch) - 1):
                from_node = branch[i]
                to_node = branch[i + 1]
                
                link = next((link for link in data['links'] if link['from'] == from_node['key'] and link['to'] == to_node['key']), None)

                if link:
                    from_agent = agents_dict[from_node['key']]
                    to_agent = agents_dict[to_node['key']]

                    task = Task(
                        description=link['description'],
                        agent=from_agent,
                        expected_output=link.get('expected_output', ''),
                        tools=from_agent.tools
                    )

                    tasks.append(task)
                    list_agents.append(from_agent)
                    
            
            print("Kickoff for final branch")
            if tasks and list_agents:  # Vérifiez que les listes ne sont pas vides
                # print(list_agents[-1].backstory)
                crew = Crew(
                    agents=list_agents,
                    tasks=tasks
                )
                
                for agent in list_agents:
                    print(f"\033[95m Backstory for AGENT {agent.role}:\033[0m")
                    print(f"\033[96m \n\n{agent.backstory}\033[0m")
                    

                kickoff_result = crew.kickoff()
                result = ""
                for task in tasks:
                    result += f"\n\n***\n\n"
                    result += f"\n\n## {task.output.agent}\n\n"
                    result += f"\n\n### {task.output.description}\n\n"
                    result += f"\n\n{task.output.raw}\n\n"

                all_results.append(result)
            else:
                print("Skipping kickoff: No valid agents or tasks found.")

        return {
            'status': 'success',
            'message': "\n".join(all_results),
            'branches_count': len(branches)
        }

    except Exception as e:
        print("Error in process: " + str(e))
        return {
            'status': 'error',
            'message': str(e)
        }












# launch process 
def crewai_launch_process3(request, folder, llm="openai"):
    """
    Améliore la fonction pour traiter un diagramme en passant une seule fois par chaque noeud.
    """
    Verbose = False
    resetChroma()
    
    try:
        data = json.loads(request.body)
        branches, multi_incoming_nodes = determine_branches_and_nodes(data)
        all_results = []
        processed_nodes = set()  # Pour suivre les noeuds déjà visités
        
        # Initialisation des agents
        agents_dict = {}
        for node in data['nodes']:
            agents_dict[node['key']] = Agent(
                role=node.get('role', ''),
                goal=node.get('goal', ''),
                backstory=node.get('backstory', ''),
                verbose=Verbose,
                llm=ChooseLLM(llm)
            )
            file = node.get('file', '')
            if file:
                src = os.path.join(folder, file)
                if os.path.exists(src):
                    agents_dict[node['key']].tools = [choose_tool(src=src)]
                    backstory_file = crewai_summarize_ifnotexists(pdf=src, llm=llm)
                    agents_dict[node['key']].backstory += f"""\n\nContexte du Fichier {file}: \n\n{backstory_file}"""

        # Traitement des branches
        for branch in branches:
            tasks = []
            list_agents = []

            for i in range(len(branch) - 1):
                from_node = branch[i]
                to_node = branch[i + 1]

                if from_node['key'] in processed_nodes:
                    continue  # Passer si le noeud est déjà traité

                link = next((link for link in data['links'] if link['from'] == from_node['key'] and link['to'] == to_node['key']), None)
                
                if link:
                    from_agent = agents_dict[from_node['key']]
                    task = Task(
                        description=link['description'],
                        agent=from_agent,
                        expected_output=link.get('expected_output', ''),
                        tools=from_agent.tools
                    )

                    tasks.append(task)
                    list_agents.append(from_agent)
                    processed_nodes.add(from_node['key'])

            # Exécuter les tâches pour cette branche
            if tasks and list_agents:
                crew = Crew(
                    agents=list_agents,
                    tasks=tasks
                )
                try:
                    kickoff_result = crew.kickoff()
                    for task in tasks:
                        result = f"\n\n***\n\n"
                        result += f"\n\n## {task.output.agent}\n\n"
                        result += f"\n\n### {task.output.description}\n\n"
                        result += f"\n\n{task.output.raw}\n\n"
                        all_results.append(result)
                except Exception as e:
                    print(f"Error processing branch: {str(e)}")
                    continue

        # Traitement des noeuds avec plusieurs entrées (multi-incoming nodes)
        for multi_node in multi_incoming_nodes:
            upstream_chains = get_upstream_chain(multi_node, data)
            backstory_concat = ""

            for chain in upstream_chains:
                tasks = []
                list_agents = []

                for i in range(len(chain) - 1):
                    from_key = chain[i]
                    to_key = chain[i + 1]

                    if (from_key, to_key) in processed_nodes:
                        continue

                    link = next((link for link in data['links'] if link['from'] == from_key and link['to'] == to_key), None)

                    if link:
                        from_agent = agents_dict[from_key]
                        task = Task(
                            description=link['description'],
                            agent=from_agent,
                            expected_output=link.get('expected_output', ''),
                            tools=from_agent.tools
                        )
                        tasks.append(task)
                        list_agents.append(from_agent)
                        processed_nodes.add((from_key, to_key))

                # Exécuter les chaînes
                if tasks and list_agents:
                    crew = Crew(
                        agents=list_agents,
                        tasks=tasks
                    )
                    try:
                        kickoff_result = crew.kickoff()
                        for task in tasks:
                            backstory_concat += f"\n\n{task.output.agent} :\n\n {task.output.raw}"
                    except Exception as e:
                        print(f"Error processing chain: {str(e)}")
                        continue

            agents_dict[multi_node].backstory += "\n\n Informations supplémentaires : " + backstory_concat

        return {
            'status': 'success',
            'message': "\n".join(all_results),
            'branches_count': len(branches)
        }

    except Exception as e:
        print(f"Error in crewai_launch_process3: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


def get_upstream_chain(node_key, data, visited=None):
    if visited is None:
        visited = set()
    
    if node_key in visited:
        return []
    
    visited.add(node_key)
    chain = []
    
    # Find all incoming links to this node
    incoming_links = [link for link in data['links'] if link['to'] == node_key]
    
    for link in incoming_links:
        upstream_chains = get_upstream_chain(link['from'], data, visited.copy())
        for upstream_chain in upstream_chains:
            chain.append(upstream_chain + [node_key])
        if not upstream_chains:  # If this is a start node
            chain.append([link['from'], node_key])
    
    return chain











def reorder_agents(json_data):
    # Extraire les liens et les noeuds
    links = json_data['links']
    nodes = json_data['nodes']

    # Créer un dictionnaire pour les noeuds par clé
    node_dict = {node['key']: node for node in nodes}

    # Extraire l'ordre des clés dans les relations from/to
    # On commence par le premier "from" qui est le patient
    ordered_keys = []
    # Dictionnaire pour vérifier les relations existantes
    visited = set()

    # Ajouter toutes les clés "from" dans l'ordre des relations
    for link in links:
        from_key = link['from']
        if from_key not in visited:
            ordered_keys.append(from_key)
            visited.add(from_key)
        to_key = link['to']
        if to_key not in visited:
            ordered_keys.append(to_key)
            visited.add(to_key)

    # Ajouter la clé "output" à la fin
    if 'output' not in visited:
        ordered_keys.append('output')

    # Reorganiser les noeuds en suivant l'ordre des clés dans ordered_keys
    ordered_nodes = [node_dict[key] for key in ordered_keys]

    # Retourner le json avec les nodes réorganisés
    return {
        "nodes": ordered_nodes,
        "links": links
    }

# Exemple d'utilisation avec le JSON fourni
json_data = {
    "nodes": [
        {
            "key": "output",
            "role": "Output",
            "goal": "output",
            "category": "output"
        },
        {
            "role": "analyste médical 1",
            "goal": "analyser les résultats supérieurs aux valeurs normales de la première prise de sang",
            "backstory": "l'analyse médical est un spécialiste capable de déterminer les variables non conformes à la normale",
            "file": "MED\\analyses2023.pdf",
            "key": "1735053672917"
        },
        {
            "role": "patient",
            "goal": "connaitre mon état de santé",
            "backstory": "patient atteint d'une polykystose rénale",
            "file": "",
            "key": "1735053584475"
        },
        {
            "role": "analyste médical 2 ",
            "goal": "comparer l'évolution des résultats d'analyse",
            "backstory": "médecin expérimenté, l'analyste médical compare l'évolution des constantes médicales entre les deux analyses sanguines",
            "file": "MED\\analyses.pdf",
            "key": "1735053926157"
        },
        {
            "role": "médecin traitant",
            "goal": "produire un rapport d'évolution de la maladie",
            "backstory": "le médecin généraliste se sert des analyses précédentes pour déterminer une évolution à la maladie du patient",
            "file": "",
            "key": "1735054026456"
        }
    ],
    "links": [
        {
            "from": "1735053584475",
            "to": "1735053672917",
            "relationship": "",
            "description": "décrire ses symptomes à l'analyste médical 1",
            "expected_output": "une descrition des symptomes"
        },
        {
            "from": "1735053672917",
            "to": "1735053926157",
            "relationship": "",
            "description": "transmission des résultats de la première analyse",
            "expected_output": "une liste des analyses en dehors des standards en deux parties : les valeurs supérieures à la normale et les valeurs inférieures à la normale"
        },
        {
            "from": "1735053926157",
            "to": "1735054026456",
            "relationship": "",
            "description": "transmettre un comparatif de l'évolution des constantes d'analyse en dehors des standards",
            "expected_output": "une liste de chaque constante en dehors des standards avec commentaire de son évolution à la hausse ou à la baisse"
        },
        {
            "from": "1735054026456",
            "to": "output",
            "relationship": "",
            "description": "rapport d'évolution de la maladie",
            "expected_output": "un rapport rappellant les constantes vitales en dehors des standards, leur évolution et en conclusion des recommandations pour le suivi d'un traitement"
        }
    ]
}

# Appliquer la fonction
reordered_json = reorder_agents(json_data)
print(reordered_json)

import json
import os
from crewai import Agent, Crew, Process, Task, LLM
from box8.CrewAIFunctions import (choose_tool, ChooseLLM,resetChroma)
from box8.utils_pdf import (extractPageTextFromFile)

def crewai_summarize_ifnotexists(pdf, pages=6 , history=None, llm="openai"):
    
    txt_path = pdf + ".txt"
    if os.path.exists(txt_path):
        try:
            with open(txt_path, "r", encoding="utf-8") as file:
                content = file.read()  # Lire tout le contenu du fichier
            # print(f"Contenu du fichier :\n{content}")
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier : {e}")
    else:
        print(f"Le fichier {pdf} n'existe pas, on le génère.")
        content = crewai_summarize(pdf, pages=pages , history=history, llm=llm)
    return content



def crewai_summarize(pdf, pages=6, history=None, llm="openai"):
    print(llm)
    """
    Extrait des insights à partir d'un document PDF en utilisant CrewAI.

    Paramètres :
    - pdf (str) : Le chemin vers le fichier PDF à analyser.
    - pages (str) : nombre de pages.
    - llm (str) : Le modèle de langage à utiliser (par défaut, "openai").

    Retourne :
    - list : Une liste d'insights sous forme de tableau JSON.
    """
    firstpages = extractPageTextFromFile(src=pdf)
    # Prendre uniquement les 6 premières pages
    try:
        entier = int(pages)
    except ValueError:
        print("La chaîne ne peut pas être convertie en entier")
        entier = 6
        
    content = "\n".join(firstpages[:entier])

    # Définition des agents
    title_extractor = Agent(
        name="Title Extractor",
        role="Expert en identification de titres",
        goal="Identifier le titre du document",
        backstory=f"""
            Un spécialiste dans l'identification rapide de titres et de sujets principaux 
            à partir d'extraits de documents textuels.""",
        llm=ChooseLLM(llm)
    )

    author_audience_extractor = Agent(
        name="Author and Audience Extractor",
        role="Expert en analyse d'auteur et de public cible",
        goal="Identifier qui a écrit le document et à qui il est adressé",
        backstory="""
            Un analyste expérimenté capable de déduire l'auteur et le public cible 
            d'un texte en étudiant le style et le contenu.""",
        llm=ChooseLLM(llm)
    )

    subject_purpose_extractor = Agent(
        name="Subject and Purpose Extractor",
        role="Expert en analyse de contenu",
        goal="Déterminer le sujet du document et son but",
        backstory="""
            Un expert en compréhension et analyse de texte, capable de résumer 
            les thèmes principaux et les objectifs sous-jacents d'un document.""",
        llm=ChooseLLM(llm)
    )

    # Définition des tâches
    title_task = Task(
        name="Extraction du titre",
        agent=title_extractor,
        description=f"""
            À partir du texte suivant, identifie le titre du document :
            {content}""",
        expected_output="Le titre du document."
    )

    author_audience_task = Task(
        name="Identification de l'auteur et du public cible",
        agent=author_audience_extractor,
        description=f"""
            En te basant sur le texte suivant, détermine qui a écrit le document 
            et à quel public il s'adresse :
            {content}""",
        expected_output="L'auteur du document et le public cible."
    )

    subject_purpose_task = Task(
        name="Analyse du sujet et du but",
        agent=subject_purpose_extractor,
        description=f"""
            Analyse le texte suivant pour déterminer le sujet du document et son objectif :
            {content}""",
        expected_output="Le sujet et le but du document avec un titre des sous titres les informations clefs (chiffres conclusions) et structuré au format markdown."
    )

    # Création de l'équipe CrewAI
    crew = Crew(
        agents=[title_extractor, author_audience_extractor, subject_purpose_extractor],
        tasks=[title_task, author_audience_task, subject_purpose_task]
    )

    # Exécution des tâches par les agents
    result = crew.kickoff()
    summary = result.raw
    return summary




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




def crewai_launch_process(request, folder, llm="openai"):
    return execute_process_from_diagram(request, folder, llm=llm)



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










import networkx as nx
def execute_process_from_diagram(request, folder, llm="openai"):
    """
    Exécute un processus basé sur un diagramme de tâches et d'agents en respectant l'ordre hiérarchique
    des tâches à effectuer grâce à un tri topologique.

    Arguments :
    - request : Requête contenant les données JSON décrivant les nœuds et les liens du diagramme.
    - folder : Répertoire contenant les fichiers associés aux agents.
    - llm : Modèle de langage à utiliser pour les agents.

    Retourne :
    - Un dictionnaire contenant le statut, le message des résultats et le nombre de branches traitées.
    """

    resetChroma()

    try:
        data = json.loads(request.body)
        nodes = {node['key']: node for node in data['nodes']}
        links = data['links']

        agents_dict = {}
        all_results = []

        # Initialiser les agents
        for node in data['nodes']:
            agents_dict[node['key']] = Agent(
                role=node.get('role', ''),
                goal=node.get('goal', ''),
                backstory=node.get('backstory', ''),
                llm=ChooseLLM(llm)
            )
            file = node.get('file', '')
            if file:
                src = os.path.join(folder, file)
                if os.path.exists(src):
                    agents_dict[node['key']].tools = [choose_tool(src=src)]
                    backstory = crewai_summarize_ifnotexists(pdf=src, llm=llm)
                    agents_dict[node['key']].backstory += f"\n\nContexte du fichier {file} :\n{backstory}"

        # Construire le graphe des tâches
        task_graph = nx.DiGraph()
        for link in links:
            task_graph.add_edge(link['from'], link['to'], description=link.get('description', 'Effectuer une tâche'), expected_output=link.get('expected_output', ''))

        # Effectuer un tri topologique pour déterminer l'ordre des tâches
        try:
            task_order = list(nx.topological_sort(task_graph))
        except nx.NetworkXUnfeasible:
            return {
                'status': 'error',
                'message': 'Le graphe contient des cycles, impossible de déterminer un ordre des tâches.'
            }
        # Trouver les noeuds de depart
        roots = [node for node in task_graph.nodes if task_graph.in_degree(node) == 0]


        # Exécuter les tâches dans l'ordre déterminé par le tri topologique
        for node_key in task_order:
            current_node = nodes[node_key]
            outgoing_links = task_graph.out_edges(node_key, data=True)

            for from_key, to_key, link_data in outgoing_links:
                from_agent = agents_dict[from_key]
                to_agent = agents_dict[to_key]

                task = Task(
                    description=link_data['description'],
                    agent=from_agent,
                    expected_output=link_data.get('expected_output', ''),
                    tools=from_agent.tools
                )

                try:
                    crew = Crew(agents=[from_agent], tasks=[task])
                    kickoff = crew.kickoff()

                    result = f"\n\n***\n\n"
                    result += f"\n\n## {task.output.agent}\n\n"
                    result += f"\n\n### {task.output.description}\n\n"
                    result += f"\n\n{task.output.raw}\n\n"
                    to_agent.backstory += f"\n\nRésultat de {from_agent.role} : {task.output.raw}"
                    #result += f"\n\n<small><i>{from_agent.backstory}</i></small>\n\n"
                    all_results.append(result)
                    print(result)
                    print(f"{from_agent.backstory}")

                except Exception as e:
                    print(f"Erreur lors de l'exécution de la tâche : {str(e)}")

        return {
            'status': 'success',
            'message': "\n".join(all_results),
            'branches_count': len(roots)
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }











def crewai_launch_process_old(request, folder, llm="openai"):
    anyTask = True
    Verbose = True
    try:
        print(llm)
        data = json.loads(request.body)

        branches, multi_incoming_nodes = determine_branches_and_nodes(data)
        all_results = []

        # Print all branches and their nodes
        print("All branches and their nodes:")
        for i, branch in enumerate(branches):
            print(f"Branch {i + 1}:")
            for node in branch:
                print(f"  Node {node['key']}: {node['role']}")

        # Kickoff branches leading to nodes with multiple incoming links
        """for branch in branches:
            if any(node['key'] in multi_incoming_nodes for node in branch):
                print(f"Kickoff for branch leading to multi-incoming node: {branch}")"""

        for branch in branches:
            agents = {}
            tasks = []
            
            for node in branch:
                role = node.get('role', '')
                key = node.get('key', '')
                
            
                print(f"New Agent : {role}")
                file = node.get('file', '')
                src = os.path.join(folder, file) if file else ""
                agent = Agent(
                    role=role,
                    goal=node.get('goal', ''),
                    backstory=node.get('backstory', ''),
                    allow_delegation=False,
                    verbose=Verbose,
                    llm=ChooseLLM(llm)
                )
                print(f"File : {src}")

                if os.path.exists(src) and file != "":
                    agent.tools = [choose_tool(src=src)]
                    

                agents[node.get('key')] = agent

            for link in data['links']:
                if link['from'] in agents and link['to'] in agents:
                    from_agent = agents[link['from']]
                    print(f"New Task {link['description']} : {agents[link['from']].role } -> {agents[link['to']].role}")
                    tasks.append(Task(
                        description=link['description'],
                        agent=from_agent,
                        expected_output=link.get('expected_output', ''),
                        tools=from_agent.tools,
                    ))


            listAgents = list(agents.values())[:-1]  # Exclude the last agent
            
            crew = Crew(
                agents=listAgents,
                tasks=tasks
            )
            print("Kickoff")
            # print(listAgents)
            # print(tasks)
            kickoff = crew.kickoff()
            result = """
            \n\n\n***
            """
            


            if anyTask:
                for task in tasks:
                    result += f"\n\n***\n\n"
                    result += f"\n\n## {task.output.agent}\n\n"
                    result += f"\n\n### {task.output.description}\n\n"
                    result += f"\n\n{task.output.raw}\n\n"
                    if Verbose:
                        print(f"\n\n\n----------------------------------------------------")
                        print(f"Task Agent: {task.output.agent}")
                        print(f"{task.output.description}")
                        print(f" - - - ")
                        print(f"{task.output.raw}")
            else:
                result += kickoff.raw
            
            all_results.append(result)

        return {
            'status': 'success',
            'message': "\n".join(all_results),
            'branches_count': len(branches)
        }

    except Exception as e:
        print("error in kickoff_for_branches: " + str(e))
        return {
            'status': 'error',
            'message': "ERROR " + str(e)
        }

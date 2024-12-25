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

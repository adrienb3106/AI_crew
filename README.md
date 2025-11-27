# My AI Team

## Description

My AI Team est une application Python qui utilise la puissance des grands modèles de langage (LLM) pour automatiser les processus de génération et de revue de code. Elle s'appuie sur le framework `crewai` pour orchestrer une équipe d'agents IA, chacun ayant un rôle spécifique (Manager, Développeur, Réviseur), afin de collaborer sur une tâche de programmation donnée.

Le projet est conçu pour être hautement configurable et extensible. L'objectif du projet, les rôles des agents et les modèles utilisés peuvent tous être personnalisés via de simples fichiers de configuration JSON.

## Fonctionnalités

- **Génération de code automatisée** : Laissez une équipe d'IA écrire du code Python en fonction de vos objectifs de projet.
- **Processus hiérarchique** : Un agent manager délègue les tâches à un développeur et à un réviseur, garantissant un flux de travail structuré.
- **Configurable** : Modifiez facilement l'objectif du projet, les backstories des agents et les modèles LLM via des fichiers JSON.
- **Extensible** : La structure du projet permet d'ajouter facilement de nouveaux agents, tâches ou outils.
- **Codebase modulaire** : Le code est organisé en modules logiques pour une meilleure lisibilité et maintenance.

## Structure du projet

```
.
├── .gitignore         # Spécifie les fichiers à ignorer par Git
├── agents.py          # Définit les agents IA pour l'équipe
├── config.json        # Configuration pour les modèles LLM
├── context.json       # Configuration pour l'objectif du projet et les rôles des agents
├── main_crew.py       # Script principal pour lancer l'équipe IA
├── README.md          # Ce fichier
├── requirements.txt   # Dépendances Python
├── results/           # Répertoire où les fichiers de sortie sont sauvegardés
└── utils.py           # Fonctions utilitaires utilisées par le script principal
```

## Configuration

Avant de lancer l'application, vous devez configurer les fichiers de configuration.

### 1. Variables d'environnement (`.env`)

Créez un fichier `.env` à la racine du projet et ajoutez vos clés API pour les fournisseurs de LLM. Vous avez besoin d'au moins une des clés suivantes :

```
OPENAI_API_KEY="votre-clé-api-openai"
ANTHROPIC_API_KEY="votre-clé-api-anthropic"
GEMINI_API_KEY="votre-clé-api-gemini"
```

### 2. Configuration du modèle (`config.json`)

Ce fichier spécifie les modèles LLM à utiliser. Vous pouvez y ajouter des commentaires pour expliquer chaque élément.

- `mini_model_name`: Ce modèle est utilisé pour les tâches de base par souci d'économie.
- `smart_model_name`: Ce modèle est utilisé pour les tâches plus complexes.

**Exemple `config.json`:**

```json
{
    "llm_config": {
        "mini_model_name": "gpt-4o-mini",
        "smart_model_name": "gpt-4o"
    }
}
```

### 3. Configuration du contexte (`context.json`)

Ce fichier définit l'objectif global du projet ainsi que les rôles et backstories spécifiques de chaque agent IA. Vous pouvez également y ajouter des commentaires.

- `project_goal`: Une description claire et concise de ce que le script final doit accomplir.
- `agents`: Un objet contenant la configuration pour chaque agent.

**Exemple `context.json`:**

```json
{
    "project_goal": "Développer un script Python de niveau production, performant et sécurisé...",
    "agents": {
        "manager": {
            "role": "Chef de Projet (Project Manager)",
            "goal": "Coordonner l'équipe pour produire le code...",
            "backstory": "Tu es le garant du budget et de la qualité finale du produit..."
        }
    }
}
```

## Comment ajouter et configurer un agent

Le code fourni est un exemple avec une équipe de trois agents (Manager, Développeur, Réviseur). Vous pouvez facilement le modifier pour ajouter, supprimer ou adapter des agents à vos besoins.

### 1. Mettre à jour `context.json`

Pour chaque nouvel agent, ajoutez une entrée dans la section `agents` de `context.json`. Définissez son `role`, son `goal` (objectif) et son `backstory` (histoire/contexte).

**Exemple : Ajout d'un agent "Architecte"**

```json
"architect": {
    "role": "Architecte Logiciel",
    "goal": "Concevoir l'architecture globale du projet et s'assurer qu'elle est évolutive et robuste.",
    "backstory": "Tu es un architecte expérimenté, obsédé par les design patterns et les bonnes pratiques."
}
```

### 2. Créer l'agent dans `agents.py`

Dans le fichier `agents.py`, utilisez la fonction `create_agents` pour instancier votre nouvel agent.

- Récupérez le contexte de l'agent depuis le dictionnaire `context`.
- Créez une instance de la classe `Agent` en utilisant les informations du `context.json`.
- Choisissez le modèle LLM (`llm_mini` ou `llm_smart`) et les outils (`tools`) appropriés pour cet agent.
- Ajoutez le nouvel agent au dictionnaire retourné par la fonction.

**Exemple : Instanciation de l'agent "Architecte"**

```python
# agents.py

from crewai import Agent

def create_agents(llm_mini, llm_smart, coding_tools, context):
    # ... (code des autres agents)

    # Ajout de l'agent Architecte
    architect_context = context['agents']['architect']
    architect_agent = Agent(
        role=architect_context['role'],
        goal=architect_context['goal'],
        backstory=architect_context['backstory'],
        verbose=True,
        allow_delegation=False,
        llm=llm_smart  # Utiliser le modèle puissant pour la conception
    )

    return {
        'manager': manager_agent,
        'developer': dev_agent,
        'review': review_agent,
        'architect': architect_agent  # Ne pas oublier de l'ajouter ici
    }
```

### 3. Intégrer l'agent dans le `main_crew.py`

Enfin, intégrez le nouvel agent dans le flux de travail principal dans `main_crew.py`.

- Récupérez l'instance de l'agent depuis le dictionnaire retourné par `create_agents`.
- Ajoutez l'agent à la liste des agents de votre `Crew`.
- Définissez et assignez des tâches (`Task`) spécifiques pour ce nouvel agent.

**Exemple : Intégration dans le `Crew`**
```python
# main_crew.py

# ... (importations et configuration)

def main():
    # ... (chargement des configurations)

    agents_dict = create_agents(llm_mini, llm_smart, coding_tools, context)
    manager_agent = agents_dict['manager']
    dev_agent = agents_dict['developer']
    review_agent = agents_dict['review']
    architect_agent = agents_dict['architect'] # Récupérer l'agent

    # Définir une tâche pour l'architecte
    design_task = Task(
        description="Concevoir l'architecture du projet en suivant les meilleures pratiques.",
        expected_output="Un document décrivant l'architecture proposée.",
        agent=architect_agent
    )

    # Mettre à jour la définition des tâches pour inclure le résultat de l'architecte
    tasks = define_tasks(dev_agent, review_agent, context={'design_document': design_task})

    my_team = Crew(
        agents=[architect_agent, dev_agent, review_agent], # Ajouter l'agent à l'équipe
        tasks=[design_task] + tasks, # Ajouter sa tâche
        # ... (reste de la configuration du Crew)
    )

    # ... (lancement du crew)
```

## Installation

1.  Clonez le dépôt :
    ```bash
    git clone <URL-du-repo>
    cd my-ai-team
    ```

2.  Créez un environnement virtuel et activez-le :
    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur Windows, utilisez `venv\Scripts\activate`
    ```

3.  Installez les dépendances requises :
    ```bash
    pip install -r requirements.txt
    ```

## Utilisation

Pour lancer l'équipe d'IA, exécutez simplement le script principal :

```bash
python main_crew.py
```

Le script initialisera les agents et les tâches, et l'équipe commencera à travailler sur l'objectif du projet. Le résultat final sera sauvegardé dans le répertoire `results`.

## Référence des fonctions (`utils.py`)

---

### `load_json_file(file_path)`

-   **Description**: Charge un fichier JSON à partir du chemin donné et retourne son contenu sous forme de dictionnaire Python.
-   **Paramètres**:
    -   `file_path` (str): Le chemin vers le fichier JSON.
-   **Retourne**: `dict`: Le contenu du fichier JSON.
-   **Quitte**: Si le fichier n'est pas trouvé ou si le fichier n'est pas un JSON valide.

---

### `check_api_keys()`

-   **Description**: Vérifie la présence des clés API nécessaires dans les variables d'environnement.
-   **Paramètres**: Aucun.
-   **Retourne**: Rien.
-   **Quitte**: Si aucune clé API n'est trouvée.

---

### `setup_llms(config)`

-   **Description**: Initialise et retourne les modèles LLM en fonction de la configuration fournie.
-   **Paramètres**:
    -   `config` (dict): Le dictionnaire de configuration chargé depuis `config.json`.
-   **Retourne**: `tuple`: Un tuple contenant les modèles `llm_mini` et `llm_smart`.

---

### `setup_output_directory(dir_name="results")`

-   **Description**: S'assure que le répertoire de sortie existe. S'il n'existe pas, il le crée.
-   **Paramètres**:
    -   `dir_name` (str, optionnel): Le nom du répertoire de sortie. Par défaut, `"results"`.
-   **Retourne**: `str`: Le nom du répertoire de sortie.

---

### `setup_tools(output_dir)`

-   **Description**: Crée et retourne une liste d'outils que les agents peuvent utiliser. Dans cet exemple, il s'agit d'outils pour lire et écrire des fichiers.
-   **Paramètres**:
    -   `output_dir` (str): Le répertoire où les outils doivent lire et écrire.
-   **Retourne**: `list`: Une liste d'instances d'outils.

---

### `define_tasks(dev_agent, review_agent)`

-   **Description**: Définit les tâches pour les agents développeur et réviseur.
-   **Paramètres**:
    -   `dev_agent` (Agent): L'instance de l'agent développeur.
    -   `review_agent` (Agent): L'instance de l'agent réviseur.
-   **Retourne**: `list`: Une liste d'instances de `Task`.
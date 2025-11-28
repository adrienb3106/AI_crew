# utils.py

import os
import json
from crewai import Task, LLM
from crewai_tools import FileWriterTool, FileReadTool

from exceptions import ConfigurationError, MissingAPIKeyError

def load_json_file(file_path):
    """Charge un fichier JSON et retourne son contenu."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ConfigurationError(f"Fichier de configuration '{file_path}' introuvable.")
    except json.JSONDecodeError:
        raise ConfigurationError(f"Le fichier '{file_path}' n'est pas un JSON valide.")

def check_api_keys():
    """Vérifie la présence des clés API nécessaires."""
    if not any(os.getenv(key) for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]):
        raise MissingAPIKeyError(
            "Aucune clé API de modèle (OpenAI, Anthropic, Gemini) n'a été trouvée. "
            "Veuillez définir au moins l'une d'elles dans votre fichier .env."
        )

def setup_llms(config):
    """Initialise et retourne les modèles LLM."""
    print("Initialisation des modèles LLM (Mode Production)...")
    llm_mini = LLM(model=config['llm_config']['mini_model_name'])
    llm_smart = LLM(model=config['llm_config']['smart_model_name'])
    return llm_mini, llm_smart

def setup_output_directory(dir_name="results"):
    """Assure que le répertoire de sortie existe."""
    os.makedirs(dir_name, exist_ok=True)
    print(f"Répertoire de sortie assuré : '{dir_name}'")
    return dir_name

def setup_tools(output_dir):
    """Crée et retourne les outils de manipulation de fichiers."""
    return [
        FileWriterTool(root_dir=output_dir),
        FileReadTool(root_dir=output_dir)
    ]

def define_tasks(dev_agent, review_agent):
    """Définit et retourne les tâches pour les agents."""
    task_dev = Task(
        description="""
        1. Crée un script Python simple basé sur le but du projet suivant : {project_goal}.
        2. Sauvegarde la première version dans 'v1_dev.py'.
        3. Si une version précédente existe (suite à une itération), applique les corrections demandées.
        """,
        expected_output="Un fichier 'v1_dev.py' contenant le code source fonctionnel et potentiellement corrigé.",
        agent=dev_agent
    )

    task_review = Task(
        description="""
        1. Lis le fichier 'v1_dev.py'.
        2. Vérifie la conformité au but du projet : {project_goal}. Ajoute la Docstrings en anglais et la gestion d'erreur (try/except).
        3. Si le code est parfait, le renommer en 'app_final.py'. Sinon, liste les corrections requises pour le Manager.
        """,
        expected_output="Un fichier 'app_final.py' ou une liste de corrections détaillées.",
        agent=review_agent,
        context=[task_dev]
    )
    return [task_dev, task_review]

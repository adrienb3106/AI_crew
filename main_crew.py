# main_crew.py

import os
import json
from dotenv import load_dotenv
from crewai import Task, Crew, Process, LLM
from crewai_tools import FileWriterTool, FileReadTool
from agents import create_agents 


# Chargement de la clé API
load_dotenv()

CONFIG_FILE = 'config.json'
try:
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        CONFIG = json.load(f)
    print(f" Configuration chargée : {CONFIG_FILE}")
except FileNotFoundError:
    print(f"ERREUR: Fichier de configuration '{CONFIG_FILE}' introuvable à la racine du projet.")
    exit()
except json.JSONDecodeError:
    print(f"ERREUR: Le fichier '{CONFIG_FILE}' n'est pas un JSON valide.")
    exit()


OPENAI_KEY_FOUND = os.getenv("OPENAI_API_KEY")
ANTHROPIC_KEY_FOUND = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_KEY_FOUND = os.getenv("GEMINI_API_KEY")

if not OPENAI_KEY_FOUND and not ANTHROPIC_KEY_FOUND and not GOOGLE_KEY_FOUND:
    print("FATAL ERROR : Aucune clé API de modèle (OpenAI, Anthropic, Gemini) n'a été trouvée.")
    print("Veuillez définir au moins l'une d'elles dans votre fichier .env.")
    exit()

# --- SETUP DES MODÈLES (LLM) EN MODE PRODUCTION ---
print("Initialisation des modèles LLM (Mode Production)...")
# Modèles réels pour la production
llm_mini = LLM(model=CONFIG['llm_config']['mini_model_name'])
llm_smart = LLM(model=CONFIG['llm_config']['smart_model_name'])

# --- CHARGEMENT DU FICHIER DE CONTEXTE ---
CONTEXT_FILE = 'context.json'
try:
    with open(CONTEXT_FILE, 'r', encoding='utf-8') as f:
        CONTEXT = json.load(f)
    print(f" Contexte chargé : {CONTEXT_FILE}")
except FileNotFoundError:
    print(f"ERREUR: Fichier de contexte '{CONTEXT_FILE}' introuvable à la racine du projet.")
    exit()
except json.JSONDecodeError:
    print(f"ERREUR: Le fichier '{CONTEXT_FILE}' n'est pas un JSON valide.")
    exit()

# --- SETUP DES OUTILS ---
file_writer = FileWriterTool()
file_reader = FileReadTool()
coding_tools = [file_writer, file_reader]

# --- CRÉATION DES AGENTS (Importés) ---
agents_dict = create_agents(
    llm_mini, 
    llm_smart, 
    coding_tools, 
    context=CONTEXT
)

dev_agent = agents_dict['developer']
review_agent = agents_dict['review']
manager_agent = agents_dict['manager']

# --- DÉFINITION DES TÂCHES ---

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

# --- L'ÉQUIPE (Mode Hiérarchique) ---

my_team = Crew(
    agents=[dev_agent, review_agent],
    tasks=[task_dev, task_review],
    verbose=True,
    process=Process.hierarchical,
    manager_agent=manager_agent,
    memory=True, 
    output_log_file="crew_execution.log" 
)

# --- EXÉCUTION ---
print("### Démarrage du Crew ###")
result = my_team.kickoff(inputs={'project_goal': CONTEXT['project_goal']})

print("\n\n########################")
print("## RÉSULTAT FINAL ##")
print("########################\n")
print(result)

print("\n Usage des tokens (Global) :")
print(result.token_usage)
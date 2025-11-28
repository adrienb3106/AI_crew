# main_crew.py

from dotenv import load_dotenv
from crewai import Crew, Process
from agents import create_agents
from utils import (
    load_json_file, 
    check_api_keys, 
    setup_llms, 
    setup_output_directory, 
    setup_tools, 
    define_tasks
)

from exceptions import ConfigurationError, MissingAPIKeyError
import sys

def main():
    """Fonction principale pour orchestrer le processus du Crew."""
    try:
        load_dotenv()
        
        # --- Chargements et Configurations ---
        config = load_json_file('config.json')
        context = load_json_file('context.json')
        check_api_keys()
        llm_mini, llm_smart = setup_llms(config)
        output_dir = setup_output_directory()
        coding_tools = setup_tools(output_dir)
        
        # --- Création des Agents et Tâches ---
        agents_dict = create_agents(llm_mini, llm_smart, coding_tools, context)
        dev_agent = agents_dict['developer']
        review_agent = agents_dict['review']
        manager_agent = agents_dict['manager']
        
        tasks = define_tasks(dev_agent, review_agent)
        
        # --- Création et Exécution de l'Équipe ---
        crew_config = config.get('crew_config', {})
        
        process_type = crew_config.get('process', 'sequential').lower()
        if process_type == 'hierarchical':
            crew_process = Process.hierarchical
        else:
            crew_process = Process.sequential

        my_team = Crew(
            agents=[manager_agent, dev_agent, review_agent],
            tasks=tasks,
            verbose=crew_config.get('verbose', True),
            process=crew_process,
            manager_agent=manager_agent if crew_process == Process.hierarchical else None,
            memory=crew_config.get('memory', False),
            output_log_file=crew_config.get('output_log_file', False)
        )
        
        print("### Démarrage du Crew ###")
        result = my_team.kickoff(inputs={'project_goal': context['project_goal']})
        
        # --- Affichage des Résultats ---
        print("\n\n########################")
        print("## RÉSULTAT FINAL ##")
        print("########################\n")
        print(result)
        
        print("\nUsage des tokens (Global) :")
        print(result.token_usage)

    except (ConfigurationError, MissingAPIKeyError) as e:
        print(f"\nERREUR CRITIQUE: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUNE ERREUR INATTENDUE EST SURVENUE: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
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

def main():
    """Fonction principale pour orchestrer le processus du Crew."""
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
    my_team = Crew(
        agents=[dev_agent, review_agent],
        tasks=tasks,
        verbose=True,
        process=Process.hierarchical,
        manager_agent=manager_agent,
        memory=True,
        output_log_file="crew_execution.log"
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

if __name__ == "__main__":
    main()
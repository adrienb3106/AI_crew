# main_crew.py

from dotenv import load_dotenv
from crewai import Crew, Process
from dotenv import load_dotenv
from crewai import Crew, Process
from src.agents import create_agent
from src.utils import (
    load_json_file, 
    check_api_keys, 
    setup_llms, 
    setup_output_directory, 
    setup_tools, 
    create_manager_task
)

from src.exceptions import ConfigurationError, MissingAPIKeyError
import sys
import os

def main():
    """Main function to orchestrate the Crew process."""
    try:
        load_dotenv()
        
        # --- Loadings and Configurations ---
        # Remonter d'un cran pour trouver config/ depuis src/
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_path, 'config', 'config.json')
        context_path = os.path.join(base_path, 'config', 'context.json')

        config = load_json_file(config_path)
        context = load_json_file(context_path)
        check_api_keys()
        llm_mini, llm_smart = setup_llms(config)
        
        output_dir_name = config.get('crew_config', {}).get('output_dir_name', 'results')
        output_dir = setup_output_directory(output_dir_name)
        coding_tools = setup_tools(output_dir)
        
        # --- Agent and Task Creation ---
        max_cycles = context.get('process_config', {}).get('max_cycles', 3) #3 is the default value
        agents_dict = {}

        # Dynamic Agent Creation
        for agent_name, agent_context in context.get('agents', {}).items():
            agents_dict[agent_name] = create_agent(
                agent_context=agent_context,
                llm_mini=llm_mini,
                llm_smart=llm_smart,
                coding_tools=coding_tools,
                max_cycles=max_cycles,
                output_dir=output_dir
            )

        manager = agents_dict.pop('manager', None)
        if not manager:
            raise ConfigurationError("An agent with the name 'manager' is required for the hierarchical process.")
        
        worker_agents = list(agents_dict.values())
        
        task = create_manager_task(manager, context)
        
        crew_config = config.get('crew_config', {})
        
        my_team = Crew(
            agents=worker_agents, # Use worker_agents here
            tasks=[task],
            process=Process.hierarchical,
            manager_agent=manager,
            verbose=crew_config.get('verbose', True),
            memory=crew_config.get('memory', False),
            output_log_file=crew_config.get('output_log_file', False)
        )
        
        print("### Starting the Crew ###")
        # The project_goal is now integrated into the manager's task
        result = my_team.kickoff()
        
        # --- Display Results ---
        print("\n\n########################")
        print("## FINAL RESULT ##")
        print("########################\n")
        print(result)
        
        print("\nGlobal Token Usage:")
        print(my_team.usage_metrics)

    except (ConfigurationError, MissingAPIKeyError) as e:
        print(f"\nCRITICAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nAN UNEXPECTED ERROR OCCURRED: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
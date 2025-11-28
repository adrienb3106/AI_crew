# agents.py

from crewai import Agent

# Suppression de l'import FakeListLLM et de la fonction setup_llms

def create_agents(llm_mini, llm_smart, coding_tools, context):
    """Crée et retourne les agents de manière dynamique à partir du contexte."""
    agents = {}
    llm_map = {'mini': llm_mini, 'smart': llm_smart}
    max_cycles = context.get('process_config', {}).get('max_cycles', 3)

    for agent_name, agent_context in context['agents'].items():
        agent_config = agent_context.get('config', {})
        
        # Formattage du but pour y inclure les variables de processus
        goal = agent_context['goal'].format(max_cycles=max_cycles)

        agents[agent_name] = Agent(
            role=agent_context['role'],
            goal=goal,
            backstory=agent_context['backstory'],
            verbose=True,  # Peut être externalisé plus tard si nécessaire
            allow_delegation=agent_config.get('allow_delegation', False),
            llm=llm_map.get(agent_config.get('llm', 'mini')),
            tools=coding_tools if agent_config.get('use_tools', False) else []
        )
    
    return agents
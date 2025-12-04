# agents.py

from crewai import Agent

# Suppression de l'import FakeListLLM et de la fonction setup_llms

def create_agent(agent_context, llm_mini, llm_smart, coding_tools, max_cycles):
    """Crée et retourne un seul agent à partir de son contexte."""
    agent_config = agent_context.get('config', {})
    
    # Formattage du but pour y inclure les variables de processus
    goal = agent_context['goal'].format(max_cycles=max_cycles)
    
    # Détermination des outils à utiliser
    tools = coding_tools if agent_config.get('use_tools', False) else []
    
    # Mapping du LLM
    llm_map = {'mini': llm_mini, 'smart': llm_smart}
    llm = llm_map.get(agent_config.get('llm', 'mini'))

    return Agent(
        role=agent_context['role'],
        goal=goal,
        backstory=agent_context['backstory'],
        verbose=True,  # Peut être externalisé plus tard si nécessaire
        allow_delegation=agent_config.get('allow_delegation', False),
        llm=llm,
        tools=tools
    )
# agents.py

from crewai import Agent

# Suppression de l'import FakeListLLM et de la fonction setup_llms

def create_agents(llm_mini, llm_smart, coding_tools, context):
    """Crée et retourne les agents avec leurs rôles et modèles LLM assignés."""
    
    dev_context = context['agents']['developer']
    review_context = context['agents']['review']
    manager_context = context['agents']['manager']

    # 2. DÉFINITION DE L'AGENT MANAGER
    manager_agent = Agent(
        role=manager_context['role'],
        goal=manager_context['goal'],
        backstory=manager_context['backstory'],
        verbose=True,
        allow_delegation=True,  # Le manager DOIT pouvoir déléguer
        llm=llm_smart
    )

    # 3. DÉFINITION DE L'AGENT DEV
    dev_agent = Agent(
        role=dev_context['role'],
        goal=dev_context['goal'],
        backstory=dev_context['backstory'],
        verbose=True,
        allow_delegation=False,
        tools=coding_tools,
        llm=llm_smart
    )

    # 4. DÉFINITION DE L'AGENT REVIEWER 
    review_agent = Agent(
        role=review_context['role'],
        goal=review_context['goal'],
        backstory=review_context['backstory'],
        verbose=True,
        allow_delegation=False,
        tools=coding_tools,
        llm=llm_mini
    )

    return {
        'manager': manager_agent,
        'developer': dev_agent,
        'review': review_agent
    }
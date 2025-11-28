# My AI Team

## Description

My AI Team is a Python application that leverages the power of large language models (LLMs) to automate code generation and review processes. It relies on the `crewai` framework to orchestrate a team of AI agents, each with a specific role (Manager, Developer, Reviewer), to collaborate on a given programming task.
The project is designed to be highly configurable and extensible. The project's objective, agent roles, and models used can all be customized via simple JSON configuration files.

## Features

- **Automated Code Generation** : Let an AI team write Python code based on your project objectives.
- **Hierarchical Process** : A manager agent delegates tasks to a developer and a reviewer, ensuring a structured workflow.
- **Configurable** : Easily modify the project's objective, agent backstories, and LLM models via JSON files.
- **Extensible** : The project structure allows for easy addition of new agents, tasks, or tools.
- **Modular Codebase** : The code is organized into logical modules for better readability and maintainability.

## Project Structure

```
.
├── .gitignore         # Specifies files to be ignored by Git
├── agents.py          # Defines the AI agents for the team
├── config.json        # Configuration for LLM models
├── context.json       # Configuration for the project objective and agent roles
├── main_crew.py       # Main script to launch the AI team
├── README.md          # This file
├── requirements.txt   # Python dependencies
├── utils.py           # Utility functions used by the main script
└── results/           # Directory where output files are saved
```

## Configuration

Before launching the application, you need to configure the configuration files.

### 1. Environment Variables (`.env`)

Create a `.env` file at the root of the project and add your API keys for LLM providers. You need at least one of the following keys:

```
OPENAI_API_KEY="your-openai-api-key"
ANTHROPIC_API_KEY="your-anthropic-api-key"
GEMINI_API_KEY="your-gemini-api-key"
```

### 2. Model and Crew Configuration (`config.json`)

This file specifies the LLM models to use as well as the team (`Crew`) configuration.

-   **`llm_config`**: Defines the models to use.
    -   `mini_model_name`: This model is used for basic tasks for cost efficiency.
    -   `smart_model_name`: This model is used for more complex tasks.
-   **`crew_config`**: Configures the team's behavior.
    -   `verbose`: If `true`, displays real-time execution details.
    -   `process`: The team's operating mode (`hierarchical` or `sequential`).
    -   `memory`: If `true`, allows the team to remember past tasks.
    -   `output_log_file`: If a filename is provided (e.g., `"crew.log"`), the full execution history will be saved there.

**Example `config.json`:**

```json
{
    "llm_config": {
        "mini_model_name": "gpt-4o-mini",
        "smart_model_name": "gpt-4o"
    },
    "crew_config": {
        "verbose": true,
        "process": "hierarchical",
        "memory": true,
        "output_log_file": "crew_execution.log"
    }
}
```

### 3. Context Configuration (`context.json`)

This file defines the overall project objective as well as the specific roles and backstories of each AI agent. You can also add comments here.

- `project_goal`: A clear and concise description of what the final script should accomplish.
- `agents`: An object containing the configuration for each agent.

**Example `context.json`:**

```json
{
    "project_goal": "Develop a production-grade, performant, and secure Python script...",
    "agents": {
        "manager": {
            "role": "Agile Project Manager",
            "goal": "Coordinate the team to produce code...",
            "backstory": "You are the guarantor of the budget and the final product quality..."
        }
    }
}
```

## How to add and configure an agent

The provided code is an example with a team of three agents (Manager, Developer, Reviewer). You can easily modify it to add, remove, or adapt agents to your needs.

### 1. Update `context.json`

For each new agent, add an entry to the `agents` section of `context.json`. Define its `role`, `goal`, and `backstory`.

**Example: Adding an "Architect" agent**

```json
"architect": {
    "role": "Software Architect",
    "goal": "Design the overall project architecture and ensure it is scalable and robust.",
    "backstory": "You are an experienced architect, obsessed with design patterns and best practices."
}
```

### 2. Create the agent in `agents.py`

In the `agents.py` file, use the `create_agents` function to instantiate your new agent.

- Retrieve the agent's context from the `context` dictionary.
- Create an instance of the `Agent` class using the information from `context.json`.
- Choose the appropriate LLM model (`llm_mini` or `llm_smart`) and `tools` for this agent.
- Add the new agent to the dictionary returned by the function.

**Example: Instantiating the "Architect" agent**

```python
# agents.py

from crewai import Agent

def create_agents(llm_mini, llm_smart, coding_tools, context):
    # ... (code of other agents)

    # Adding the Architect agent
    architect_context = context['agents']['architect']
    architect_agent = Agent(
        role=architect_context['role'],
        goal=architect_context['goal'],
        backstory=architect_context['backstory'],
        verbose=True,
        allow_delegation=False,
        llm=llm_smart  # Use the powerful model for design
    )

    return {
        'manager': manager_agent,
        'developer': dev_agent,
        'reviewer': reviewer_agent,
        'architect': architect_agent  # Don't forget to add it here
    }
```

### 3. Integrate the agent into `main_crew.py`

Finally, integrate the new agent into the main workflow in `main_crew.py`.

- Retrieve the agent instance from the dictionary returned by `create_agents`.
- Add the agent to your `Crew`'s agent list.
- If it's not the manager, ensure it's part of the `worker_agents` list passed to the `Crew`. The manager agent's task is created using `create_manager_task`.

**Example: Integration into the `Crew`**

```python
# main_crew.py

# ... (imports and configuration)

def main():
    # ... (loading configurations)

    agents_dict = create_agents(llm_mini, llm_smart, coding_tools, context)
    manager = agents_dict.pop('manager', None) # Manager is handled separately
    worker_agents = list(agents_dict.values()) # Other agents are worker_agents

    # Create the manager's main task
    task = create_manager_task(manager, context)

    my_team = Crew(
        agents=worker_agents, # Add worker agents to the team
        tasks=[task], # The manager's task
        process=Process.hierarchical,
        manager_agent=manager,
        # ... (rest of Crew configuration)
    )

    # ... (launching the crew)
```

## Installation

1.  Clone the repository:
    ```bash
    git clone <URL-of-repo>
    cd my-ai-team
    ```

2.  Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  Install required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To launch the AI team, simply execute the main script:

```bash
python main_crew.py
```

The script will initialize the agents and tasks, and the team will start working on the project's objective. The final result will be saved in the `results` directory.

## Function Reference (`utils.py`)

---

### `load_json_file(file_path)`

-   **Description**: Loads a JSON file from the given path and returns its content as a Python dictionary.
-   **Parameters**:
    -   `file_path` (str): The path to the JSON file.
-   **Returns**: `dict`: The content of the JSON file.
-   **Exits**: If the file is not found or if the file is not valid JSON.

---

### `check_api_keys()`

-   **Description**: Checks for the presence of necessary API keys in environment variables.
-   **Parameters**: None.
-   **Returns**: Nothing.
-   **Exits**: If no API key is found.

---

### `setup_llms(config)`

-   **Description**: Initializes and returns the LLM models based on the provided configuration.
-   **Parameters**:
    -   `config` (dict): The configuration dictionary loaded from `config.json`.
-   **Returns**: `tuple`: A tuple containing the `llm_mini` and `llm_smart` models.

---

### `setup_output_directory(dir_name="results")`

-   **Description**: Ensures that the output directory exists. If it doesn't, it creates it.
-   **Parameters**:
    -   `dir_name` (str, optional): The name of the output directory. Defaults to `"results"`.
-   **Returns**: `str`: The name of the output directory.

---

### `setup_tools(output_dir)`

-   **Description**: Creates and returns a list of tools that agents can use. In this example, these are tools for reading and writing files.
-   **Parameters**:
    -   `output_dir` (str): The directory where tools should read and write.
-   **Returns**: `list`: A list of `Tool` instances.

---

### `create_manager_task(manager_agent, context)`

-   **Description**: Creates the initial and global task for the manager, based on the project goal and process configuration.
-   **Parameters**:
    -   `manager_agent` (Agent): The manager agent instance.
    -   `context` (dict): The context dictionary loaded from `context.json`.
-   **Returns**: `Task`: A `Task` instance for the manager.
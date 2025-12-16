# utils.py

import os
import json
from crewai import Task, LLM
from crewai_tools import FileWriterTool, FileReadTool

from exceptions import ConfigurationError, MissingAPIKeyError

def load_json_file(file_path):
    """Loads a JSON file and returns its content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ConfigurationError(f"Configuration file '{file_path}' not found.")
    except json.JSONDecodeError:
        raise ConfigurationError(f"File '{file_path}' is not valid JSON.")

def check_api_keys():
    """Checks for the presence of necessary API keys."""
    if not any(os.getenv(key) for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]):
        raise MissingAPIKeyError(
            "No model API key (OpenAI, Anthropic, Gemini) found. "
            "Please define at least one in your .env file."
        )

def setup_llms(config):
    """Initializes and returns the LLM models."""
    print("Initializing LLM models (Production Mode)...")
    llm_mini = LLM(model=config['llm_config']['mini_model_name'])
    llm_smart = LLM(model=config['llm_config']['smart_model_name'])
    return llm_mini, llm_smart

def setup_output_directory(dir_name="results"):
    """Ensures the output directory exists."""
    os.makedirs(dir_name, exist_ok=True)
    print(f"Output directory ensured: '{dir_name}'")
    return dir_name

from crewai.tools import BaseTool
from crewai_tools import FileReadTool

# --- File Registry System ---

class FileRegistry:
    """Singleton to store created files."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FileRegistry, cls).__new__(cls)
            cls._instance.files = []
        return cls._instance

    def add_file(self, filename):
        if filename not in self.files:
            self.files.append(filename)
    
    def get_files(self):
        return self.files

class ListFilesTool(BaseTool):
    name: str = "List Files"
    description: str = "Lists all files created during this session. Use this to verify exact filenames before reading them."
    registry: FileRegistry = None

    def __init__(self, registry):
        super().__init__()
        self.registry = registry

    def _run(self, **kwargs) -> str:
        files = self.registry.get_files()
        if not files:
            return "No files have been created yet."
        return "Files created: " + ", ".join(files)

class SmartFileWriterTool(BaseTool):
    name: str = "Smart File Writer"
    description: str = "Writes content to a file and registers it directly in the system. Arguments: filename (str), content (str)."
    root_dir: str = ""
    registry: FileRegistry = None

    def __init__(self, root_dir, registry):
        super().__init__()
        self.root_dir = root_dir
        self.registry = registry

    def _run(self, filename: str, content: str) -> str:
        try:
            full_path = os.path.join(self.root_dir, filename)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.registry.add_file(filename)
            return f"Successfully created file '{filename}' and registered it in the system."
        except Exception as e:
            return f"Error writing file: {str(e)}"

# ---

def setup_tools(output_dir):
    """Crée et retourne un dictionnaire d'outils disponibles."""
    registry = FileRegistry()
    
    return {
        "file_writer": SmartFileWriterTool(root_dir=output_dir, registry=registry),
        "file_reader": FileReadTool(root_dir=output_dir),
        "list_files": ListFilesTool(registry=registry)
    }

def create_manager_task(manager_agent, context):
    """Creates the initial and global task for the manager."""
    project_goal = context.get('project_goal', '')
    max_cycles = context.get('process_config', {}).get('max_cycles', 3)

    return Task(
        description=f"The project goal is: '{project_goal}'. You must manage the project in {max_cycles} sprints. Be concise. Do not summarize previous steps excessively.",
        expected_output=f"The final code for the project '{project_goal}', approved or as is after {max_cycles} sprints.",
        agent=None # Laissez CrewAI assigner cela au manager hiérarchique
    )
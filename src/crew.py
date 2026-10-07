import os
import yaml
from pathlib import Path
from crewai import Agent, Task, Crew, Process, LLM

# Helper to load YAML configurations
def load_yaml(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

BASE_DIR = Path(__file__).resolve().parent.parent
AGENTS_CONFIG = load_yaml(BASE_DIR / "config" / "agents.yaml")
TASKS_CONFIG = load_yaml(BASE_DIR / "config" / "tasks.yaml")

class IncidentResponseCrew:
    """Manages the creation and execution of Incident Response agents using Google Gemini."""
    
    def __init__(self, model_name: str = "gemini/gemini-2.5-flash"):
        # Initialize the LLM instance with Gemini
        self.llm = LLM(
            model=model_name,
            api_key=os.environ.get("GEMINI_API_KEY")
        )

    def run_diagnosis(self, service_name: str, logs: str) -> str:
        """Executes the initial incident triage task."""
        diagnostician = Agent(
            config=AGENTS_CONFIG["diagnostician"],
            llm=self.llm,
            verbose=True
        )
        
        diag_task = Task(
            config=TASKS_CONFIG["diagnosis_task"],
            agent=diagnostician
        )
        
        crew = Crew(
            agents=[diagnostician],
            tasks=[diag_task],
            process=Process.sequential
        )
        
        result = crew.kickoff(inputs={"service_name": service_name, "logs": logs})
        return str(result)

    def run_postmortem(self, diagnosis_output: str) -> str:
        """Executes the post-mortem report generation task."""
        writer = Agent(
            config=AGENTS_CONFIG["postmortem_writer"],
            llm=self.llm,
            verbose=True
        )
        
        pm_task = Task(
            config=TASKS_CONFIG["postmortem_task"],
            agent=writer
        )
        
        crew = Crew(
            agents=[writer],
            tasks=[pm_task],
            process=Process.sequential
        )
        
        result = crew.kickoff(inputs={"diagnosis_output": diagnosis_output})
        return str(result)
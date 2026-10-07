from pydantic import BaseModel
from crewai.flow.flow import Flow, start, listen, router
from src.crew import IncidentResponseCrew

class IncidentState(BaseModel):
    service_name: str = ""
    logs: str = ""
    severity: str = "UNKNOWN"
    diagnosis: str = ""
    postmortem: str = ""

class IncidentResponseFlow(Flow[IncidentState]):
    """
    Agentic Flow managing the lifecycle of an incident:
    1. Triage & Diagnose system logs.
    2. Route execution based on severity.
    3. Generate Post-Mortem if severity is High/Critical.
    """

    @start()
    def diagnose_incident(self):
        """Step 1: Execute initial diagnosis via CrewAI."""
        crew_handler = IncidentResponseCrew()
        diagnosis_res = crew_handler.run_diagnosis(
            service_name=self.state.service_name,
            logs=self.state.logs
        )
        
        self.state.diagnosis = diagnosis_res
        
        # Simple heuristic to determine severity from output
        diag_upper = diagnosis_res.upper()
        if "CRITICAL" in diag_upper or "HIGH" in diag_upper:
            self.state.severity = "HIGH"
        else:
            self.state.severity = "LOW"
            
        return self.state.diagnosis

    @router(diagnose_incident)
    def route_by_severity(self):
        """Step 2: Route workflow conditionally depending on incident impact."""
        if self.state.severity == "HIGH":
            return "high_severity_path"
        return "low_severity_path"

    @listen("high_severity_path")
    def generate_postmortem(self):
        """Step 3a: High severity flow - trigger post-mortem report generation."""
        crew_handler = IncidentResponseCrew()
        postmortem_res = crew_handler.run_postmortem(
            diagnosis_output=self.state.diagnosis
        )
        self.state.postmortem = postmortem_res
        return self.state.postmortem

    @listen("low_severity_path")
    def resolve_minor_incident(self):
        """Step 3b: Low severity flow - close out workflow cleanly."""
        self.state.postmortem = "N/A - Standard minor incident; post-mortem not required."
        return self.state.postmortem

import json
from internal.engine.llm.gateway import llm

class TaskDecomposer:
    """
    Takes a validated spec.json and decomposes it into atomic implementation tasks.
    """
    def decompose(self, spec: dict) -> list:
        system_prompt = """You are the SpecKit Pro Task Decomposer.
        Break down the provided high-fidelity spec into atomic implementation tasks.
        
        REQUIRED TASK SCHEMA:
        - id: string (e.g., TASK-001)
        - file_path: string (target file)
        - description: string (what to do)
        - dependencies: array of strings (task IDs)
        - acceptance_criteria: array of strings
        
        Return a JSON object with a "tasks" key containing the array of tasks.
        """
        
        response_text = llm.complete(
            prompt=json.dumps(spec),
            system_prompt=system_prompt,
            role="generator", # Decomposition requires high reasoning
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response_text)
        return data.get("tasks", [])

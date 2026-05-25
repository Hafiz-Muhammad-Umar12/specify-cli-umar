import json
from speckit_pro.engine.llm.gateway import llm

class ArchitectAgent:
    def design_system(self, spec: dict) -> dict:
        system_prompt = """You are the Architect Agent.
        Refine the 'system_design', 'api_endpoints', and 'database_schema' 
        of the given spec to follow enterprise best practices."""
        
        response = llm.complete(
            prompt=json.dumps(spec),
            system_prompt=system_prompt,
            role="architect",
            response_format={"type": "json_object"}
        )
        return json.loads(response)

class SecurityAgent:
    def audit_and_secure(self, spec: dict) -> dict:
        system_prompt = """You are the Security Agent.
        Audit the spec and augment 'security_model' and 'security_requirements'
        with necessary protections against OWASP Top 10."""
        
        response = llm.complete(
            prompt=json.dumps(spec),
            system_prompt=system_prompt,
            role="security",
            response_format={"type": "json_object"}
        )
        return json.loads(response)

class DevAgent:
    def generate_code(self, task: dict) -> str:
        system_prompt = """You are the Dev Agent.
        Write complete code for the requested file.
        Output valid JSON with {"code": "..."}."""
        prompt = f"Task: {task['description']}\nFile path: {task['file_path']}"
        response = llm.complete(prompt, system_prompt=system_prompt, role="dev", response_format={"type": "json_object"})
        return json.loads(response).get("code", "")

class QAAgent:
    def generate_tests(self, task: dict, code: str) -> str:
        system_prompt = """You are the QA Agent.
        Write unit tests for the provided code.
        Output valid JSON with {"test_code": "..."}."""
        prompt = f"Code:\n{code}\nCriteria: {task.get('acceptance_criteria')}"
        response = llm.complete(prompt, system_prompt=system_prompt, role="qa", response_format={"type": "json_object"})
        return json.loads(response).get("test_code", "")

class ReviewerAgent:
    def review_code(self, task: dict, code: str, test_code: str) -> dict:
        system_prompt = """You are the Reviewer Agent.
        Review the implementation and tests.
        Output valid JSON with {"approved": true/false, "feedback": "..."}."""
        prompt = f"Task: {task['description']}\nCode:\n{code}\nTests:\n{test_code}"
        response = llm.complete(prompt, system_prompt=system_prompt, role="reviewer", response_format={"type": "json_object"})
        return json.loads(response)

import os
import time
import logging
from typing import Optional, Any, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLMGateway")

class LLMGateway:
    """
    Production-ready LLM Gateway using LiteLLM.
    Supports fallback routing, retries, role-based model selection, and usage tracking.
    """
    
    MODELS = {
        "generator": ["gpt-4o", "claude-3-5-sonnet-20240620", "gemini/gemini-1.5-pro"],
        "critic": ["gpt-4o-mini", "gemini/gemini-1.5-flash", "claude-3-haiku-20240307"],
        "refiner": ["gpt-4o", "claude-3-5-sonnet-20240620", "gemini/gemini-1.5-pro"],
        "architect": ["gpt-4o", "claude-3-5-sonnet-20240620"],
        "security": ["gpt-4o", "claude-3-5-sonnet-20240620"],
        "dev": ["gpt-4o", "claude-3-5-sonnet-20240620", "gemini/gemini-1.5-pro"],
        "qa": ["gpt-4o-mini", "gemini/gemini-1.5-flash"],
        "reviewer": ["gpt-4o", "claude-3-5-sonnet-20240620"]
    }

    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock
        self.usage_stats = {"total_calls": 0, "roles": {}}
        if not use_mock:
            self._validate_env()

    def _validate_env(self):
        keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]
        missing = [k for k in keys if not os.getenv(k)]
        if len(missing) == len(keys):
            logger.warning("No LLM API keys found. Gateway might fail unless using a local provider.")

    def _track_usage(self, role: str):
        self.usage_stats["total_calls"] += 1
        self.usage_stats["roles"][role] = self.usage_stats["roles"].get(role, 0) + 1
        
        # Persist to DB
        try:
            from internal.memory.state.db import StateMachineDB
            import json
            db = StateMachineDB()
            db.set_system_state("llm_usage", json.dumps(self.usage_stats))
        except Exception:
            pass

    def complete(
        self, 
        prompt: str, 
        system_prompt: str = "", 
        role: str = "generator",
        response_format: Optional[Dict] = None,
        retries: int = 3
    ) -> str:
        self._track_usage(role)
        
        if self.use_mock:
            return self._mock_completion(prompt, system_prompt, role)

        try:
            import litellm
        except ImportError:
            logger.error("litellm not installed. Falling back to mock.")
            return self._mock_completion(prompt, system_prompt, role)

        models_to_try = self.MODELS.get(role, self.MODELS["generator"])
        
        for model in models_to_try:
            for attempt in range(retries):
                try:
                    logger.info(f"Attempting {model} (Attempt {attempt + 1}) for role '{role}'")
                    response = litellm.completion(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        response_format=response_format,
                        timeout=60
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    logger.error(f"Error with {model}: {e}")
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)
                    else:
                        logger.warning(f"Moving to next model in fallback list after {model} failed.")
                        break
        
        raise RuntimeError(f"All models failed for role '{role}' after exhaustive retries and fallbacks.")

    def _mock_completion(self, prompt, system_prompt, role):
        import json
        p_lower = system_prompt.lower()
        
        if role == "dev" or "expert coder" in p_lower:
            return json.dumps({"code": "# Generated mock code for " + prompt[:20] + "\ndef mock_func():\n    pass"})
        elif role == "qa":
            return json.dumps({"test_code": "# Mock test for " + prompt[:20] + "\ndef test_mock():\n    assert True"})
        elif role == "reviewer":
            return json.dumps({"approved": True, "feedback": "LGTM!"})
        elif role == "architect":
            spec = json.loads(prompt)
            spec["system_design"] = "Refined Event-Driven Microservices"
            return json.dumps(spec)
        elif role == "security":
            spec = json.loads(prompt)
            spec["security_model"] = "Zero Trust Architecture with mTLS"
            return json.dumps(spec)
            
        if "generator" in p_lower or "decomposer" in p_lower:
            if "decomposer" in p_lower:
                return json.dumps({
                    "tasks": [
                        {
                            "id": "TASK-001",
                            "file_path": "models.py",
                            "description": "Define the User model",
                            "dependencies": [],
                            "acceptance_criteria": ["Field 'username' exists"]
                        }
                    ]
                })
            return json.dumps({
                "title": "Mock Project",
                "description": "Mock description",
                "user_stories": ["Story 1"],
                "functional_requirements": ["Req 1"],
                "system_design": "Microservices",
                "api_endpoints": [{"name": "Signup", "path": "/signup", "method": "POST", "description": "User signup"}],
                "database_schema": "PostgreSQL",
                "security_model": "OAuth2",
                "scalability_notes": "Use K8s",
                "security_requirements": ["Encryption"],
                "edge_cases": ["Retry on fail"]
            })
        elif "critic" in p_lower:
            return json.dumps({"pass": True, "violations": []})
        elif "refiner" in p_lower:
            return prompt
        return "{}"

llm = LLMGateway(use_mock=True)

import json
from internal.engine.llm.gateway import llm

class GeneratorAgent:
    def draft_spec(self, user_idea: str, past_context: str = "") -> dict:
        system_prompt = f"""You are the SpecKit Pro Generator.
        Convert the user's idea into a high-fidelity JSON specification.
        
        {past_context}
        
        REQUIRED SCHEMA:
        - title: String
        - description: String
        - user_stories: Array of Strings
        - functional_requirements: Array of Strings
        - system_design: String (High-level architecture)
        - api_endpoints: Array of Objects (name, path, method, description)
        - database_schema: String (Table definitions or ERD description)
        - security_model: String (Auth/AuthZ, encryption)
        - scalability_notes: String (How it handles load)
        - security_requirements: Array of Strings
        - edge_cases: Array of Strings
        """
        
        response_text = llm.complete(
            prompt=user_idea,
            system_prompt=system_prompt,
            role="generator",
            response_format={"type": "json_object"}
        )
        return json.loads(response_text)

class CriticAgent:
    def critique_spec(self, spec: dict) -> dict:
        system_prompt = """You are the SpecKit Pro Critic.
        Review the JSON spec for architectural completeness and security.
        Check each section: title, description, user_stories, functional_requirements, system_design, 
        api_endpoints, database_schema, security_model, scalability_notes, security_requirements, edge_cases.
        
        Return JSON:
        {
            "pass": boolean,
            "violations": [
                {"section": "string", "issue": "string", "severity": "high|medium|low"}
            ]
        }
        """
        
        response_text = llm.complete(
            prompt=json.dumps(spec),
            system_prompt=system_prompt,
            role="critic",
            response_format={"type": "json_object"}
        )
        return json.loads(response_text)

class RefinerAgent:
    def refine_spec(self, original_spec: dict, violations: list) -> dict:
        system_prompt = """You are the SpecKit Pro Refiner.
        Fix the provided JSON spec by addressing the Critic's violations.
        Ensure the resulting JSON is complete and follows the original schema perfectly."""
        
        input_data = json.dumps({
            "spec": original_spec,
            "violations": violations
        })

        response_text = llm.complete(
            prompt=input_data,
            system_prompt=system_prompt,
            role="refiner",
            response_format={"type": "json_object"}
        )
        return json.loads(response_text)

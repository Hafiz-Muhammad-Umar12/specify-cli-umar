from speckit_pro.engine.agents.core_loop import GeneratorAgent, CriticAgent, RefinerAgent
from speckit_pro.engine.agents.task_decomposer import TaskDecomposer
from speckit_pro.memory.vector_db import MemoryLayer
from speckit_pro.execution.task_runner import TaskRunner

class SpecKitProOrchestrator:
    def __init__(self):
        self.generator = GeneratorAgent()
        self.critic = CriticAgent()
        self.refiner = RefinerAgent()
        self.decomposer = TaskDecomposer()
        self.memory = MemoryLayer()
        self.max_loops = 3

    def run_full_cycle(self, user_idea: str):
        print(f"\n--- [SpecKit Pro] Starting Full Lifecycle for: '{user_idea}' ---")

        # 1. Retrieval
        print("\n[1/4] MEMORY: Searching for similar past projects...")
        context = self.memory.retrieve_similar(user_idea)
        if context:
            print("      -> Found similar context in vector DB.")
        else:
            print("      -> No prior context found.")

        # 2. Spec Generation Loop
        print("\n[2/4] SPEC: Generating and validating specification...")
        current_spec = self.generator.draft_spec(user_idea, past_context=context)
        
        for attempt in range(1, self.max_loops + 1):
            critique = self.critic.critique_spec(current_spec)
            if critique.get("pass"):
                print("      -> Spec Validated Successfully.")
                break
            
            if attempt == self.max_loops:
                print("      -> Warning: Max refinement loops reached.")
                break
                
            print(f"      -> Iteration {attempt}: Refining due to violations...")
            current_spec = self.refiner.refine_spec(current_spec, critique.get("violations", []))

        # Store validated spec in memory
        self.memory.store_spec(current_spec)

        # 3. Task Decomposition
        print("\n[3/4] DECOMPOSITION: Breaking spec into implementation tasks...")
        tasks = self.decomposer.decompose(current_spec)
        print(f"      -> Generated {len(tasks)} atomic tasks.")

        # 4. Execution (Skeleton)
        print("\n[4/4] EXECUTION: Starting task runner...")
        runner = TaskRunner(tasks)
        while any(status == "Pending" for status in runner.get_summary().values()):
            runner.execute_next()

        print("\n--- [SpecKit Pro] Lifecycle Complete! ---")
        return current_spec, tasks

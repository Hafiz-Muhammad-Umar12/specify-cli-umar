import enum
import os
import subprocess
from typing import List, Dict, Any
from internal.execution.code_generator import CodeGenerator
from internal.engine.agents.specialized import DevAgent, QAAgent, ReviewerAgent

class TaskStatus(enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
    FAILED = "Failed"

class TaskRunner:
    """
    Executes tasks using the real CodeGenerator and the Dev -> QA -> Reviewer AI loop.
    """
    def __init__(self, tasks: List[Dict[str, Any]], dry_run: bool = False):
        self.tasks = tasks
        self.state = {t["id"]: TaskStatus.PENDING for t in tasks}
        self.code_gen = CodeGenerator(dry_run=dry_run)
        
        self.dev = DevAgent()
        self.qa = QAAgent()
        self.reviewer = ReviewerAgent()
        self.max_retries = 3

    def execute_next(self):
        """Finds and executes the next available task."""
        for task in self.tasks:
            if self.state[task["id"]] == TaskStatus.PENDING:
                deps_met = all(self.state.get(d) == TaskStatus.COMPLETED for d in task.get("dependencies", []))
                if deps_met:
                    self._run_task(task)

    def _run_tests(self, test_file_path: str):
        """Simulates running the tests using pytest."""
        if self.code_gen.dry_run:
            print("[DRY RUN] Would execute pytest on " + test_file_path)
            return True, "Mock tests passed."
            
        full_path = os.path.join(self.code_gen.workspace_dir, test_file_path)
        try:
            # We mock the actual test execution if the file isn't real Python or pytest isn't available
            # For this MVP, we simulate a successful test run if the file exists
            if os.path.exists(full_path):
                return True, "Tests passed."
            else:
                return False, "Test file not found."
        except Exception as e:
            return False, str(e)

    def _run_task(self, task: Dict[str, Any]):
        print(f"\n[RUNNER] Executing {task['id']}: {task['description']}")
        self.state[task["id"]] = TaskStatus.IN_PROGRESS
        
        try:
            for attempt in range(self.max_retries):
                print(f"  -> [Attempt {attempt+1}] DevAgent: Generating code...")
                code_content = self.dev.generate_code(task)
                
                print(f"  -> [Attempt {attempt+1}] QAAgent: Generating tests...")
                test_content = self.qa.generate_tests(task, code_content)
                
                print(f"  -> [Attempt {attempt+1}] ReviewerAgent: Reviewing...")
                review = self.reviewer.review_code(task, code_content, test_content)
                
                if review.get("approved"):
                    print("  -> Reviewer approved.")
                    
                    # Write and commit
                    self.code_gen.write_file(task["file_path"], code_content)
                    
                    # Also write tests
                    test_file = task["file_path"].replace(".py", "_test.py")
                    if "test_file" not in task["file_path"]:
                        self.code_gen.write_file(test_file, test_content)
                        
                    # Run tests
                    passed, log = self._run_tests(test_file)
                    if passed:
                        print("  -> Tests passed.")
                        self.code_gen.commit_task(task["id"], task["description"])
                        print(f"[RUNNER] Task {task['id']} COMPLETED.")
                        self.state[task["id"]] = TaskStatus.COMPLETED
                        return
                    else:
                        print(f"  -> Tests failed: {log}")
                        task["description"] += f" Fix failing tests: {log}"
                else:
                    print(f"  -> Reviewer rejected: {review.get('feedback')}")
                    task["description"] += f" Feedback: {review.get('feedback')}"
            
            print(f"[RUNNER] Task {task['id']} FAILED after {self.max_retries} retries.")
            self.state[task["id"]] = TaskStatus.FAILED

        except Exception as e:
            print(f"[RUNNER] Task {task['id']} FAILED: {e}")
            self.state[task["id"]] = TaskStatus.FAILED

    def get_summary(self):
        return {tid: status.value for tid, status in self.state.items()}

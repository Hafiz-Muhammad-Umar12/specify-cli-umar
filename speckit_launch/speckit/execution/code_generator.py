import os
import subprocess
import difflib
from typing import Dict, Any

class CodeGenerator:
    def __init__(self, workspace_dir: str = "out", dry_run: bool = False):
        self.workspace_dir = workspace_dir
        self.dry_run = dry_run
        if not self.dry_run:
            os.makedirs(self.workspace_dir, exist_ok=True)
            self._init_git()

    def _init_git(self):
        if not os.path.exists(os.path.join(self.workspace_dir, ".git")):
            subprocess.run(["git", "init"], cwd=self.workspace_dir, capture_output=True)

    def write_file(self, file_path: str, content: str):
        full_path = os.path.join(self.workspace_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        old_content = ""
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                old_content = f.read()

        if self.dry_run:
            print(f"\n[DRY RUN] Diff for {file_path}:")
            diff = difflib.unified_diff(
                old_content.splitlines(keepends=True),
                content.splitlines(keepends=True),
                fromfile='a/' + file_path,
                tofile='b/' + file_path
            )
            print("".join(diff))
        else:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

    def commit_task(self, task_id: str, description: str):
        if self.dry_run:
            print(f"[DRY RUN] Would commit: {task_id}: {description}")
            return
        
        subprocess.run(["git", "add", "."], cwd=self.workspace_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"{task_id}: {description}"], cwd=self.workspace_dir, capture_output=True)

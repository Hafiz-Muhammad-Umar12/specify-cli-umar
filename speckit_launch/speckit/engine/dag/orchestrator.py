import time
from typing import Dict, Any, List
from internal.memory.state.db import StateMachineDB
from internal.engine.agents.core_loop import GeneratorAgent, CriticAgent, RefinerAgent
from internal.engine.agents.specialized import ArchitectAgent, SecurityAgent
from internal.engine.agents.task_decomposer import TaskDecomposer
from internal.execution.task_runner import TaskRunner
from internal.memory.vector_db import MemoryLayer

class DAGOrchestrator:
    """
    DAG-based orchestrator with multi-agent pipeline and Human-in-the-Loop controls.
    """
    def __init__(self, dry_run: bool = False):
        self.db = StateMachineDB()
        self.generator = GeneratorAgent()
        self.architect = ArchitectAgent()
        self.security = SecurityAgent()
        self.critic = CriticAgent()
        self.refiner = RefinerAgent()
        self.decomposer = TaskDecomposer()
        self.memory = MemoryLayer()
        self.dry_run = dry_run
        
    def init_dag(self, idea: str):
        self.db.clear_all()
        self.db.set_system_state("idea", idea)
        self.db.set_system_state("global_status", "running")
        
        # Define DAG nodes for Multi-Agent Spec Generation
        self.db.upsert_node("spec_gen", "generation", "pending")
        self.db.upsert_node("spec_arch", "architecture", "pending", dependencies=["spec_gen"])
        self.db.upsert_node("spec_sec", "security", "pending", dependencies=["spec_arch"])
        self.db.upsert_node("spec_val", "validation", "pending", dependencies=["spec_sec"])
        self.db.upsert_node("human_approval", "gate", "pending", dependencies=["spec_val"])
        self.db.upsert_node("task_decomp", "decomposition", "pending", dependencies=["human_approval"])
        self.db.upsert_node("task_exec", "execution", "pending", dependencies=["task_decomp"])

    def pause(self):
        self.db.set_system_state("global_status", "paused")
        print("[DAG] Execution paused.")

    def resume(self):
        self.db.set_system_state("global_status", "running")
        print("[DAG] Execution resumed.")
        self.run_loop()

    def rollback(self, target_node: str):
        nodes = self.db.get_all_nodes()
        found = False
        for n in nodes:
            if n["id"] == target_node:
                found = True
            if found:
                self.db.upsert_node(n["id"], n["type"], "pending", data={}, dependencies=n["dependencies"])
        if found:
            self.db.set_system_state("global_status", "running")
            print(f"[DAG] Rolled back to {target_node}.")
        else:
            print(f"[DAG] Node {target_node} not found.")

    def approve(self):
        node = self.db.get_node("human_approval")
        if node and node["status"] == "pending":
            self.db.upsert_node("human_approval", "gate", "completed", dependencies=node["dependencies"])
            print("[DAG] Gate approved by human.")
            self.db.set_system_state("global_status", "running")
            self.run_loop()
        else:
            print("[DAG] No pending approval gate.")

    def run_loop(self):
        while self.db.get_system_state("global_status") == "running":
            nodes = self.db.get_all_nodes()
            pending_nodes = [n for n in nodes if n["status"] == "pending"]
            
            if not pending_nodes:
                print("\n[DAG] All nodes completed. Execution finished.")
                break

            progress = False
            for node in pending_nodes:
                deps_met = True
                for dep_id in node["dependencies"]:
                    dep_node = self.db.get_node(dep_id)
                    if dep_node["status"] != "completed":
                        deps_met = False
                        break
                
                if deps_met:
                    if node["type"] == "gate":
                        print(f"\n[DAG] Execution paused at gate '{node['id']}'. Waiting for human approval. Run 'approve' to continue.")
                        self.db.set_system_state("global_status", "paused")
                        progress = True
                        break
                    else:
                        self._execute_node(node)
                        progress = True
                        break

            if not progress:
                if self.db.get_system_state("global_status") == "running":
                    failed = next((n for n in nodes if n["status"] == "failed"), None)
                    if failed:
                        print(f"\n[DAG] Execution blocked by failed node '{failed['id']}'.")
                        self.db.set_system_state("global_status", "paused")
                    else:
                        print("\n[DAG] Deadlock detected! No nodes can execute.")
                        self.db.set_system_state("global_status", "error")
                break

    def _execute_node(self, node: dict):
        node_id = node["id"]
        node_type = node["type"]
        print(f"\n[DAG] Executing node: {node_id} ({node_type})")
        self.db.upsert_node(node_id, node_type, "in_progress", dependencies=node["dependencies"])
        
        try:
            if node_type == "generation":
                idea = self.db.get_system_state("idea")
                context = self.memory.retrieve_similar(idea)
                spec = self.generator.draft_spec(idea, past_context=context)
                self.db.upsert_node(node_id, node_type, "completed", data={"spec": spec}, dependencies=node["dependencies"])
                
            elif node_type == "architecture":
                gen_node = self.db.get_node("spec_gen")
                spec = self.architect.design_system(gen_node["data"]["spec"])
                self.db.upsert_node(node_id, node_type, "completed", data={"spec": spec}, dependencies=node["dependencies"])
                
            elif node_type == "security":
                arch_node = self.db.get_node("spec_arch")
                spec = self.security.audit_and_secure(arch_node["data"]["spec"])
                self.db.upsert_node(node_id, node_type, "completed", data={"spec": spec}, dependencies=node["dependencies"])
                
            elif node_type == "validation":
                sec_node = self.db.get_node("spec_sec")
                spec = sec_node["data"]["spec"]
                
                max_loops = 3
                for attempt in range(max_loops):
                    critique = self.critic.critique_spec(spec)
                    if critique.get("pass"):
                        print(f"      -> Validation pass on attempt {attempt+1}")
                        self.db.upsert_node(node_id, node_type, "completed", data={"spec": spec}, dependencies=node["dependencies"])
                        self.memory.store_spec(spec, success=True)
                        return
                    print(f"      -> Refining violations: {critique.get('violations')}")
                    spec = self.refiner.refine_spec(spec, critique.get("violations", []))
                
                self.db.upsert_node(node_id, node_type, "completed", data={"spec": spec}, dependencies=node["dependencies"])
                self.memory.store_spec(spec, success=False) # Record failed pattern

            elif node_type == "gate":
                pass
                
            elif node_type == "decomposition":
                val_node = self.db.get_node("spec_val")
                spec = val_node["data"]["spec"]
                tasks = self.decomposer.decompose(spec)
                self.db.upsert_node(node_id, node_type, "completed", data={"tasks": tasks}, dependencies=node["dependencies"])

            elif node_type == "execution":
                decomp_node = self.db.get_node("task_decomp")
                tasks = decomp_node["data"]["tasks"]
                runner = TaskRunner(tasks, dry_run=self.dry_run)
                while any(status == "Pending" for status in runner.get_summary().values()):
                    runner.execute_next()
                self.db.upsert_node(node_id, node_type, "completed", dependencies=node["dependencies"])

        except Exception as e:
            print(f"[DAG] Node {node_id} failed: {e}")
            self.db.upsert_node(node_id, node_type, "failed", error=str(e), dependencies=node["dependencies"])
            self.db.set_system_state("global_status", "error")

from internal.memory.state.db import StateMachineDB
import json

def render_dashboard():
    db = StateMachineDB()
    nodes = db.get_all_nodes()
    global_status = db.get_system_state("global_status") or "uninitialized"
    idea = db.get_system_state("idea") or "N/A"

    print("=" * 60)
    print(" " * 20 + "SPECKIT PRO DASHBOARD")
    print("=" * 60)
    print(f"Project Idea: {idea}")
    print(f"Global State: {global_status.upper()}")
    print("-" * 60)
    
    print("DAG EXECUTION GRAPH:")
    
    order = [
        "spec_gen", 
        "spec_arch", 
        "spec_sec", 
        "spec_val", 
        "human_approval", 
        "task_decomp", 
        "task_exec"
    ]
    
    node_dict = {n["id"]: n for n in nodes}
    
    for i, n_id in enumerate(order):
        node = node_dict.get(n_id)
        if not node:
            status = "[NOT STARTED]"
        else:
            status = f"[{node['status'].upper()}]"
            
        prefix = "  " if i == 0 else "  |-> "
        print(f"{prefix}{status} {n_id}")
        
    print("-" * 60)
    print("LLM USAGE TRACKING:")
    
    usage_str = db.get_system_state("llm_usage")
    if usage_str:
        usage = json.loads(usage_str)
        print(f"Total API Calls: {usage.get('total_calls', 0)}")
        for role, count in usage.get("roles", {}).items():
            print(f"  - {role}: {count} calls")
    else:
        print("Total API Calls: 0")
        
    print("=" * 60)

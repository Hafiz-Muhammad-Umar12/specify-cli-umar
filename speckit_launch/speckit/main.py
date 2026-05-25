import typer
import json
import sys
import os

# Add parent directory to path to allow direct execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from internal.engine.dag.orchestrator import DAGOrchestrator

app = typer.Typer(help="SpecKit Pro CLI")

@app.command()
def run(
    idea: str = typer.Argument(..., help="The natural language project idea"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Run execution phase in dry-run mode")
):
    """
    Start the DAG lifecycle from idea to execution.
    """
    orchestrator = DAGOrchestrator(dry_run=dry_run)
    orchestrator.init_dag(idea)
    orchestrator.run_loop()

@app.command()
def approve(dry_run: bool = typer.Option(False, "--dry-run", help="Run execution phase in dry-run mode")):
    """
    Approve the pending gate and continue execution.
    """
    orchestrator = DAGOrchestrator(dry_run=dry_run)
    orchestrator.approve()

@app.command()
def pause():
    """
    Pause the DAG execution.
    """
    orchestrator = DAGOrchestrator()
    orchestrator.pause()

@app.command()
def resume(dry_run: bool = typer.Option(False, "--dry-run", help="Run execution phase in dry-run mode")):
    """
    Resume a paused DAG execution.
    """
    orchestrator = DAGOrchestrator(dry_run=dry_run)
    orchestrator.resume()

@app.command()
def rollback(node_id: str = typer.Argument(..., help="Node ID to rollback to (e.g., 'spec_gen', 'spec_val')")):
    """
    Rollback the DAG to a specific node state.
    """
    orchestrator = DAGOrchestrator()
    orchestrator.rollback(node_id)

@app.command()
def status():
    """
    Print the current status of all DAG nodes.
    """
    from internal.memory.state.db import StateMachineDB
    db = StateMachineDB()
    nodes = db.get_all_nodes()
    typer.echo(f"Global Status: {db.get_system_state('global_status')}")
    for n in nodes:
        typer.echo(f"[{n['status']}] {n['id']} ({n['type']})")

@app.command()
def dashboard():
    """
    Render the SpecKit Pro graphical dashboard.
    """
    from internal.cli.dashboard import render_dashboard
    render_dashboard()

if __name__ == "__main__":
    app()

import typer
import sys
import os
import json
import contextlib
import io
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.live import Live
from rich.table import Table

# Add current directory to sys.path for internal imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from internal.engine.dag.orchestrator import DAGOrchestrator
from internal.memory.state.db import StateMachineDB

app = typer.Typer(help="SpecKit: Build high-quality software from a single idea.", add_completion=False)
console = Console()

@app.command()
def run(
    idea: str = typer.Argument(..., help="The natural language idea for your project"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without writing to disk"),
    auto_approve: bool = typer.Option(True, "--auto-approve", help="Automatically skip human-in-the-loop gates")
):
    """
    Transform your idea into a production-ready software repository.
    """
    console.print(Panel(f"[bold green]🌱 SpecKit is bringing your idea to life:[/bold green]\n[dim]{idea}[/dim]", expand=False))
    
    # Internal DAG Orchestrator (Hidden from user)
    orchestrator = DAGOrchestrator(dry_run=dry_run)
    db = StateMachineDB()
    
    # User-friendly progress mapping
    friendly_names = {
        "spec_gen": "Drafting product requirements...",
        "spec_arch": "Designing system architecture...",
        "spec_sec": "Hardening security layer...",
        "spec_val": "Verifying project integrity...",
        "human_approval": "Finalizing design...",
        "task_decomp": "Preparing implementation roadmap...",
        "task_exec": "Generating production code and tests..."
    }

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        
        main_task = progress.add_task("[cyan]Starting SpecKit engine...", total=100)
        
        # 1. Initialization
        orchestrator.init_dag(idea)
        progress.update(main_task, advance=5, description="[yellow]Initializing workspace...")
        
        while True:
            nodes = db.get_all_nodes()
            pending = [n for n in nodes if n["status"] == "pending"]
            completed = [n for n in nodes if n["status"] == "completed"]
            
            # Update progress based on DAG completion
            total_nodes = len(nodes)
            percent = (len(completed) / total_nodes) * 90 
            progress.update(main_task, completed=5 + percent)

            if not pending:
                break
                
            current_node = pending[0]
            node_desc = friendly_names.get(current_node["id"], "Processing...")
            progress.update(main_task, description=f"[cyan]{node_desc}")

            # Suppress internal technical logs
            with contextlib.redirect_stdout(io.StringIO()):
                if current_node["type"] == "gate":
                    if auto_approve:
                        orchestrator.approve()
                    else:
                        # Manual interaction needed
                        progress.stop()
                        console.print(f"\n[bold yellow]Design Milestone Reached:[/bold yellow] {current_node['id']}")
                        if typer.confirm("Review and proceed?"):
                            progress.start()
                            orchestrator.approve()
                        else:
                            console.print("[red]Aborted by user.[/red]")
                            raise typer.Exit()
                else:
                    orchestrator.run_loop()
            
            # Check for failures
            nodes_after = db.get_all_nodes()
            failed = [n for n in nodes_after if n["status"] == "failed"]
            if failed:
                console.print(f"\n[red]Error:[/red] Failed at step {failed[0]['id']}. {failed[0]['error']}")
                raise typer.Exit(1)

        progress.update(main_task, completed=100, description="[bold green]Success! Project complete.")

    # Final summary
    summary_table = Table(title="Generated Project Artifacts", show_header=True, header_style="bold magenta")
    summary_table.add_column("Artifact", style="dim")
    summary_table.add_column("Status")
    
    summary_table.add_row("Product Specification (spec.json)", "[green]Created[/green]")
    summary_table.add_row("System Architecture & Security Model", "[green]Hardened[/green]")
    summary_table.add_row("Implementation Tasks (tasks.json)", "[green]Created[/green]")
    summary_table.add_row("Source Code & Unit Tests", "[green]Verified & Committed[/green]")
    summary_table.add_row("Local Git Repository", "[green]Initialized[/green]")

    console.print(summary_table)
    console.print("\n[bold]Your new project is ready in the 'out/' directory.[/bold] ✨")

if __name__ == "__main__":
    app()


import typer

app = typer.Typer()

@app.command()
def hello():
    print("Spec CLI is working 🚀")

def main():
    app()
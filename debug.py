import typer  # type: ignore
import inspect


def debug_mode(debug: bool = False):
    if not debug:
        return
    try:
        import snoop  # type: ignore
    except ImportError:
        typer.echo("Debug mode requires the snoop package")
        raise typer.Exit(1)
    else:
        snoop.install(
            snoop="ss",
        )
    typer.echo(f"Debug mode enabled: {inspect.stack()[1].filename}")

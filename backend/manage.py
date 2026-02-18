import click
from flask.cli import with_appcontext
from backend import create_app
from backend.models import db


app = create_app()


@click.command("create-db")
@with_appcontext
def create_db():
    """Create database tables (SQLAlchemy create_all)."""
    db.create_all()
    click.echo("Database tables created.")


@click.command("drop-db")
@with_appcontext
def drop_db():
    """Drop all database tables."""
    db.drop_all()
    click.echo("Database tables dropped.")


def register_commands(app):
    app.cli.add_command(create_db)
    app.cli.add_command(drop_db)


if __name__ == "__main__":
    register_commands(app)
    app.run(host="0.0.0.0", port=5000)

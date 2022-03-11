import sqlite3

import click
from flask import current_app, g, Flask
from flask.cli import with_appcontext


def get_db_connection():
    # g is a special object unique for each request
    if 'db_connection' not in g:
        g.db_connection = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db_connection.row_factory = sqlite3.Row
    return g.db_connection


def close_db_connection(e=None):
    db_connection = g.pop('db_connection', None)
    if db_connection:
        db_connection.close()


def init_db():
    db_connection = get_db_connection()
    with current_app.open_resource('schema.sql') as schema_file:
        db_connection.executescript(schema_file.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('DB initialized')


def init_app(app: Flask):
    app.teardown_appcontext(close_db_connection)
    app.cli.add_command(init_db_command)

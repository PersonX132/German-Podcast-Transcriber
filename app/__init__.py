import os
import click
from flask import Flask
from flask.cli import with_appcontext

from app.models import db
from app.routes import main_routes
def create_app():
    app = Flask(__name__, instance_relative_config=True)
  
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    secret_key = os.environ.get('SECRET_KEY', 'fallback') # Load from environment variables, uses fallback as a fallback
    app.config.from_mapping(
        SECRET_KEY=secret_key,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(basedir, 'library.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(basedir, 'temp_uploads'),
        AUDIO_LIBRARY_FOLDER=os.path.join(basedir, 'audio_library')
    )

    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['AUDIO_LIBRARY_FOLDER'], exist_ok=True)
    except OSError:
        pass

    db.init_app(app)

    app.register_blueprint(main_routes)

    @click.command('init-db')
    @with_appcontext
    def init_db_command():
        db.create_all()
        click.echo('Initialized the database.')
    
    app.cli.add_command(init_db_command)

    return app

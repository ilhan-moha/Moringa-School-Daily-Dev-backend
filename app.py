from flask import Flask
from extensions import db, migrate, jwt, cors
from config import Config
from models import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    return app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
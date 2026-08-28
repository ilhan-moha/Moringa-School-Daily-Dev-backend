from flask import Flask
from extensions import db, migrate, jwt, cors
from config import Config
from models import User
from routes.auth_route import auth_bp


from routes.user_route import user_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)


    app.register_blueprint(user_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
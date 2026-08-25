from flask import Flask
from extensions import db, migrate, jwt, cors
from config import Config
from models import User
from routes.auth_route import auth_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    app.register_blueprint(auth_bp)

    @app.get("/test")
    def test():
        return {"message": "correct Flask app"}
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
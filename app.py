from flask import Flask
from config import Config
from extensions import db, bcrypt, jwt
import sys

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)
jwt_blocklist = set()  # Set to store revoked tokens

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload["jti"] in jwt_blocklist

# IMPORTANT: make "app" point to this running module
sys.modules["app"] = sys.modules[__name__]

import routes

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    print(app.url_map)

    app.run(debug=True)
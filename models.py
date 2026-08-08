from datetime import datetime, UTC
from extensions import db, bcrypt


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(128), nullable=False)

    role = db.Column(
        db.String(20),
        nullable=False,
        default="user"
    )



    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.username}>"


class PasswordResetOTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    otp = db.Column(
        db.String(6),
        nullable=False
    )

    expires_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False
    )

    is_used = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    user = db.relationship(
        "User",
        backref="password_reset_otps"
    )

    def __repr__(self):
        return f"<PasswordResetOTP {self.user_id}>"
import random
from datetime import datetime, timedelta, UTC
from models import User, PasswordResetOTP
from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
from app import app, jwt_blocklist
from extensions import db, bcrypt
from utils.validators import is_strong_password
from utils.decorators import admin_required

@app.route("/")
def home():
    return jsonify({
        "message": "Secure Authentication System API is running!"
    })


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"msg": "Missing username, email, or password"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists"}), 409

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201

# ... rest of your routes ...
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():

    current_user = get_jwt_identity()

    new_access_token = create_access_token(identity=current_user)

    return jsonify({
        "access_token": new_access_token
    }), 200

@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():

    jti = get_jwt()["jti"]

    jwt_blocklist.add(jti)

    return jsonify({
        "msg": "Successfully logged out"
    }), 200


@app.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():

    current_user_id = int(get_jwt_identity())

    user = db.session.get(User, current_user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json()

    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not old_password or not new_password:
        return jsonify({"msg": "Both old and new passwords are required"}), 400

    if not user.check_password(old_password):
        return jsonify({"msg": "Old password is incorrect"}), 401

    if not is_strong_password(new_password):
        return jsonify({
            "msg": "Password must be at least 8 characters long and include uppercase, lowercase, number, and special character."
        }), 400

    user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")

    db.session.commit()

    return jsonify({
        "msg": "Password changed successfully"
    }), 200

@app.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():

    current_user_id = int(get_jwt_identity())

    user = db.session.get(User, current_user_id)

    if not user:
        return jsonify({
            "msg": "User not found"
        }), 404

    return jsonify({
    "id": user.id,
    "username": user.username,
    "email": user.email,
    "role": user.role
}), 200

@app.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():

    current_user_id = int(get_jwt_identity())

    user = db.session.get(User, current_user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")

    # Check username uniqueness
    if username:
        existing_user = User.query.filter_by(username=username).first()

        if existing_user and existing_user.id != user.id:
            return jsonify({
                "msg": "Username already exists"
            }), 409

        user.username = username

    # Check email uniqueness
    if email:
        existing_email = User.query.filter_by(email=email).first()

        if existing_email and existing_email.id != user.id:
            return jsonify({
                "msg": "Email already exists"
            }), 409

        user.email = email

    db.session.commit()

    return jsonify({
        "msg": "Profile updated successfully"
    }), 200

@app.route("/profile", methods=["DELETE"])
@jwt_required()
def delete_profile():

    current_user_id = int(get_jwt_identity())

    user = db.session.get(User, current_user_id)

    if not user:
        return jsonify({
            "msg": "User not found"
        }), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "msg": "Account deleted successfully"
    }), 200

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = int(get_jwt_identity())
    user = db.session.get(User, current_user_id)

    return jsonify({
        "msg": f"Hello, {user.username}! You have access to protected data."
    }), 200

@app.route("/forgot-password", methods=["POST"])
def forgot_password():

    data = request.get_json()

    email = data.get("email")

    if not email:
        return jsonify({
            "msg": "Email is required"
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "msg": "No account found with this email"
        }), 404

    # Generate a random 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # OTP expires after 5 minutes
    expires_at = datetime.now(UTC) + timedelta(minutes=5)

    password_otp = PasswordResetOTP(
        user_id=user.id,
        otp=otp,
        expires_at=expires_at
    )

    db.session.add(password_otp)
    db.session.commit()

    # For now, return the OTP.
    # Later we'll send it via email.
    return jsonify({
        "msg": "OTP generated successfully",
        "otp": otp
    }), 200

@app.route("/verify-otp", methods=["POST"])
def verify_otp():

    data = request.get_json()

    email = data.get("email")
    otp = data.get("otp")

    if not email or not otp:
        return jsonify({
            "msg": "Email and OTP are required"
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "msg": "User not found"
        }), 404

    password_otp = PasswordResetOTP.query.filter_by(
        user_id=user.id,
        otp=otp,
        is_used=False
    ).first()

    if not password_otp:
        return jsonify({
            "msg": "Invalid OTP"
        }), 400

    if password_otp.expires_at < datetime.now(UTC):
        return jsonify({
            "msg": "OTP has expired"
        }), 400

    return jsonify({
        "msg": "OTP verified successfully"
    }), 200

@app.route("/reset-password", methods=["POST"])
def reset_password():

    data = request.get_json()

    email = data.get("email")
    otp = data.get("otp")
    new_password = data.get("new_password")

    if not email or not otp or not new_password:
        return jsonify({
            "msg": "Email, OTP and new password are required"
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "msg": "User not found"
        }), 404

    password_otp = PasswordResetOTP.query.filter_by(
        user_id=user.id,
        otp=otp,
        is_used=False
    ).first()

    if not password_otp:
        return jsonify({
            "msg": "Invalid OTP"
        }), 400

    if password_otp.expires_at < datetime.now(UTC):
        return jsonify({
            "msg": "OTP has expired"
        }), 400

    # Hash the new password
    user.password = bcrypt.generate_password_hash(
        new_password
    ).decode("utf-8")

    # Mark OTP as used
    password_otp.is_used = True

    db.session.commit()

    return jsonify({
        "msg": "Password reset successfully"
    }), 200

@app.route("/admin/users", methods=["GET"])
@admin_required
def get_all_users():

    users = User.query.all()

    data = []

    for user in users:
        data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        })

    return jsonify(data), 200

@app.route("/admin/users/<int:user_id>/role", methods=["PUT"])
@admin_required
def update_user_role(user_id):

    data = request.get_json()

    role = data.get("role")

    if role not in ["admin", "user"]:
        return jsonify({
            "msg": "Role must be 'admin' or 'user'"
        }), 400

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            "msg": "User not found"
        }), 404

    user.role = role

    db.session.commit()

    return jsonify({
        "msg": f"{user.username} is now {role}"
    }), 200

@app.route("/admin/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            "msg": "User not found"
        }), 404

    if user.role == "admin":
        return jsonify({
            "msg": "Cannot delete another admin"
        }), 403

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "msg": f"{user.username} deleted successfully"
    }), 200
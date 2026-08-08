from functools import wraps

from flask import jsonify
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_identity,
)
from extensions import db
from models import User


def admin_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):

        verify_jwt_in_request()

        current_user_id = get_jwt_identity()

        user = db.session.get(User, int(current_user_id))

        if not user:
            return jsonify({
                "msg": "User not found"
            }), 404

        if user.role != "admin":
            return jsonify({
                "msg": "Admins only"
            }), 403

        return fn(*args, **kwargs)

    return wrapper
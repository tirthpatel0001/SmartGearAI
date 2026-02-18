from flask import Blueprint, jsonify, request
from .models import db, User
from .config import Config
import jwt
import datetime

api_bp = Blueprint("api", __name__)


@api_bp.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "sgmas-backend"})


@api_bp.route("/users", methods=["GET"])
def list_users():
    users = User.query.all()
    return jsonify([u.as_dict() for u in users])


@api_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    if not username or not email:
        return jsonify({"error": "username and email required"}), 400

    if not password:
        return jsonify({"error": "password required"}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "user exists"}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.as_dict()), 201



@api_bp.route('/auth/signup', methods=['POST'])
def auth_signup():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')
    if not username or not email or not password:
        return jsonify({'error': 'username, email and password required'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'user exists'}), 409

    # New users with roles other than 'user' require admin approval
    approved = True if role == 'user' else False
    user = User(username=username, email=email, role=role, is_approved=approved)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    if not approved:
        return jsonify({'msg': 'signup_pending', 'user': user.as_dict()}), 201
    return jsonify({'msg': 'user created', 'user': user.as_dict()}), 201


@api_bp.route('/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400

    user = User.query.filter((User.username == username) | (User.email == username)).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'invalid credentials'}), 401

    # Deny login if user requires approval
    if user.role != 'user' and not user.is_approved:
        return jsonify({'error': 'account pending approval'}), 403

    payload = {
        'sub': str(user.id),
        'username': user.username,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)

    user_data = user.as_dict()
    user_data['role'] = user.role
    user_data['is_approved'] = user.is_approved

    return jsonify({'access_token': token, 'user': user_data})


def _require_admin_from_token():
    import sys
    auth = request.headers.get('Authorization', None)
    print(f"DEBUG: Authorization header = {auth[:50] if auth else 'None'}...", file=sys.stderr)
    
    if not auth or not auth.startswith('Bearer '):
        print(f"DEBUG: No valid Authorization header", file=sys.stderr)
        return None
    token = auth.split(' ', 1)[1]
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        print(f"DEBUG: Token decoded. Payload: {payload}", file=sys.stderr)
    except Exception as e:
        print(f"DEBUG: Token decode failed: {e}", file=sys.stderr)
        return None
    uid = int(payload.get('sub'))
    print(f"DEBUG: Looking up user ID {uid}", file=sys.stderr)
    user = User.query.get(uid)
    print(f"DEBUG: Query result: {user}", file=sys.stderr)
    return user


@api_bp.route('/admin/pending', methods=['GET'])
def admin_pending():
    admin_user = _require_admin_from_token()
    
    # Debug logging
    import sys
    print(f"DEBUG: admin_user = {admin_user}", file=sys.stderr)
    if admin_user:
        print(f"DEBUG: admin_user.role = {admin_user.role}", file=sys.stderr)
        print(f"DEBUG: admin_user.id = {admin_user.id}", file=sys.stderr)
    
    if not admin_user or admin_user.role != 'admin':
        return jsonify({'error': 'admin required'}), 403

    pending = User.query.filter(User.is_approved == False).all()
    return jsonify([{"id": u.id, "username": u.username, "email": u.email, "role": u.role} for u in pending])


@api_bp.route('/admin/approve/<int:user_id>', methods=['POST'])
def admin_approve(user_id):
    admin_user = _require_admin_from_token()
    if not admin_user or admin_user.role != 'admin':
        return jsonify({'error': 'admin required'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'not found'}), 404
    user.is_approved = True
    db.session.commit()
    return jsonify({'msg': 'approved'})


@api_bp.route('/admin/reject/<int:user_id>', methods=['POST'])
def admin_reject(user_id):
    admin_user = _require_admin_from_token()
    if not admin_user or admin_user.role != 'admin':
        return jsonify({'error': 'admin required'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'msg': 'rejected'})


@api_bp.route('/admin/heads', methods=['GET'])
def admin_heads():
    admin_user = _require_admin_from_token()
    if not admin_user or admin_user.role != 'admin':
        return jsonify({'error': 'admin required'}), 403

    heads = User.query.filter(User.role.in_(['inventory_head', 'maintenance_head', 'production_head'])).all()
    return jsonify([{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "role": u.role,
        "is_approved": u.is_approved,
        "created_at": str(u.created_at)
    } for u in heads])

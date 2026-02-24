from flask import Blueprint, jsonify, request
from .models import (
    db,
    User,
    InventoryItem,
    MaterialRequest,
    MaterialRequestItem,
    PurchaseRequest,
    PurchaseRequestItem,
    PurchaseOrder,
    PurchaseOrderItem,
    ScrapRecord,
    Notification,
)
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

    # include scm head/planner/purchaser when listing department heads
    roles_to_include = [
        'inventory_head',
        'maintenance_head',
        'production_head',
        'scm_head',
        'scm_planner',
        'scm_purchaser'
    ]
    heads = User.query.filter(User.role.in_(roles_to_include)).all()
    return jsonify([{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "role": u.role,
        "is_approved": u.is_approved,
        "created_at": str(u.created_at)
    } for u in heads])


# ---------------- SCM / Inventory API ----------------


@api_bp.route('/inventory/items', methods=['GET'])
def get_inventory_items():
    # return items sorted by code for consistency
    items = InventoryItem.query.order_by(InventoryItem.item_code).all()
    return jsonify([i.as_dict() for i in items])


@api_bp.route('/inventory/items', methods=['POST'])
def create_inventory_item():
    # any authenticated head can add/update inventory
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    if user.role not in ('inventory_head', 'scm_head'):
        return jsonify({'error': 'insufficient permissions'}), 403

    data = request.get_json() or {}
    item_code = data.get('item_code')
    name = data.get('name')
    qty = data.get('quantity', 0)
    category = data.get('category')

    # require name for any operation
    if not name:
        return jsonify({'error': 'name required'}), 400

    # if code is provided try to find by code
    existing = None
    if item_code:
        existing = InventoryItem.query.filter_by(item_code=item_code).first()
    # if we didn't find by code and a name exists, use name lookup (backwards compatibility)
    if not existing:
        existing = InventoryItem.query.filter_by(name=name).first()

    if existing:
        # update existing record; set code if provided
        if item_code:
            existing.item_code = item_code
        existing.name = name
        existing.quantity = qty
        if category is not None:
            existing.category = category
        db.session.commit()
        return jsonify(existing.as_dict()), 200

    # creating new item requires code
    if not item_code:
        return jsonify({'error': 'item_code required for new item'}), 400

    item = InventoryItem(item_code=item_code, name=name, quantity=qty, category=category)
    db.session.add(item)
    db.session.commit()
    return jsonify(item.as_dict()), 201


@api_bp.route('/material_requests', methods=['GET'])
def list_material_requests():
    # inventory head, scm head, production head or scm planner can view
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    if user.role not in ('inventory_head', 'scm_head', 'production_head', 'scm_planner'):
        return jsonify({'error': 'insufficient permissions'}), 403
    reqs = MaterialRequest.query.all()
    return jsonify([r.as_dict() for r in reqs])


def _ensure_material_request_schema():
    """Make sure the material_requests table has the latest columns.

    This duplicates a subset of the startup migration logic so that if a
    request is handled before the app has been restarted after a model change,
    we can still recover gracefully.
    """
    from sqlalchemy import inspect
    insp = inspect(db.engine)  # fresh inspector
    if 'material_requests' in insp.get_table_names():
        cols = [c['name'] for c in insp.get_columns('material_requests')]
        if 'processed_by' not in cols:
            db.engine.execute('ALTER TABLE material_requests ADD COLUMN processed_by INT NULL')
        if 'processed_at' not in cols:
            db.engine.execute('ALTER TABLE material_requests ADD COLUMN processed_at DATETIME NULL')


@api_bp.route('/material_requests', methods=['POST'])
def create_material_request():
    # only production head (manufacturing department) can create a material request
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    if user.role != 'production_head':
        return jsonify({'error': 'only production head can request materials'}), 403

    data = request.get_json() or {}
    department = data.get('department')
    requested_by = data.get('requested_by')
    items = data.get('items', [])
    if not department or not requested_by:
        return jsonify({'error': 'department and requested_by required'}), 400

    # guard for missing schema columns before doing the insert
    try:
        _ensure_material_request_schema()
    except Exception:
        # ignore; later insert may still fail and the error will bubble
        pass

    # create material request record without touching inventory yet
    mr = MaterialRequest(department=department, requested_by=requested_by)
    db.session.add(mr)
    try:
        db.session.flush()  # get id without commit
    except Exception as exc:
        # any operational errors are likely due to missing columns; inform the
        # user and encourage a restart which will trigger our schema update
        from sqlalchemy.exc import OperationalError
        if isinstance(exc, OperationalError):
            db.session.rollback()
            return jsonify({'error': 'database schema out of date, restart backend'}), 500
        raise

    # evaluate availability but do not alter inventory until later approval
    result = {'available': [], 'to_order': []}
    for it in items:
        item_id = it.get('item_id')
        qty = it.get('quantity', 0)
        inv = InventoryItem.query.get(item_id)
        name = inv.name if inv else it.get('item_name', '')
        mr_item = MaterialRequestItem(
            request_id=mr.id,
            item_id=item_id,
            item_name=name,
            quantity=qty,
        )
        if inv:
            take = min(inv.quantity, qty)
            mr_item.quantity_allocated = take
            mr_item.quantity_to_order = max(0, qty - take)
            if take > 0:
                result['available'].append({'item_id': inv.id, 'item_name': inv.name, 'quantity': take})
            if qty - take > 0:
                result['to_order'].append({'item_id': inv.id, 'item_name': inv.name, 'quantity': qty - take})
        else:
            mr_item.quantity_allocated = 0
            mr_item.quantity_to_order = qty
            result['to_order'].append({'item_id': item_id, 'item_name': name, 'quantity': qty})
        mr.items.append(mr_item)
    db.session.commit()

    # AUTO-CREATE PURCHASE REQUESTS for items that need to be ordered
    if result.get('to_order'):
        pr = PurchaseRequest(material_request_id=mr.id, created_by=requested_by, status='pending')
        for to_order_item in result['to_order']:
            pr_item = PurchaseRequestItem(
                item_name=to_order_item.get('item_name'),
                quantity=to_order_item.get('quantity', 0)
            )
            pr.items.append(pr_item)
        db.session.add(pr)
        db.session.commit()

    # create notifications for inventory heads and scm planners
    inv_heads = User.query.filter(User.role == 'inventory_head').all()
    for ih in inv_heads:
        n = Notification(user_id=ih.id,
                         message=f"New material request {mr.id} needs review",
                         related_type="MR", related_id=mr.id)
        db.session.add(n)
    if result.get('to_order'):
        planners = User.query.filter(User.role == 'scm_planner').all()
        for pl in planners:
            n = Notification(user_id=pl.id,
                             message=f"Purchase request created for material request {mr.id}",
                             related_type="PR", related_id=mr.id)
            db.session.add(n)
    db.session.commit()

    return jsonify({'material_request': mr.as_dict(), 'result': result}), 201


@api_bp.route('/material_requests/<int:req_id>/process', methods=['POST'])
def process_material_request(req_id):
    # inventory head or scm head processes request
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    if user.role not in ('inventory_head', 'scm_head'):
        return jsonify({'error': 'insufficient permissions'}), 403

    mr = MaterialRequest.query.get(req_id)
    if not mr:
        return jsonify({'error': 'not found'}), 404

    result = {'available': [], 'to_order': []}
    # deduct inventory only for items that had been allocated earlier
    for it in mr.items:
        inv = InventoryItem.query.get(it.item_id)
        allocated = it.quantity_allocated or 0
        if allocated > 0 and inv:
            take = min(inv.quantity, allocated)
            inv.quantity -= take
            it.status = 'allocated'
            result['available'].append({
                'item_id': inv.id,
                'item_name': inv.name,
                'quantity': take,
            })
        # any remaining to_order already recorded on creation
        if it.quantity_to_order and it.quantity_to_order > 0:
            it.status = 'to_order'
            result['to_order'].append({
                'item_id': it.item_id,
                'item_name': it.item_name,
                'quantity': it.quantity_to_order,
            })
    mr.status = 'inventory_approved'
    mr.processed_by = user.id
    mr.processed_at = datetime.datetime.utcnow()

    # if scm_head processed and there are missing items - auto create a purchase request
    if user.role == 'scm_head' and result.get('to_order'):
        pr = PurchaseRequest(material_request_id=mr.id, created_by=user.id)
        for item in result['to_order']:
            pr.items.append(PurchaseRequestItem(item_name=item['item_name'], quantity=item['quantity']))
        db.session.add(pr)

    # send notification back to production head
    req_user = User.query.get(mr.requested_by)
    if req_user:
        msg = f"Material request {mr.id} has been processed. "
        if result.get('available'):
            msg += "Items are ready to dispatch. "
        if result.get('to_order'):
            msg += "Some items will be ordered via SCM."
        n = Notification(user_id=req_user.id, message=msg, related_type="MR", related_id=mr.id)
        db.session.add(n)

    db.session.commit()
    return jsonify(result)


@api_bp.route('/purchase_requests', methods=['GET'])
def list_purchase_requests():
    # scm planner, scm head or scm purchaser can view
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    if user.role not in ('scm_planner', 'scm_head', 'scm_purchaser'):
        return jsonify({'error': 'insufficient permissions'}), 403
    prs = PurchaseRequest.query.all()
    return jsonify([p.as_dict() for p in prs])


@api_bp.route('/purchase_requests/assigned', methods=['GET'])
def list_assigned_purchase_requests():
    """Get purchase requests assigned to the logged-in user's email"""
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    if user.role != 'scm_purchaser':
        return jsonify({'error': 'insufficient permissions'}), 403
    # Get PRs where purchaser_email matches the logged-in user's email
    prs = PurchaseRequest.query.filter_by(purchaser_email=user.email).all()
    return jsonify([p.as_dict() for p in prs])


@api_bp.route('/purchase_requests', methods=['POST'])
def create_purchase_request():
    # only SCM planner (or head) can raise a purchase request
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    if user.role not in ('scm_planner', 'scm_head'):
        return jsonify({'error': 'insufficient permissions'}), 403

    data = request.get_json() or {}
    mr_id = data.get('material_request_id')
    created_by = data.get('created_by')
    items = data.get('items', [])
    status = data.get('status')
    purchaser_email = data.get('purchaser_email')
    if not created_by:
        return jsonify({'error': 'created_by required'}), 400
    pr = PurchaseRequest(material_request_id=mr_id, created_by=created_by)
    if purchaser_email:
        pr.purchaser_email = purchaser_email
    # allow planner to pre-set status (e.g. submitted)
    if status and user.role == 'scm_planner':
        pr.status = status
    for it in items:
        pr.items.append(PurchaseRequestItem(item_name=it.get('item_name'), quantity=it.get('quantity', 0)))
    db.session.add(pr)
    db.session.commit()
    return jsonify(pr.as_dict()), 201


@api_bp.route('/notifications', methods=['GET'])
def list_notifications():
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    notes = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()
    return jsonify([n.as_dict() for n in notes])


@api_bp.route('/notifications/<int:note_id>/read', methods=['POST'])
def read_notification(note_id):
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    n = Notification.query.get(note_id)
    if not n or n.user_id != user.id:
        return jsonify({'error': 'not found'}), 404
    n.seen = True
    db.session.commit()
    return jsonify(n.as_dict())


@api_bp.route('/purchase_requests/<int:pr_id>/submit', methods=['POST'])
def submit_purchase_request(pr_id):
    """Mark a purchase request as submitted so the purchaser can act on it."""
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    if user.role not in ('scm_planner', 'scm_head'):
        return jsonify({'error': 'insufficient permissions'}), 403

    pr = PurchaseRequest.query.get(pr_id)
    if not pr:
        return jsonify({'error': 'not found'}), 404
    if pr.status != 'draft':
        return jsonify({'error': 'cannot submit non-draft request'}), 400
    pr.status = 'submitted'
    db.session.commit()
    return jsonify(pr.as_dict())


@api_bp.route('/purchase_requests/<int:pr_id>', methods=['DELETE'])
def delete_purchase_request(pr_id):
    """Delete a purchase request (only draft requests can be deleted)."""
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    if user.role not in ('scm_planner', 'scm_head'):
        return jsonify({'error': 'insufficient permissions'}), 403

    pr = PurchaseRequest.query.get(pr_id)
    if not pr:
        return jsonify({'error': 'not found'}), 404
    
    db.session.delete(pr)
    db.session.commit()
    return jsonify({'message': 'purchase request deleted'}), 200


@api_bp.route('/purchase_requests/all', methods=['DELETE'])
def delete_all_purchase_requests():
    """Delete all purchase requests."""
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    if user.role not in ('scm_planner', 'scm_head'):
        return jsonify({'error': 'insufficient permissions'}), 403

    prs = PurchaseRequest.query.all()
    for pr in prs:
        db.session.delete(pr)
    db.session.commit()
    return jsonify({'message': f'deleted {len(prs)} purchase requests'}), 200


@api_bp.route('/purchase_requests/<int:pr_id>/status', methods=['PATCH'])
def update_purchase_request_status(pr_id):
    """Update purchase request status and/or purchaser_email"""
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    if user.role not in ('scm_planner', 'scm_head', 'scm_purchaser'):
        return jsonify({'error': 'insufficient permissions'}), 403

    pr = PurchaseRequest.query.get(pr_id)
    if not pr:
        return jsonify({'error': 'not found'}), 404
    
    data = request.get_json() or {}
    new_status = data.get('status')
    purchaser_email = data.get('purchaser_email')
    
    if new_status:
        pr.status = new_status
    if purchaser_email:
        pr.purchaser_email = purchaser_email
    
    db.session.commit()
    return jsonify(pr.as_dict())


@api_bp.route('/purchase_orders', methods=['GET'])
def list_purchase_orders():
    # only scm purchaser, scm planner, or scm head can view
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    if user.role not in ('scm_purchaser', 'scm_head', 'scm_planner'):
        return jsonify({'error': 'insufficient permissions'}), 403
    pos = PurchaseOrder.query.all()
    return jsonify([p.as_dict() for p in pos])


@api_bp.route('/purchase_orders', methods=['POST'])
def create_purchase_order():
    # only SCM purchaser (or head) can create a purchase order
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    if user.role not in ('scm_purchaser', 'scm_head'):
        return jsonify({'error': 'insufficient permissions'}), 403

    data = request.get_json() or {}
    pr_id = data.get('purchase_request_id')
    created_by = data.get('created_by')
    vendor = data.get('vendor')
    items = data.get('items', [])
    if not created_by or not pr_id:
        return jsonify({'error': 'purchase_request_id and created_by required'}), 400
    po = PurchaseOrder(purchase_request_id=pr_id, created_by=created_by, vendor=vendor)
    for it in items:
        po.items.append(PurchaseOrderItem(item_name=it.get('item_name'), quantity=it.get('quantity', 0)))
    db.session.add(po)
    db.session.commit()
    return jsonify(po.as_dict()), 201


@api_bp.route('/purchase_orders/<int:po_id>/receive', methods=['POST'])
def receive_purchase_order(po_id):
    """Mark a purchase order as received and update inventory accordingly.
    Only SCM purchaser or SCM head may perform this action.

    When the order is received we increment the quantities of the
    corresponding inventory items.  If an inventory item with the same
    name does not already exist we create a new record using a simple
    autogenerated code.

    We also transition related material/purchase requests to indicate
    the work is complete.
    """
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    if user.role not in ('scm_purchaser', 'scm_head'):
        return jsonify({'error': 'insufficient permissions'}), 403

    po = PurchaseOrder.query.get(po_id)
    if not po:
        return jsonify({'error': 'not found'}), 404
    if po.status != 'open':
        return jsonify({'error': 'order already processed'}), 400

    # update inventory quantities
    for item in po.items:
        inv = InventoryItem.query.filter_by(name=item.item_name).first()
        if not inv:
            # generate a crude item_code if missing; ensure uniqueness by
            # appending the new item's database id after committing below.
            inv = InventoryItem(item_code=f"AUTO-{item.item_name[:8].upper()}",
                                name=item.item_name,
                                quantity=0.0)
            db.session.add(inv)
            # commit now so we can reference inv.id if needed later
            db.session.flush()
            inv.item_code = inv.item_code + f"-{inv.id}"
        inv.quantity = (inv.quantity or 0.0) + item.quantity

    # mark PO received
    po.status = 'received'

    # if there is a linked purchase request / material request, advance
    # their statuses
    pr = None
    if po.purchase_request:
        pr = po.purchase_request
        pr.status = 'approved'
        if pr.material_request:
            mr = pr.material_request
            mr.status = 'fulfilled'
    db.session.commit()
    return jsonify(po.as_dict())


@api_bp.route('/scrap_records', methods=['GET'])
def list_scrap_records():
    # any authorized head can view scrap records
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    if user.role not in ('inventory_head', 'production_head', 'scm_head', 'scm_planner'):
        return jsonify({'error': 'insufficient permissions'}), 403
    recs = ScrapRecord.query.all()
    return jsonify([r.as_dict() for r in recs])


@api_bp.route('/scrap_records', methods=['POST'])
def create_scrap_record():
    # any authenticated head can report scrap
    user = _require_admin_from_token()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    # allow inventory_head, production_head, scm_head, scm_planner
    if user.role not in ('inventory_head', 'production_head', 'scm_head', 'scm_planner'):
        return jsonify({'error': 'insufficient permissions'}), 403

    data = request.get_json() or {}
    department = data.get('department')
    description = data.get('description')
    quantity = data.get('quantity')
    created_by = data.get('created_by')
    if not department or not description or quantity is None or not created_by:
        return jsonify({'error': 'department, description, quantity and created_by required'}), 400
    rec = ScrapRecord(department=department, description=description, quantity=quantity, created_by=created_by)
    db.session.add(rec)
    db.session.commit()
    return jsonify(rec.as_dict()), 201

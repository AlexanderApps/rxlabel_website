from functools import wraps
from flask import (
    Blueprint, render_template, request,
    jsonify, session, redirect, url_for, current_app,
)
from ..extensions    import db
from ..email_service import send_invoice

admin_bp = Blueprint('admin', __name__)


# ── AUTH ──────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    error = None
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        if (u == current_app.config['ADMIN_USERNAME'] and
                p == current_app.config['ADMIN_PASSWORD']):
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        error = 'Invalid username or password.'
    return render_template('admin/login.html', error=error)


@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))


# ── DASHBOARD ─────────────────────────────────────────────
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    total    = db.execute('SELECT COUNT(*) FROM license_requests').fetchone()[0]
    pending  = db.execute("SELECT COUNT(*) FROM license_requests WHERE status='pending'").fetchone()[0]
    approved = db.execute("SELECT COUNT(*) FROM license_requests WHERE status='approved'").fetchone()[0]
    rejected = db.execute("SELECT COUNT(*) FROM license_requests WHERE status='rejected'").fetchone()[0]
    recent   = db.execute('SELECT * FROM license_requests ORDER BY submitted_at DESC LIMIT 5').fetchall()
    by_type  = db.execute(
        'SELECT license_type, COUNT(*) as cnt FROM license_requests GROUP BY license_type ORDER BY cnt DESC'
    ).fetchall()
    mail_configured = bool(current_app.config.get('MAIL_USERNAME'))
    return render_template('admin/dashboard.html',
                           total=total, pending=pending, approved=approved, rejected=rejected,
                           recent=recent, by_type=by_type, mail_configured=mail_configured)


# ── REQUESTS LIST ─────────────────────────────────────────
@admin_bp.route('/requests')
@login_required
def requests_list():
    sf = request.args.get('status', '')
    if sf in ('pending', 'approved', 'rejected'):
        rows = db.execute(
            'SELECT * FROM license_requests WHERE status=? ORDER BY submitted_at DESC', (sf,)
        ).fetchall()
    else:
        rows = db.execute('SELECT * FROM license_requests ORDER BY submitted_at DESC').fetchall()
    return render_template('admin/requests.html', requests=rows, status_filter=sf)


# ── UPDATE STATUS ─────────────────────────────────────────
@admin_bp.route('/requests/<int:req_id>/status', methods=['POST'])
@login_required
def update_status(req_id):
    data   = request.get_json(silent=True)
    status = data.get('status') if data else None
    if status not in ('pending', 'approved', 'rejected'):
        return jsonify({'success': False, 'message': 'Invalid status.'}), 400
    db.execute('UPDATE license_requests SET status=? WHERE id=?', (status, req_id))
    db.commit()
    return jsonify({'success': True})


# ── SEND INVOICE ──────────────────────────────────────────
@admin_bp.route('/requests/<int:req_id>/invoice', methods=['POST'])
@login_required
def send_invoice_route(req_id):
    row = db.execute('SELECT * FROM license_requests WHERE id=?', (req_id,)).fetchone()
    if not row:
        return jsonify({'success': False, 'message': 'Request not found.'}), 404
    data = request.get_json(silent=True) or {}
    for f in ['number', 'amount', 'currency', 'due_date', 'description']:
        if not data.get(f, '').strip():
            return jsonify({'success': False, 'message': f'{f} is required.'}), 400
    ok, err = send_invoice(dict(row), data)
    if ok:
        return jsonify({'success': True, 'message': f'Invoice sent to {row["facility_email"]}'})
    return jsonify({"success": False, "message": f"Email not sent: {err}"})

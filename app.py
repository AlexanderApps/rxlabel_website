from flask import Flask, render_template, request, jsonify, g
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(__file__), 'rxlabel.db')


# ── DATABASE ──────────────────────────────────────────────
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS license_requests (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                facility_name    TEXT NOT NULL,
                facility_contact TEXT NOT NULL,
                facility_address TEXT NOT NULL,
                facility_email   TEXT NOT NULL,
                license_type     TEXT NOT NULL,
                status           TEXT DEFAULT 'pending',
                submitted_at     TEXT NOT NULL
            )
        ''')
        db.commit()


# ── ROUTES ────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/request-license', methods=['POST'])
def request_license():
    data = request.get_json()
    required = ['facility_name', 'facility_contact', 'facility_address',
                 'facility_email', 'license_type']

    for field in required:
        if not data.get(field, '').strip():
            return jsonify({'success': False, 'message': f'{field} is required.'}), 400

    db = get_db()
    db.execute('''
        INSERT INTO license_requests
            (facility_name, facility_contact, facility_address, facility_email, license_type, submitted_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['facility_name'].strip(),
        data['facility_contact'].strip(),
        data['facility_address'].strip(),
        data['facility_email'].strip(),
        data['license_type'].strip(),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    db.commit()
    return jsonify({'success': True, 'message': 'License request submitted successfully!'})


@app.route('/admin/requests')
def admin_requests():
    db = get_db()
    rows = db.execute(
        'SELECT * FROM license_requests ORDER BY submitted_at DESC'
    ).fetchall()
    return render_template('admin.html', requests=rows)


@app.route('/admin/requests/<int:req_id>/status', methods=['POST'])
def update_status(req_id):
    data = request.get_json()
    status = data.get('status')
    if status not in ('pending', 'approved', 'rejected'):
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    db = get_db()
    db.execute('UPDATE license_requests SET status=? WHERE id=?', (status, req_id))
    db.commit()
    return jsonify({'success': True})


# ── MAIN ──────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(debug=True)

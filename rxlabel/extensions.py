import sqlite3
from flask import g, current_app


class _DB:
    """Thin wrapper that gives us a per-request SQLite connection."""

    def init_app(self, app):
        app.teardown_appcontext(self._close)
        with app.app_context():
            self._init_schema(app)

    # ── connection ──────────────────────────────────────────
    def get(self):
        conn = getattr(g, '_db', None)
        if conn is None:
            conn = g._db = sqlite3.connect(current_app.config['DATABASE'])
            conn.row_factory = sqlite3.Row
        return conn

    def _close(self, _exc):
        conn = getattr(g, '_db', None)
        if conn is not None:
            conn.close()

    # ── schema ───────────────────────────────────────────────
    def _init_schema(self, app):
        with app.app_context():
            conn = sqlite3.connect(app.config['DATABASE'])
            conn.execute('''
                CREATE TABLE IF NOT EXISTS license_requests (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    facility_name    TEXT    NOT NULL,
                    facility_contact TEXT    NOT NULL,
                    facility_address TEXT    NOT NULL,
                    facility_email   TEXT    NOT NULL,
                    license_type     TEXT    NOT NULL,
                    status           TEXT    NOT NULL DEFAULT 'pending',
                    submitted_at     TEXT    NOT NULL
                )
            ''')
            conn.commit()
            conn.close()

    # ── convenience ──────────────────────────────────────────
    def execute(self, sql, params=()):
        return self.get().execute(sql, params)

    def commit(self):
        self.get().commit()


db = _DB()

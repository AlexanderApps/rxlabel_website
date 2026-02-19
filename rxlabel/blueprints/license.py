from flask import Blueprint, request, jsonify
from datetime import datetime
from ..extensions import db
from ..email_service import send_license_request_notification, send_request_confirmation

license_bp = Blueprint("license", __name__)

REQUIRED_FIELDS = [
    "facility_name",
    "facility_contact",
    "facility_address",
    "facility_email",
    "license_type",
]

VALID_LICENSE_TYPES = {
    "Preorder – Starter Package",
    "Standard – Starter Package",
    "Enterprise – Multi-Facility",
}


@license_bp.route("/request-license", methods=["POST"])
def request_license():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Invalid request."}), 400

    for field in REQUIRED_FIELDS:
        if not data.get(field, "").strip():
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f'{field.replace("_"," ").title()} is required.',
                    }
                ),
                400,
            )

    if data["license_type"] not in VALID_LICENSE_TYPES:
        return jsonify({"success": False, "message": "Invalid license type."}), 400

    req = {k: data[k].strip() for k in REQUIRED_FIELDS}

    db.execute(
        """INSERT INTO license_requests
               (facility_name, facility_contact, facility_address,
                facility_email, license_type, submitted_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (*req.values(), datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    db.commit()

    # fire-and-forget emails (errors are logged but don't break the response)
    send_license_request_notification(req)
    send_request_confirmation(req)

    return jsonify(
        {
            "success": True,
            "message": "License request submitted! Check your email for confirmation.",
        }
    )

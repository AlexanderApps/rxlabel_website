"""
email_service.py
Thin wrapper around stdlib smtplib for sending transactional emails.
Works with Gmail (App Password) or any SMTP provider.

Config keys expected in app.config:
    MAIL_HOST       – SMTP host (default: smtp.gmail.com)
    MAIL_PORT       – SMTP port (default: 587)
    MAIL_USERNAME   – sender email address
    MAIL_PASSWORD   – app password / SMTP password
    MAIL_FROM_NAME  – display name (default: RxLabel)
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app

log = logging.getLogger(__name__)


def _get_cfg(key, default=None):
    return current_app.config.get(key, default)


def send_email(to: str | list, subject: str, html: str, text: str = ""):
    """
    Send an email. Returns (True, None) on success, (False, error_str) on failure.
    `to` can be a single address string or a list of addresses.
    """
    host = _get_cfg("MAIL_HOST", "smtp.gmail.com")
    port = _get_cfg("MAIL_PORT", 587)
    username = _get_cfg("MAIL_USERNAME", "")
    password = _get_cfg("MAIL_PASSWORD", "")
    name = _get_cfg("MAIL_FROM_NAME", "RxLabel")

    if not username or not password:
        log.warning(
            "Email not configured — skipping send (set MAIL_USERNAME / MAIL_PASSWORD)"
        )
        return False, "Email not configured."

    recipients = [to] if isinstance(to, str) else to

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{name} <{username}>"
    msg["To"] = ", ".join(recipients)

    if text:
        msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(host, port) as server:
            server.ehlo()
            server.starttls()
            server.login(username, password)
            server.sendmail(username, recipients, msg.as_string())
        log.info("Email sent to %s | %s", recipients, subject)
        return True, None
    except Exception as exc:
        log.error("Email failed: %s", exc)
        return False, str(exc)


# ── PRE-BUILT EMAIL TEMPLATES ────────────────────────────


def send_license_request_notification(req: dict):
    """Notify admin that a new license request came in."""
    admin_email = _get_cfg("MAIL_USERNAME", "")
    subject = f"[RxLabel] New License Request — {req['facility_name']}"
    html = f"""
    <div style="font-family:sans-serif;max-width:560px;margin:0 auto">
      <div style="background:#0d3b6e;padding:24px 32px;border-radius:10px 10px 0 0">
        <span style="font-size:1.3rem;font-weight:900;color:#F47C20">Rx</span>
        <span style="font-size:1.3rem;font-weight:900;color:white">Label</span>
        <span style="font-size:.85rem;color:rgba(255,255,255,.5);margin-left:12px">Admin Notification</span>
      </div>
      <div style="background:#f7f9fc;padding:28px 32px;border:1px solid #dde4f0;border-top:none">
        <h2 style="margin:0 0 16px;color:#0d3b6e;font-size:1.1rem">New License Request Received</h2>
        <table style="width:100%;border-collapse:collapse;font-size:.9rem">
          <tr><td style="padding:8px 0;color:#5a718a;width:140px">Facility</td>
              <td style="padding:8px 0;font-weight:600;color:#0f1f35">{req['facility_name']}</td></tr>
          <tr><td style="padding:8px 0;color:#5a718a">Contact</td>
              <td style="padding:8px 0;color:#0f1f35">{req['facility_contact']}</td></tr>
          <tr><td style="padding:8px 0;color:#5a718a">Email</td>
              <td style="padding:8px 0;color:#0f1f35">{req['facility_email']}</td></tr>
          <tr><td style="padding:8px 0;color:#5a718a">Address</td>
              <td style="padding:8px 0;color:#0f1f35">{req['facility_address']}</td></tr>
          <tr><td style="padding:8px 0;color:#5a718a">License</td>
              <td style="padding:8px 0"><span style="background:#e8f0fb;color:#1A5EA8;
                padding:3px 10px;border-radius:4px;font-weight:600;font-size:.82rem">
                {req['license_type']}</span></td></tr>
        </table>
        <div style="margin-top:24px">
          <a href="https://rxlabel.pythonanywhere.com/admin" style="background:#F47C20;color:white;padding:11px 24px;
            border-radius:50px;text-decoration:none;font-weight:600;font-size:.88rem">
            View in Admin Panel
          </a>
        </div>
      </div>
      <div style="padding:16px 32px;font-size:.78rem;color:#5a718a;text-align:center">
        RxLabel &mdash; rxlabelapp@gmail.com
      </div>
    </div>
    """
    return send_email(admin_email, subject, html)


def send_request_confirmation(req: dict):
    """Send confirmation to the facility that submitted the request."""
    subject = "We received your RxLabel license request"
    html = f"""
    <div style="font-family:sans-serif;max-width:560px;margin:0 auto">
      <div style="background:#0d3b6e;padding:24px 32px;border-radius:10px 10px 0 0">
        <span style="font-size:1.3rem;font-weight:900;color:#F47C20">Rx</span>
        <span style="font-size:1.3rem;font-weight:900;color:white">Label</span>
      </div>
      <div style="background:#f7f9fc;padding:28px 32px;border:1px solid #dde4f0;border-top:none">
        <h2 style="margin:0 0 8px;color:#0d3b6e">Thank you, {req['facility_name']}!</h2>
        <p style="color:#5a718a;font-size:.93rem;line-height:1.7;margin-bottom:20px">
          We've received your license request for <strong>{req['license_type']}</strong>.
          Our team will review it and get back to you shortly at
          <strong>{req['facility_email']}</strong>.
        </p>
        <div style="background:white;border:1px solid #dde4f0;border-radius:10px;padding:20px">
          <div style="font-size:.75rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
            color:#F47C20;margin-bottom:12px">Your Request Summary</div>
          <table style="width:100%;border-collapse:collapse;font-size:.88rem">
            <tr><td style="padding:6px 0;color:#5a718a;width:120px">Facility</td>
                <td style="padding:6px 0;font-weight:600">{req['facility_name']}</td></tr>
            <tr><td style="padding:6px 0;color:#5a718a">License</td>
                <td style="padding:6px 0">{req['license_type']}</td></tr>
            <tr><td style="padding:6px 0;color:#5a718a">Contact</td>
                <td style="padding:6px 0">{req['facility_contact']}</td></tr>
          </table>
        </div>
        <p style="color:#5a718a;font-size:.85rem;margin-top:20px">
          Questions? Reply to this email or call us at <strong>+233 555 276 832</strong>.
        </p>
      </div>
      <div style="padding:16px 32px;font-size:.78rem;color:#5a718a;text-align:center">
        &copy; 2026 RxLabel &mdash; Clarity in every dose.
      </div>
    </div>
    """
    return send_email(req["facility_email"], subject, html)


# def send_invoice(req: dict, invoice: dict):
#     """
#     Send a payment request / invoice to the facility.
#     invoice dict: { number, amount, currency, due_date, description, notes }
#     """
#     subject = f"[RxLabel] Invoice #{invoice['number']} — {invoice['amount']} {invoice['currency']}"
#     notes_row = (
#         f"""
#       <tr><td colspan="2" style="padding:12px 0 4px">
#         <div style="font-size:.82rem;color:#5a718a;font-style:italic">{invoice.get('notes','')}</div>
#       </td></tr>"""
#         if invoice.get("notes")
#         else ""
#     )

#     html = f"""
#     <div style="font-family:sans-serif;max-width:600px;margin:0 auto">
#       <div style="background:#0d3b6e;padding:24px 32px;border-radius:10px 10px 0 0;
#         display:flex;justify-content:space-between;align-items:center">
#         <div>
#           <span style="font-size:1.3rem;font-weight:900;color:#F47C20">Rx</span>
#           <span style="font-size:1.3rem;font-weight:900;color:white">Label</span>
#         </div>
#         <div style="text-align:right">
#           <div style="color:rgba(255,255,255,.5);font-size:.75rem;letter-spacing:.08em;text-transform:uppercase">Invoice</div>
#           <div style="color:white;font-weight:700;font-size:1rem">#{invoice['number']}</div>
#         </div>
#       </div>

#       <div style="background:white;padding:28px 32px;border:1px solid #dde4f0;border-top:none">
#         <div style="display:flex;justify-content:space-between;margin-bottom:28px;flex-wrap:wrap;gap:16px">
#           <div>
#             <div style="font-size:.72rem;color:#5a718a;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px">Billed To</div>
#             <div style="font-weight:600;color:#0f1f35">{req['facility_name']}</div>
#             <div style="color:#5a718a;font-size:.88rem">{req['facility_address']}</div>
#             <div style="color:#5a718a;font-size:.88rem">{req['facility_email']}</div>
#           </div>
#           <div style="text-align:right">
#             <div style="font-size:.72rem;color:#5a718a;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px">Due Date</div>
#             <div style="font-weight:600;color:#0f1f35">{invoice['due_date']}</div>
#           </div>
#         </div>

#         <table style="width:100%;border-collapse:collapse;font-size:.9rem;margin-bottom:20px">
#           <thead>
#             <tr style="background:#f7f9fc">
#               <th style="padding:10px 14px;text-align:left;font-size:.72rem;color:#5a718a;
#                 letter-spacing:.08em;text-transform:uppercase;border-bottom:1px solid #dde4f0">Description</th>
#               <th style="padding:10px 14px;text-align:right;font-size:.72rem;color:#5a718a;
#                 letter-spacing:.08em;text-transform:uppercase;border-bottom:1px solid #dde4f0">Amount</th>
#             </tr>
#           </thead>
#           <tbody>
#             <tr>
#               <td style="padding:14px;color:#0f1f35;border-bottom:1px solid #dde4f0">{invoice['description']}</td>
#               <td style="padding:14px;text-align:right;font-weight:600;color:#0f1f35;
#                 border-bottom:1px solid #dde4f0">{invoice['currency']} {invoice['amount']}</td>
#             </tr>
#             {notes_row}
#           </tbody>
#           <tfoot>
#             <tr style="background:#f7f9fc">
#               <td style="padding:14px;font-weight:700;color:#0d3b6e">Total Due</td>
#               <td style="padding:14px;text-align:right;font-weight:700;font-size:1.1rem;color:#F47C20">
#                 {invoice['currency']} {invoice['amount']}
#               </td>
#             </tr>
#           </tfoot>
#         </table>

#         <div style="background:#fff5eb;border:1px solid rgba(244,124,32,.25);border-radius:10px;
#           padding:16px 20px;font-size:.88rem;color:#5a718a;line-height:1.6">
#           <strong style="color:#0f1f35">Payment Instructions:</strong><br/>
#           Please make payment via Mobile Money or bank transfer and send proof to
#           <a href="mailto:rxlabelapp@gmail.com" style="color:#F47C20">rxlabelapp@gmail.com</a>
#           referencing invoice <strong>#{invoice['number']}</strong>.<br/>
#           For queries call <strong>+233 555 276 832</strong>.
#         </div>
#       </div>
#       <div style="padding:16px 32px;font-size:.78rem;color:#5a718a;text-align:center">
#         &copy; 2026 RxLabel &mdash; rxlabelapp@gmail.com &mdash; +233 555 276 832
#       </div>
#     </div>
#     """
#     return send_email(req["facility_email"], subject, html)


def send_invoice(req: dict, invoice: dict):
    """
    Send a payment request / invoice to the facility.
    invoice dict: { number, amount, currency, due_date, description, notes }
    """
    subject = f"[RxLabel] Invoice #{invoice['number']} — {invoice['amount']} {invoice['currency']}"
    notes_row = (
        f"""
      <tr><td colspan="2" style="padding:10px 14px 14px">
        <div style="font-size:.82rem;color:#5a718a;font-style:italic;line-height:1.5">{invoice.get('notes','')}</div>
      </td></tr>"""
        if invoice.get("notes")
        else ""
    )

    html = f"""
    <div style="font-family:'Segoe UI',Helvetica,Arial,sans-serif;max-width:620px;margin:0 auto;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.10)">

      <!-- Header -->
      <div style="background:#0d3b6e;padding:28px 36px 24px">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
          <!-- Logo -->
          <div>
            <span style="font-size:1.5rem;font-weight:900;color:#F47C20;letter-spacing:-0.5px">Rx</span>
            <span style="font-size:1.5rem;font-weight:900;color:#ffffff;letter-spacing:-0.5px">Label</span>
            <div style="margin-top:4px;font-size:.72rem;color:rgba(255,255,255,.45);letter-spacing:.1em;text-transform:uppercase">Healthcare Labelling</div>
          </div>
          <!-- Invoice Badge -->
          <div style="text-align:right">
            <div style="display:inline-block;background:rgba(244,124,32,.15);border:1px solid rgba(244,124,32,.35);border-radius:8px;padding:10px 18px">
              <div style="font-size:.65rem;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:.12em;margin-bottom:4px">Invoice No.</div>
              <div style="color:#F47C20;font-weight:800;font-size:1.15rem;letter-spacing:.02em">#{invoice['number']}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Meta bar: Billed To + Due Date -->
      <div style="background:#f0f4fb;padding:20px 36px;border-bottom:1px solid #dde4f0;display:flex;justify-content:space-between;flex-wrap:wrap;gap:20px">
        <!-- Billed To -->
        <div>
          <div style="font-size:.65rem;color:#5a718a;text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px">Billed To</div>
          <div style="font-weight:700;color:#0f1f35;font-size:.95rem">{req['facility_name']}</div>
          <div style="color:#5a718a;font-size:.83rem;margin-top:2px">{req['facility_address']}</div>
          <div style="color:#5a718a;font-size:.83rem;margin-top:1px">{req['facility_email']}</div>
        </div>
        <!-- Due Date -->
        <div style="text-align:right">
          <div style="font-size:.65rem;color:#5a718a;text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px">Due Date</div>
          <div style="font-weight:700;color:#0f1f35;font-size:.95rem">{invoice['due_date']}</div>
          <div style="margin-top:6px;display:inline-block;background:#fff3e0;border:1px solid rgba(244,124,32,.3);border-radius:20px;padding:3px 10px;font-size:.72rem;color:#F47C20;font-weight:600">Payment Due</div>
        </div>
      </div>

      <!-- Body -->
      <div style="background:white;padding:28px 36px">

        <!-- Line Items Table -->
        <table style="width:100%;border-collapse:collapse;font-size:.9rem;margin-bottom:24px">
          <thead>
            <tr style="background:#f7f9fc">
              <th style="padding:11px 14px;text-align:left;font-size:.68rem;color:#5a718a;letter-spacing:.1em;text-transform:uppercase;border-bottom:2px solid #dde4f0;border-top:1px solid #dde4f0">Description</th>
              <th style="padding:11px 14px;text-align:right;font-size:.68rem;color:#5a718a;letter-spacing:.1em;text-transform:uppercase;border-bottom:2px solid #dde4f0;border-top:1px solid #dde4f0">Amount</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="padding:16px 14px;color:#0f1f35;border-bottom:1px solid #eef1f7;line-height:1.5">{invoice['description']}</td>
              <td style="padding:16px 14px;text-align:right;font-weight:600;color:#0f1f35;border-bottom:1px solid #eef1f7;white-space:nowrap">{invoice['currency']} {invoice['amount']}</td>
            </tr>
            {notes_row}
          </tbody>
          <tfoot>
            <tr style="background:#f7f9fc">
              <td style="padding:14px;font-weight:700;color:#0d3b6e;font-size:.9rem">Total Due</td>
              <td style="padding:14px;text-align:right;font-weight:800;font-size:1.2rem;color:#F47C20;white-space:nowrap">
                {invoice['currency']} {invoice['amount']}
              </td>
            </tr>
          </tfoot>
        </table>

        <!-- Payment Instructions -->
        <div style="background:#fff8f2;border-left:4px solid #F47C20;border-radius:0 10px 10px 0;padding:18px 22px;font-size:.87rem;color:#5a718a;line-height:1.7">
          <div style="font-weight:700;color:#0f1f35;margin-bottom:6px">Payment Instructions</div>
          Please make payment via Mobile Money or bank transfer and send proof to
          <a href="mailto:rxlabelapp@gmail.com" style="color:#F47C20;font-weight:600;text-decoration:none">rxlabelapp@gmail.com</a>
          referencing invoice <strong style="color:#0f1f35">#{invoice['number']}</strong>.<br/>
          For queries call <strong style="color:#0f1f35">+233 555 276 832</strong>.
        </div>
      </div>

      <!-- Footer -->
      <div style="background:#0d3b6e;padding:16px 36px;font-size:.75rem;color:rgba(255,255,255,.45);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px">
        <span>&copy; 2026 RxLabel</span>
        <span>rxlabelapp@gmail.com &nbsp;&middot;&nbsp; +233 555 276 832</span>
      </div>

    </div>
    """
    return send_email(req["facility_email"], subject, html)

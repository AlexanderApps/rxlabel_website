/* modal.js – license request modal + form submission */
(function () {
  const overlay  = document.getElementById('modalOverlay');
  const toast    = document.getElementById('toast');
  const submitBtn = document.getElementById('submitBtn');

  /* ── OPEN / CLOSE ─────────────────────────────────────── */
  window.openModal = function (licenseType) {
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';

    if (licenseType) {
      const sel = document.getElementById('license_type');
      for (const opt of sel.options) {
        if (opt.value === licenseType) { sel.value = licenseType; break; }
      }
    }
  };

  window.closeModal = function () {
    overlay.classList.remove('open');
    document.body.style.overflow = '';
    clearErrors();
  };

  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) window.closeModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') window.closeModal();
  });

  /* ── VALIDATION ───────────────────────────────────────── */
  const FIELDS = [
    'facility_name',
    'facility_contact',
    'facility_address',
    'facility_email',
    'license_type',
  ];

  function clearErrors() {
    FIELDS.forEach((f) => {
      const el = document.getElementById(f);
      if (el) el.classList.remove('error');
    });
  }

  function validate(data) {
    let valid = true;
    FIELDS.forEach((f) => {
      const el = document.getElementById(f);
      if (!data[f]) {
        el.classList.add('error');
        valid = false;
      } else {
        el.classList.remove('error');
      }
    });
    return valid;
  }

  /* ── SUBMIT ───────────────────────────────────────────── */
  window.submitForm = async function () {
    clearErrors();

    const data = {};
    FIELDS.forEach((f) => {
      const el = document.getElementById(f);
      data[f] = el ? el.value.trim() : '';
    });

    if (!validate(data)) {
      showToast('Please fill in all required fields.', true);
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting…';

    try {
      const res = await fetch('/request-license', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      const result = await res.json();

      if (result.success) {
        window.closeModal();
        FIELDS.forEach((f) => { const el = document.getElementById(f); if (el) el.value = ''; });
        showToast('✓ License request submitted! We will be in touch soon.');
      } else {
        showToast(result.message || 'Submission failed. Please try again.', true);
      }
    } catch (err) {
      showToast('Network error. Please try again.', true);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Submit Request';
    }
  };

  /* ── TOAST ────────────────────────────────────────────── */
  function showToast(msg, isError = false) {
    toast.innerHTML = msg;
    toast.className = 'toast' + (isError ? ' error' : '') + ' show';
    setTimeout(() => {
      toast.className = 'toast' + (isError ? ' error' : '');
    }, 4000);
  }
})();

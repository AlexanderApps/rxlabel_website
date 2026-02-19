/* admin.js – status updates, toast, shared admin utilities */
(function () {
  const toast = document.getElementById('adminToast');

  /* ── TOAST (global so inline scripts can call it) ─────── */
  window.showAdminToast = function (msg, isError = false) {
    toast.textContent = msg;
    toast.className = 'admin-toast' + (isError ? ' error' : '') + ' show';
    setTimeout(() => {
      toast.className = 'admin-toast' + (isError ? ' error' : '');
    }, 3500);
  };

  /* ── STATUS UPDATE ────────────────────────────────────── */
  window.updateStatus = async function (id, status, el) {
    const prev = el.dataset.prev || el.value;
    try {
      const res  = await fetch(`/admin/requests/${id}/status`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ status }),
      });
      const data = await res.json();
      if (data.success) {
        el.dataset.prev = status;
        window.showAdminToast(`Request #${id} marked as "${status}".`);
      } else {
        el.value = prev;
        window.showAdminToast('Update failed. Please try again.', true);
      }
    } catch (err) {
      el.value = prev;
      window.showAdminToast('Network error.', true);
    }
  };

  /* store initial values so we can revert on failure */
  document.querySelectorAll('.action-select').forEach((el) => {
    el.dataset.prev = el.value;
  });
})();

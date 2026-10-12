/**
 * CarePulse Hospital Portal - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Auto-dismiss flash alerts after 5 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 5500);
  });

  // 2. Initialize Bootstrap Tooltips & Popovers
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // 3. Client-side Search filter for Doctor cards (live filtering)
  const doctorSearchInput = document.getElementById('doctorLiveSearch');
  if (doctorSearchInput) {
    doctorSearchInput.addEventListener('input', function (e) {
      const query = e.target.value.toLowerCase().trim();
      const doctorCards = document.querySelectorAll('.doctor-item-col');

      doctorCards.forEach(function (col) {
        const text = col.textContent.toLowerCase();
        if (text.includes(query)) {
          col.style.display = '';
        } else {
          col.style.display = 'none';
        }
      });
    });
  }

  // 4. Action Confirmation Prompts
  const confirmActions = document.querySelectorAll('[data-confirm]');
  confirmActions.forEach(function (el) {
    el.addEventListener('click', function (e) {
      const message = el.getAttribute('data-confirm') || 'Are you sure you want to proceed?';
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });
});

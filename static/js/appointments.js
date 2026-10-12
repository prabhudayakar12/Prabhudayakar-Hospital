/**
 * Interactive Time Slot System for CarePulse Hospital Portal
 */

document.addEventListener('DOMContentLoaded', function () {
  const dateInput = document.getElementById('appointment_date');
  const slotHiddenInput = document.getElementById('id_time_slot');
  const slotsContainer = document.getElementById('slotsContainer');
  const slotsLoading = document.getElementById('slotsLoading');
  const slotsAlert = document.getElementById('slotsAlert');
  const appointmentForm = document.getElementById('appointmentBookingForm');
  const doctorDataEl = document.getElementById('doctorBookingData');

  if (!dateInput || !slotsContainer || !doctorDataEl) {
    return;
  }

  const doctorId = doctorDataEl.getAttribute('data-doctor-id');

  // Trigger availability check when date changes
  dateInput.addEventListener('change', function () {
    const selectedDate = dateInput.value;
    if (selectedDate) {
      fetchAvailableSlots(doctorId, selectedDate);
    }
  });

  // Fetch initial slots on page load
  if (dateInput.value) {
    fetchAvailableSlots(doctorId, dateInput.value);
  }

  function fetchAvailableSlots(docId, targetDate) {
    // Reset selected slot
    if (slotHiddenInput) {
      slotHiddenInput.value = '';
    }

    // Show loading
    slotsLoading.classList.remove('d-none');
    slotsAlert.classList.add('d-none');
    slotsContainer.innerHTML = '';

    fetch(`/api/available-slots/?doctor_id=${encodeURIComponent(docId)}&date=${encodeURIComponent(targetDate)}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to retrieve slot availability.');
        }
        return response.json();
      })
      .then(data => {
        slotsLoading.classList.add('d-none');

        // Check if date is in the past
        if (data.is_past_date) {
          showAlert('danger', 'You cannot select a past date for an appointment. Please select a valid upcoming date.');
          return;
        }

        // Check if doctor is available on this weekday
        if (!data.is_doctor_available_day) {
          showAlert(
            'warning',
            `<strong>Dr. ${data.doctor_name}</strong> does not have consultations scheduled on this day. Available days are: <strong>${data.available_days_str}</strong>.`
          );
          return;
        }

        renderSlots(data.slots);
      })
      .catch(error => {
        slotsLoading.classList.add('d-none');
        showAlert('danger', 'Unable to check slot availability. Please try again or check your network.');
        console.error(error);
      });
  }

  function showAlert(type, messageHtml) {
    slotsAlert.className = `alert alert-${type} d-flex align-items-center mb-3`;
    slotsAlert.innerHTML = `
      <i class="fas fa-circle-exclamation me-2 fs-5"></i>
      <div>${messageHtml}</div>
    `;
    slotsAlert.classList.remove('d-none');
  }

  function renderSlots(slots) {
    if (!slots || slots.length === 0) {
      showAlert('info', 'No appointment slots configured for this doctor.');
      return;
    }

    // Split slots into Morning & Afternoon
    const morningSlots = slots.filter(s => s.slot.includes('AM'));
    const afternoonSlots = slots.filter(s => s.slot.includes('PM'));

    let html = '';

    if (morningSlots.length > 0) {
      html += `
        <div class="slot-section-title">
          <i class="fas fa-sun text-warning"></i> Morning Consultation Slots
        </div>
        <div class="slots-grid">
      `;
      morningSlots.forEach(s => {
        html += buildSlotButtonHtml(s);
      });
      html += `</div>`;
    }

    if (afternoonSlots.length > 0) {
      html += `
        <div class="slot-section-title mt-3">
          <i class="fas fa-cloud-sun text-primary"></i> Afternoon & Evening Slots
        </div>
        <div class="slots-grid">
      `;
      afternoonSlots.forEach(s => {
        html += buildSlotButtonHtml(s);
      });
      html += `</div>`;
    }

    slotsContainer.innerHTML = html;

    // Attach click handlers to slots
    const slotButtons = slotsContainer.querySelectorAll('.slot-btn.available');
    slotButtons.forEach(btn => {
      btn.addEventListener('click', function () {
        // Deselect previous
        slotsContainer.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
        // Select current
        btn.classList.add('selected');
        const selectedSlot = btn.getAttribute('data-slot');
        slotHiddenInput.value = selectedSlot;

        // Feedback in selection info badge if present
        const selectedBadge = document.getElementById('selectedSlotDisplay');
        if (selectedBadge) {
          selectedBadge.textContent = `${dateInput.value} at ${selectedSlot}`;
          selectedBadge.classList.remove('d-none');
        }
      });
    });
  }

  function buildSlotButtonHtml(slotObj) {
    if (slotObj.is_booked) {
      return `
        <div class="slot-btn booked disabled" title="This slot is already booked.">
          <span class="slot-time">${slotObj.label}</span>
          <span class="slot-state"><i class="fas fa-lock me-1"></i>Booked</span>
        </div>
      `;
    } else if (slotObj.is_available) {
      return `
        <div class="slot-btn available" data-slot="${slotObj.slot}" role="button" tabindex="0">
          <span class="slot-time">${slotObj.label}</span>
          <span class="slot-state"><i class="fas fa-check me-1"></i>Available</span>
        </div>
      `;
    } else {
      return `
        <div class="slot-btn disabled">
          <span class="slot-time">${slotObj.label}</span>
          <span class="slot-state">Unavailable</span>
        </div>
      `;
    }
  }

  // Pre-submit validation
  if (appointmentForm) {
    appointmentForm.addEventListener('submit', function (e) {
      if (!slotHiddenInput.value) {
        e.preventDefault();
        showAlert('danger', 'Please choose an available appointment time slot from the grid before confirming your booking.');
        slotsContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
  }
});

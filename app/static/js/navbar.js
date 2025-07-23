// static/js/navbar.js

// Appointment modal opener
function openCreateAppointmentModal() {
  fetch('/appointment/add')
    .then(resp => resp.text())
    .then(html => setupModal(html))
    .catch(err => console.error('Error loading modal:', err));
}

function setupModal(data) {
  const modalWrapper = document.getElementById("createAppointmentModal");
  
  if (!modalWrapper) {
    console.error("Modal wrapper not found");
    return;
  }
  
  modalWrapper.innerHTML = data;
  
  // Now that the HTML is injected, we can find the modal
  const modal = document.getElementById("myModal");
  
  if (!modal) {
    console.error("Modal element not found after injection");
    return;
  }
  
  modal.classList.add("active");
  modal.style.display = "flex";

  // Close buttons
  const closeBtn = document.getElementById("closeModalBtn");
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      modal.classList.remove("active");
      modal.style.display = "none";
    });
  }

  window.addEventListener("click", event => {
    if (event.target === modal) {
      modal.classList.remove("active");
      modal.style.display = "none";
    }
  });

  // Form validation
  const form = document.getElementById("appointmentForm");
  if (form) {
    form.addEventListener("submit", event => {
      const dateField = document.getElementById("form-date");
      if (dateField) {
        const today = new Date().toISOString().split('T')[0];
        if (dateField.value < today) {
          event.preventDefault();
          dateField.setCustomValidity('Randevu tarihi geçmişte olamaz.');
          dateField.reportValidity();
        } else {
          dateField.setCustomValidity('');
        }
      }
    });
  }
}

// Navbar dropdowns + appointment button
document.addEventListener('DOMContentLoaded', function() {
  // Appointment button
  const openBtn = document.getElementById("openCreateAppointmentModal");
  if (openBtn) {
    openBtn.addEventListener("click", openCreateAppointmentModal);
  }

  // Hover dropdowns
  document.querySelectorAll('.relative.group').forEach(navbar => {
    let timer;
    navbar.addEventListener('mouseenter', () => {
      clearTimeout(timer);
      const menu = navbar.querySelector('.dropdown-menu');
      if (menu) {
        menu.style.visibility = 'visible';
        menu.style.opacity    = '1';
      }
    });
    navbar.addEventListener('mouseleave', () => {
      timer = setTimeout(() => {
        const menu = navbar.querySelector('.dropdown-menu');
        if (menu) {
          menu.style.visibility = 'hidden';
          menu.style.opacity    = '0';
        }
      }, 200);
    });
  });
});

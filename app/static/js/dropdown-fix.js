// Fix for dropdown menu links
document.addEventListener('DOMContentLoaded', function() {
  // Add click handlers to all dropdown links
  const dropdownLinks = document.querySelectorAll('.dropdown-menu a');
  dropdownLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      // Prevent the default behavior only if the href is "#"
      if (this.getAttribute('href') === '#') {
        e.preventDefault();
        return;
      }
      
      // Special handling for the Create Appointment link
      if (this.id === 'openCreateAppointmentModal') {
        e.preventDefault();
        // If the openCreateAppointmentModal function exists, call it
        if (typeof openCreateAppointmentModal === 'function') {
          openCreateAppointmentModal();
        } else {
          // Otherwise, redirect to the add appointment page
          window.location.href = this.getAttribute('href');
        }
        return;
      }
      
      // For all other links, make sure they work by explicitly navigating
      const href = this.getAttribute('href');
      if (href && href !== '#') {
        // Let the default behavior handle it (no need to override)
        // The browser will navigate to the href
      }
    });
  });
});
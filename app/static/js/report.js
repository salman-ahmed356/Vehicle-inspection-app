// static/js/report.js

$(document).ready(function() {
  console.log("report.js loaded, AJAX URL:", window.expertiseDetailUrl);

  $('.expertise-link').on('click', function(e) {
    e.preventDefault();

    const type   = $(this).data('expertise-type');
    const report = $(this).data('report-id');
    console.log("Loading details for:", type, "report:", report);

    $.get(window.expertiseDetailUrl, {
      expertise_type: type,
      report_id:      report
    })
    .done(function(html) {
      console.log("AJAX success, injecting HTML.");
      $('#expertiseDetailContainer').html(html);
    })
    .fail(function(xhr, status, error) {
      console.error("AJAX failed:", status, error);
      alert("Failed to load inspection details. See console for more info.");
    });
  });

  // Auto-click the first tab on load
  $('.expertise-link').first().trigger('click');
});

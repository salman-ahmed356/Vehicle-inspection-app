// Handle back button functionality
document.addEventListener('DOMContentLoaded', function() {
    const backButtons = document.querySelectorAll('a[href="javascript:history.back()"]');
    
    backButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Check if there's history to go back to
            if (window.history.length > 1) {
                window.history.back();
            } else {
                // If no history, go to dashboard
                window.location.href = '/';
            }
        });
    });
});
// Tab navigation logic
document.addEventListener('DOMContentLoaded', function() {
    // Don't reset active tab on page load - the server-side will handle this
    // based on the active_tab parameter
    
    // Add click handlers for tab navigation
    document.querySelectorAll('.border-b a').forEach(function (tabLink) {
        tabLink.addEventListener('click', function (e) {
            e.preventDefault();
            
            // Get the tab ID from the href attribute
            const tabId = this.getAttribute('href');
            
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(function (tabContent) {
                tabContent.classList.remove('active');
            });
            
            // Show the selected tab content
            document.querySelector(tabId).classList.add('active');
            
            // Update tab styling
            document.querySelectorAll('.border-b a').forEach(function (link) {
                link.classList.remove('border-l', 'border-t', 'border-r', 'rounded-t', 'text-blue-700');
                link.classList.add('text-blue-500', 'hover:text-blue-700');
            });
            
            this.classList.add('border-l', 'border-t', 'border-r', 'rounded-t', 'text-blue-700');
            this.classList.remove('text-blue-500', 'hover:text-blue-700');
            
            // Update URL with the active tab (optional)
            const tabName = tabId.replace('#tab', '');
            const activeTabParam = tabName === '1' ? 'company' : 
                                 tabName === '2' ? 'staff' : 
                                 tabName === '3' ? 'invoice' : 'report';
            
            // Update URL without reloading the page
            const url = new URL(window.location.href);
            url.searchParams.set('active_tab', activeTabParam);
            window.history.replaceState({}, '', url);
        });
    });
});

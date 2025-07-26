// Global file input protection
// This script prevents InvalidStateError when trying to set file input values

(function() {
    'use strict';
    
    // Override any attempts to set file input values
    function protectFileInputs() {
        // Find all file inputs
        const fileInputs = document.querySelectorAll('input[type="file"]');
        
        fileInputs.forEach(input => {
            // Create a property descriptor that prevents setting value
            Object.defineProperty(input, 'value', {
                get: function() {
                    return this.files && this.files.length > 0 ? this.files[0].name : '';
                },
                set: function(val) {
                    // Only allow empty string
                    if (val === '' || val === null || val === undefined) {
                        // Clear the input by replacing it
                        const newInput = this.cloneNode(true);
                        newInput.value = '';
                        this.parentNode.replaceChild(newInput, this);
                        return;
                    }
                    // Ignore any other attempts to set value
                    console.warn('Cannot set file input value to:', val);
                },
                configurable: true
            });
        });
    }
    
    // Protect existing file inputs
    document.addEventListener('DOMContentLoaded', protectFileInputs);
    
    // Protect dynamically added file inputs
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        const fileInputs = node.querySelectorAll ? node.querySelectorAll('input[type="file"]') : [];
                        if (node.matches && node.matches('input[type="file"]')) {
                            protectFileInputs();
                        } else if (fileInputs.length > 0) {
                            protectFileInputs();
                        }
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
})();
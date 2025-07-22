document.addEventListener('DOMContentLoaded', function() {
  // Save form data to localStorage when form is submitted
  const form = document.querySelector('form');
  
  // Save form data before submission
  form.addEventListener('submit', function() {
    const formData = {};
    const formElements = form.elements;
    
    for (let i = 0; i < formElements.length; i++) {
      const element = formElements[i];
      if (element.name && element.type !== 'submit' && element.type !== 'hidden') {
        if (element.type === 'checkbox') {
          formData[element.name] = element.checked;
        } else {
          formData[element.name] = element.value;
        }
      }
    }
    
    localStorage.setItem('reportFormData', JSON.stringify(formData));
  });
  
  // Load form data from localStorage if it exists
  const savedData = localStorage.getItem('reportFormData');
  if (savedData) {
    const formData = JSON.parse(savedData);
    const formElements = form.elements;
    
    for (let i = 0; i < formElements.length; i++) {
      const element = formElements[i];
      if (element.name && formData[element.name] !== undefined) {
        if (element.type === 'checkbox') {
          element.checked = formData[element.name];
        } else {
          element.value = formData[element.name];
        }
      }
    }
    
    // Clear localStorage if form was successfully submitted (check for success message)
    const successMessage = document.querySelector('.bg-green-100');
    if (successMessage) {
      localStorage.removeItem('reportFormData');
    }
  }
});
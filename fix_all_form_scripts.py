import os
import re

def fix_form_script(file_path):
    """Fix the form submission script in an expertise template."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the file has a form
    if '<form id="expertiseForm"' not in content:
        print(f"No form found in {os.path.basename(file_path)}")
        return False
    
    # Check if the file has a script
    if '<script>' not in content:
        print(f"No script found in {os.path.basename(file_path)}")
        return False
    
    # Replace the script with a fixed version
    script_pattern = r'<script>.*?</script>'
    new_script = """<script>
document.addEventListener('DOMContentLoaded', function() {
  var form = document.getElementById('expertiseForm');
  
  // Log all form elements on page load
  console.log('Form elements on page load:');
  Array.from(form.elements).forEach(function(element) {
    if (element.name) {
      console.log(element.name + ' = ' + element.value + 
                 (element.type === 'radio' ? ', checked: ' + element.checked : ''));
    }
  });
  
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    var formData = new FormData(form);
    
    // Log what we're submitting
    console.log('Submitting form data:');
    for (var pair of formData.entries()) {
      console.log(pair[0] + ': ' + pair[1]);
    }
    
    fetch(form.action, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams(formData)
    })
    .then(function(response) {
      console.log('Response status:', response.status);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(function(data) {
      console.log('Response data:', data);
      if (data.success) {
        alert('Expertise updated successfully!');
      } else {
        alert('Update failed: ' + (data.error || 'Unknown error'));
      }
    })
    .catch(function(error) {
      console.error('Error:', error);
      alert('Update failed. Please check your inputs!');
    });
  });
  
  // Add change listeners to form elements
  Array.from(form.elements).forEach(function(element) {
    if (element.name && element.type !== 'hidden' && element.type !== 'submit') {
      element.addEventListener('change', function() {
        console.log(this.name + ' changed to ' + this.value);
      });
    }
  });
});
</script>"""
    
    # Replace the script
    content = re.sub(script_pattern, new_script, content, flags=re.DOTALL)
    
    # Make sure the form has the correct attributes
    form_pattern = r'<form id="expertiseForm"[^>]*>'
    form_match = re.search(form_pattern, content)
    if form_match:
        form_tag = form_match.group(0)
        if 'onsubmit="return false;"' not in form_tag:
            new_form_tag = form_tag.replace('<form id="expertiseForm"', '<form id="expertiseForm" onsubmit="return false;"')
            content = content.replace(form_tag, new_form_tag)
        
        if 'action="' not in form_tag:
            new_form_tag = form_tag.replace('>', ' action="{{ url_for(\'reports.expertise_detail\', expertise_report_id=expertise_report.id) }}">')
            content = content.replace(form_tag, new_form_tag)
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed form script in {os.path.basename(file_path)}")
    return True

def fix_all_form_scripts():
    """Fix form submission scripts in all expertise templates."""
    expertise_dir = r"c:\Users\Killua\Desktop\Vehicle-Inspection-Web-App-main\app\templates\report_sections\expertises"
    
    if not os.path.exists(expertise_dir):
        print(f"Directory not found: {expertise_dir}")
        return
    
    fixed_count = 0
    for filename in os.listdir(expertise_dir):
        if filename.endswith("_expertise.html"):
            file_path = os.path.join(expertise_dir, filename)
            if fix_form_script(file_path):
                fixed_count += 1
    
    print(f"Fixed form scripts in {fixed_count} templates")

if __name__ == "__main__":
    fix_all_form_scripts()
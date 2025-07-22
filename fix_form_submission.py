import os
import re

def fix_form_submission(file_path):
    """Fix the form submission script in expertise templates."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the form submission script with a simpler, more reliable version
    form_script_pattern = r'document\.addEventListener\([\'"]DOMContentLoaded[\'"],\s*function\(\)\s*\{.*?document\.getElementById\([\'"]expertiseForm[\'"]\)\.addEventListener\([\'"]submit[\'"],.*?\}\);'
    
    if re.search(form_script_pattern, content, re.DOTALL):
        print(f"Replacing form submission script in {os.path.basename(file_path)}")
        
        new_script = """document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('expertiseForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Get form data
    var formData = new FormData(this);
    
    // Log form data
    console.log('Submitting form data:');
    for (var pair of formData.entries()) {
      console.log(pair[0] + ': ' + pair[1]);
    }
    
    // Submit form via fetch
    fetch(this.action, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams(formData)
    })
    .then(function(response) {
      return response.json();
    })
    .then(function(data) {
      if (data.success) {
        alert('Expertise updated successfully!');
      } else {
        alert('Update failed: ' + (data.error || 'Unknown error'));
      }
    })
    .catch(function(error) {
      console.error('Error:', error);
      alert('Update failed. Please try again.');
    });
  });
});"""
        
        content = re.sub(form_script_pattern, new_script, content, flags=re.DOTALL)
        
        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    return False

def fix_all_form_submissions():
    """Fix form submission scripts in all expertise templates."""
    expertise_dir = r"c:\Users\Killua\Desktop\Vehicle-Inspection-Web-App-main\app\templates\report_sections\expertises"
    
    if not os.path.exists(expertise_dir):
        print(f"Directory not found: {expertise_dir}")
        return
    
    fixed_count = 0
    for filename in os.listdir(expertise_dir):
        if filename.endswith("_expertise.html"):
            file_path = os.path.join(expertise_dir, filename)
            if fix_form_submission(file_path):
                fixed_count += 1
    
    print(f"Fixed form submission scripts in {fixed_count} templates")

if __name__ == "__main__":
    fix_all_form_submissions()
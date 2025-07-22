import os
import re

def fix_form(file_path):
    """Fix the form in an expertise template."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the entire form with a fixed version
    form_pattern = r'<form id="expertiseForm".*?</form>'
    script_pattern = r'<script>.*?</script>'
    
    # Extract the form content
    form_match = re.search(form_pattern, content, re.DOTALL)
    if not form_match:
        print(f"No form found in {os.path.basename(file_path)}")
        return False
    
    form_content = form_match.group(0)
    
    # Add onsubmit="return false;" to prevent direct form submission
    if 'onsubmit="return false;"' not in form_content:
        form_content = form_content.replace('<form id="expertiseForm"', '<form id="expertiseForm" onsubmit="return false;"')
    
    # Replace the form in the content
    content = re.sub(form_pattern, form_content, content, flags=re.DOTALL)
    
    # Replace the script with a fixed version
    new_script = """<script>
document.addEventListener('DOMContentLoaded', function() {
  var form = document.getElementById('expertiseForm');
  
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    var formData = new FormData(form);
    var url = "{{ url_for('reports.expertise_detail', expertise_report_id=expertise_report.id) }}";
    
    fetch(url, {
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
});
</script>"""
    
    # Replace the last script tag in the file
    script_matches = list(re.finditer(script_pattern, content, re.DOTALL))
    if script_matches:
        last_script = script_matches[-1]
        content = content[:last_script.start()] + new_script + content[last_script.end():]
        print(f"Updated script in {os.path.basename(file_path)}")
    else:
        # Add the script if none exists
        content += new_script
        print(f"Added script to {os.path.basename(file_path)}")
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def fix_all_forms():
    """Fix all expertise forms in the project."""
    expertise_dir = r"c:\Users\Killua\Desktop\Vehicle-Inspection-Web-App-main\app\templates\report_sections\expertises"
    
    if not os.path.exists(expertise_dir):
        print(f"Directory not found: {expertise_dir}")
        return
    
    fixed_count = 0
    for filename in os.listdir(expertise_dir):
        if filename.endswith("_expertise.html"):
            file_path = os.path.join(expertise_dir, filename)
            if fix_form(file_path):
                fixed_count += 1
    
    print(f"Fixed {fixed_count} expertise forms")

if __name__ == "__main__":
    fix_all_forms()
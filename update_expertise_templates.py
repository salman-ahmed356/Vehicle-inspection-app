import os
import re

def update_expertise_template(file_path):
    """Update an expertise template to not reload the page after form submission."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the file contains jQuery
    jquery_pattern = r'\$\(function\(\)\s*\{|\$\(document\)\.ready\(function\(\)\s*\{|\$\(\'#expertiseForm\'\)\.on\(\'submit\''
    if re.search(jquery_pattern, content):
        print(f"Replacing jQuery in {os.path.basename(file_path)}")
        # Replace jQuery form submission with vanilla JS
        content = re.sub(
            r'\$\(function\(\)\s*\{\s*\$\(\'#expertiseForm\'\)\.on\(\'submit\',\s*function\(e\)\s*\{[^}]*\}\);\s*\}\);',
            """document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('expertiseForm').addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Create FormData object
      const formData = new FormData(this);
      
      // Submit the form via fetch
      fetch(this.action, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(formData)
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          alert("Expertise updated successfully!");
          // Don't reload the page
        } else {
          alert("Update failed. Please check your inputs!");
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert("Update failed. Please check your inputs!");
      });
    });
  });""",
            content
        )
    
    # Check for window.location.reload()
    if "window.location.reload()" in content:
        print(f"Removing page reload in {os.path.basename(file_path)}")
        content = content.replace("window.location.reload()", "// Don't reload the page")
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def update_all_expertise_templates():
    """Update all expertise templates in the project."""
    expertise_dir = r"c:\Users\Killua\Desktop\Vehicle-Inspection-Web-App-main\app\templates\report_sections\expertises"
    
    if not os.path.exists(expertise_dir):
        print(f"Directory not found: {expertise_dir}")
        return
    
    updated_count = 0
    for filename in os.listdir(expertise_dir):
        if filename.endswith("_expertise.html"):
            file_path = os.path.join(expertise_dir, filename)
            if update_expertise_template(file_path):
                updated_count += 1
    
    print(f"Updated {updated_count} expertise templates")

if __name__ == "__main__":
    update_all_expertise_templates()
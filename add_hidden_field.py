import os
import re

def add_hidden_field(file_path):
    """Add hidden field for current_expertise_type to expertise template."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the file already has the hidden field
    if 'name="current_expertise_type"' in content:
        print(f"File already has hidden field: {os.path.basename(file_path)}")
        return False
    
    # Find the form tag
    form_pattern = r'<form[^>]*>'
    form_match = re.search(form_pattern, content)
    
    if not form_match:
        print(f"No form tag found in {os.path.basename(file_path)}")
        return False
    
    # Find the position after the form tag and the first input tag
    form_end = form_match.end()
    
    # Create the hidden field HTML
    hidden_field = '\n  <input type="hidden" name="current_expertise_type" value="{{ current_expertise_type }}">'
    
    # Insert the hidden field after the form tag
    updated_content = content[:form_end] + hidden_field + content[form_end:]
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Added hidden field to {os.path.basename(file_path)}")
    return True

def process_all_templates():
    """Process all expertise templates."""
    expertise_dir = r"c:\Users\Killua\Desktop\Vehicle-Inspection-Web-App-main\app\templates\report_sections\expertises"
    
    if not os.path.exists(expertise_dir):
        print(f"Directory not found: {expertise_dir}")
        return
    
    added_count = 0
    for filename in os.listdir(expertise_dir):
        if filename.endswith("_expertise.html"):
            file_path = os.path.join(expertise_dir, filename)
            if add_hidden_field(file_path):
                added_count += 1
    
    print(f"Added hidden field to {added_count} templates")

if __name__ == "__main__":
    process_all_templates()
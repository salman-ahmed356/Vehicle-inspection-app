import os
import re

def fix_expertise_form(file_path):
    """Add the correct action URL to the form."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add action URL to the form
    if '<form id="expertiseForm" method="POST">' in content:
        print(f"Adding action URL to form in {os.path.basename(file_path)}")
        content = content.replace(
            '<form id="expertiseForm" method="POST">',
            '<form id="expertiseForm" method="POST" action="{{ url_for(\'reports.expertise_detail\', expertise_report_id=expertise_report.id) }}">'
        )
    
    # Update the fetch URL to use the form's action
    if 'fetch("{{ url_for(' in content:
        print(f"Updating fetch URL in {os.path.basename(file_path)}")
        content = content.replace(
            'fetch("{{ url_for(\'reports.expertise_detail\', expertise_report_id=expertise_report.id) }}"',
            'fetch(this.action'
        )
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def fix_all_expertise_forms():
    """Fix all expertise forms in the project."""
    expertise_dir = r"c:\Users\Killua\Desktop\Vehicle-Inspection-Web-App-main\app\templates\report_sections\expertises"
    
    if not os.path.exists(expertise_dir):
        print(f"Directory not found: {expertise_dir}")
        return
    
    fixed_count = 0
    for filename in os.listdir(expertise_dir):
        if filename.endswith("_expertise.html"):
            file_path = os.path.join(expertise_dir, filename)
            if fix_expertise_form(file_path):
                fixed_count += 1
    
    print(f"Fixed {fixed_count} expertise forms")

if __name__ == "__main__":
    fix_all_expertise_forms()
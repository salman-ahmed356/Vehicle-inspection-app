import os
import re

def add_comment_box(file_path):
    """Add technician comment box to expertise template if it doesn't have one."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the file already has a technician comment box
    if 'technician_comment' in content:
        print(f"File already has comment box: {os.path.basename(file_path)}")
        
        # Fix onsubmit attribute if present
        if 'onsubmit="return false;"' in content:
            content = content.replace('onsubmit="return false;"', '')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  Fixed onsubmit attribute in {os.path.basename(file_path)}")
        
        return False
    
    # Find the submit button div
    submit_div_pattern = r'<div class="[^"]*justify-end[^"]*">\s*<button[^>]*>\s*[^<]*\s*</button>\s*</div>'
    submit_div_match = re.search(submit_div_pattern, content, re.DOTALL)
    
    if not submit_div_match:
        print(f"No submit button found in {os.path.basename(file_path)}")
        return False
    
    # Create the comment box HTML
    comment_box = """  <div class="mb-4">
    <label for="technician_comment" class="block text-gray-700 font-semibold mb-2">
      {{ _('Technician Comment') }}
    </label>
    <textarea
      id="technician_comment"
      name="technician_comment"
      rows="4"
      class="w-full p-2 border border-gray-300 rounded"
      placeholder="{{ _('Enter technician comment here...') }}"
    >{{ expertise_report.comment }}</textarea>
  </div>

"""
    
    # Insert the comment box before the submit button
    submit_div_start = submit_div_match.start()
    updated_content = content[:submit_div_start] + comment_box + content[submit_div_start:]
    
    # Fix onsubmit attribute if present
    if 'onsubmit="return false;"' in updated_content:
        updated_content = updated_content.replace('onsubmit="return false;"', '')
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Added comment box to {os.path.basename(file_path)}")
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
            if add_comment_box(file_path):
                added_count += 1
    
    print(f"Added comment box to {added_count} templates")

if __name__ == "__main__":
    process_all_templates()
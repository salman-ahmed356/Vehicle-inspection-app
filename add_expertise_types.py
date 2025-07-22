import sqlite3
import os
import glob

# Define the expertise types
expertise_types = [
    "Paint Expertise",
    "Body Expertise",
    "Engine Expertise",
    "Lateral Drift Expertise",
    "Suspension Expertise",
    "Brake Expertise",
    "Road Expertise",
    "Dyno Expertise",
    "ECU Expertise",
    "Interior Expertise",
    "Exterior Expertise",
    "Mechanical Expertise",
    "Interior & Exterior Expertise",
    "Road & Dyno Expertise",
    "Paint & Body Expertise"
]

# Parent-child relationships
parent_child = {
    "Interior & Exterior Expertise": ["Interior Expertise", "Exterior Expertise"],
    "Road & Dyno Expertise": ["Road Expertise", "Dyno Expertise"],
    "Paint & Body Expertise": ["Paint Expertise", "Body Expertise"]
}

def add_expertise_types():
    # Find all database files in the instance folder
    instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
    db_files = glob.glob(os.path.join(instance_dir, '*.db'))
    
    if not db_files:
        print(f"No database files found in {instance_dir}")
        return
    
    print(f"Found database files: {[os.path.basename(f) for f in db_files]}")
    
    # Try each database file
    for db_path in db_files:
        print(f"\nTrying database: {os.path.basename(db_path)}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Tables in {os.path.basename(db_path)}: {tables}")
        
        # Find expertise table
        expertise_table = None
        for table in tables:
            if 'expert' in table.lower() and 'type' in table.lower():
                expertise_table = table
                break
        
        if not expertise_table:
            print(f"No expertise type table found in {os.path.basename(db_path)}")
            conn.close()
            continue
        
        print(f"Found expertise table: {expertise_table}")
        
        # Check if there are already expertise types
        cursor.execute(f"SELECT COUNT(*) FROM {expertise_table}")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"Found {count} existing expertise types")
            
            # Print existing types
            cursor.execute(f"SELECT id, name FROM {expertise_table}")
            for row in cursor.fetchall():
                print(f"- ID: {row[0]}, Name: {row[1]}")
            
            conn.close()
            continue
        
        # Add expertise types
        print(f"Adding expertise types to {expertise_table}...")
        for expertise in expertise_types:
            cursor.execute(f"INSERT INTO {expertise_table} (name) VALUES (?)", (expertise,))
            print(f"Added: {expertise}")
        
        # Set parent-child relationships
        for parent, children in parent_child.items():
            # Get parent ID
            cursor.execute(f"SELECT id FROM {expertise_table} WHERE name = ?", (parent,))
            parent_id = cursor.fetchone()[0]
            
            # Update children
            for child in children:
                cursor.execute(f"UPDATE {expertise_table} SET parent_id = ? WHERE name = ?", (parent_id, child))
                print(f"Set {parent} as parent of {child}")
        
        # Commit changes
        conn.commit()
        conn.close()
        print(f"Expertise types added successfully to {os.path.basename(db_path)}!")
        return True
    
    print("Could not add expertise types to any database.")
    return False

if __name__ == "__main__":
    add_expertise_types()
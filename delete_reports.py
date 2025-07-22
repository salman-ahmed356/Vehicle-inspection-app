import sqlite3

def delete_all_reports():
    """Delete all reports and related data from the database."""
    # Connect to the database
    conn = sqlite3.connect('instance/data.db')
    cursor = conn.cursor()
    
    try:
        # Get count of reports before deletion
        cursor.execute("SELECT COUNT(*) FROM report")
        report_count = cursor.fetchone()[0]
        
        # Delete all expertise features
        cursor.execute("DELETE FROM expertise_features")
        
        # Delete all expertise reports
        cursor.execute("DELETE FROM expertise_reports")
        
        # Delete all reports
        cursor.execute("DELETE FROM report")
        
        # Commit the changes
        conn.commit()
        
        print(f"Successfully deleted {report_count} reports and all associated data.")
    except Exception as e:
        conn.rollback()
        print(f"Error deleting reports: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    delete_all_reports()
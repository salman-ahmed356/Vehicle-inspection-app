"""
Service for calculating overall vehicle rating based on inspection results.
"""

def calculate_overall_rating(package_expertise_reports):
    """
    Calculate overall rating based on inspection results.
    Only includes expertises where something was actually marked.
    Treats 'None'/'No Issue' as good (meaning it's fine).
    Returns a tuple of (score, rating_text, color_class)
    """
    
    if not package_expertise_reports:
        return 0, "No Inspection", "red"
    
    total_features = 0
    good_features = 0
    
    # Define status categories
    good_statuses = {
        'None', 'No Issue', 'No Error Logged', 'No ISSUE',  # These mean it's fine
        'Original', 'Good', 'Excellent', 'Very Good', 'Pass', 'Passed', 
        'OK', 'Working', 'Functional', 'Clean', 'New', 'Safe', 
        'Normal', 'Acceptable', 'Present', '(Good) Passed Inspection'
    }
    
    moderate_statuses = {
        # Paint statuses (0.5 points each)
        'Plastic', 'Painted', 'Locally Painted', 'Replaced', 'Coated', 'Repaired/Painted',
        # Mechanical statuses (0.5 points each)
        'Scratch',  # Changed from BAD to MODERATE
        # ECU statuses (0.5 points)
        'Error Logged',  # Moved from BAD to MODERATE
        # General moderate statuses
        'Fair', 'Average', 'Used', 'Moderate', 'Minor', 'Light', 
        'Partial', 'Standard', 'Maintained', 'Serviced', 'Repaired',
        '(Moderate) May Cause Issues'
    }
    
    # BAD statuses (0 points) - only severe damage
    bad_statuses = {
        'Dent/Crack/Deformation',  # Only this stays as BAD
        'Connection Failed',  # ECU specific bad status
        '(Bad) Maintenance Required', 'Damaged', 'Broken', 'Cracked',
        'Missing', 'Failed', 'Critical', 'Unsafe', 'Poor', 'Very Bad'
    }
    
    # Exclude specific expertises from rating calculation
    excluded_expertises = {'Road Test', 'Brake Test', 'Suspension Test', 'Road Expertise', 'Brake Expertise', 'Suspension Expertise'}
    
    # Process only expertises that have been marked
    for expertise in package_expertise_reports:
        expertise_name = expertise.get('expertise_type_name', 'Unknown')
        
        # Skip excluded expertises
        if expertise_name in excluded_expertises:
            continue
            
        features = expertise.get('features', [])

        
        # Check if this expertise has any marked features
        has_marked_features = False
        expertise_features = []
        
        for feature in features:
            # Handle both dict and object types
            if isinstance(feature, dict):
                status = str(feature.get('status', '')).strip()
                name = feature.get('name', 'Unknown')
            else:
                status = str(getattr(feature, 'status', '')).strip()
                name = getattr(feature, 'name', 'Unknown')
            
            # Treat empty/null statuses as "No Issue" (good)
            if not status or status in ['', '0', 0, 'null']:
                status = 'No Issue'
                
            expertise_features.append(status)
            has_marked_features = True
        
        # Only include this expertise if it has marked features
        if has_marked_features:
            for status in expertise_features:
                total_features += 1
                
                # Score the feature
                if status in good_statuses or any(good_status in status for good_status in good_statuses):
                    good_features += 1
                elif status in moderate_statuses or any(moderate_status in status for moderate_status in moderate_statuses):
                    good_features += 0.5
                else:
                    good_features += 0
    
    if total_features == 0:
        return 0, "No Data", "red"
    
    # Calculate percentage
    score = (good_features / total_features) * 100
    
    # Determine rating text and color
    if score >= 80:
        return score, "Excellent Condition", "green"
    elif score >= 60:
        return score, "Good Condition", "green"
    elif score >= 40:
        return score, "Fair Condition", "orange"
    elif score >= 20:
        return score, "Poor Condition", "red"
    else:
        return score, "Bad Condition", "red"
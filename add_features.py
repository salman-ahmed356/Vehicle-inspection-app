import os
import json
from app import create_app
from app.database import db
from app.models import ExpertiseReport, ExpertiseFeature, Report

# Paint expertise features
PAINT_FEATURES = [
    "Left Front Fender",
    "Left Front Door",
    "Left Rear Fender",
    "Front Bumper",
    "Hood",
    "Roof",
    "Trunk Lid",
    "Rear Bumper",
    "Right Front Fender",
    "Right Front Door",
    "Right Rear Door",
    "Right Rear Fender",
    "Left Rear Door"
]

# Body expertise features
BODY_FEATURES = [
    "Left Front Chassis",
    "Left Inner Rocker Panel",
    "Left A-Pillar Inner",
    "Left Upper Pillar",
    "Left Side Skirt",
    "Left Rear Chassis",
    "Front Bumper",
    "Front Panel",
    "Front Windshield",
    "Roof",
    "Rear Windshield",
    "Rear Panel",
    "Rear Wheel Well",
    "Rear Bumper",
    "Right Front Chassis",
    "Right Inner Rocker Panel",
    "Right A-Pillar Inner",
    "Right Upper Pillar",
    "Right Side Skirt",
    "Right Rear Chassis"
]

def load_expertise_map():
    """Load the expertise map from the JSON file."""
    try:
        map_path = os.path.join(os.path.dirname(__file__), 'data', 'expertise_map.json')
        if os.path.exists(map_path):
            with open(map_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"Expertise map not found at {map_path}")
            return {}
    except Exception as e:
        print(f"Error loading expertise map: {e}")
        return {}

def add_features_to_report(report_id):
    """Add features to an expertise report."""
    app = create_app()
    with app.app_context():
        # Get all expertise reports for this report
        expertise_reports = ExpertiseReport.query.filter_by(report_id=report_id).all()
        
        if not expertise_reports:
            print(f"No expertise reports found for report ID {report_id}")
            return
        
        # Load expertise map
        expertise_map = load_expertise_map()
        
        for er in expertise_reports:
            print(f"Processing expertise report ID {er.id} for type {er.expertise_type.name}")
            
            # Check if features already exist
            existing_features = ExpertiseFeature.query.filter_by(expertise_report_id=er.id).count()
            if existing_features > 0:
                print(f"  Already has {existing_features} features, skipping")
                continue
            
            # Add features based on expertise type
            features_to_add = []
            default_status = "Original"
            
            # Try to get features from expertise map
            if er.expertise_type.name in expertise_map:
                parts = expertise_map[er.expertise_type.name]
                features_to_add = [part["part_name"] for part in parts]
                if parts and "default_status" in parts[0]:
                    default_status = parts[0]["default_status"]
            else:
                # Fallback to hardcoded lists
                if "Paint" in er.expertise_type.name:
                    features_to_add = PAINT_FEATURES
                    default_status = "Original"
                elif "Body" in er.expertise_type.name:
                    features_to_add = BODY_FEATURES
                    default_status = "No Issue"
                else:
                    # Add some default features
                    features_to_add = ["Part 1", "Part 2", "Part 3"]
                    default_status = "No Issue"
            
            # Add the features
            for feature_name in features_to_add:
                feature = ExpertiseFeature(
                    name=feature_name,
                    status=default_status,
                    expertise_report_id=er.id
                )
                db.session.add(feature)
                print(f"  Added feature: {feature_name}")
            
            db.session.commit()
            print(f"  Added {len(features_to_add)} features to expertise report {er.id}")

def add_features_to_all_reports():
    """Add features to all reports in the database."""
    app = create_app()
    with app.app_context():
        reports = Report.query.all()
        print(f"Found {len(reports)} reports")
        
        for report in reports:
            print(f"Processing report ID {report.id}")
            add_features_to_report(report.id)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            add_features_to_all_reports()
        else:
            report_id = int(sys.argv[1])
            add_features_to_report(report_id)
    else:
        print("Usage: python add_features.py <report_id|all>")
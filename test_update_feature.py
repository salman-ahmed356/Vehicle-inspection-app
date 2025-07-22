from app import create_app
from app.database import db
from app.models import ExpertiseReport, ExpertiseFeature

def update_feature(report_id, feature_name, new_status):
    """Update a feature's status directly in the database."""
    app = create_app()
    with app.app_context():
        # Find the expertise report
        report = ExpertiseReport.query.get(report_id)
        if not report:
            print(f"Report {report_id} not found")
            return False
        
        # Find the feature
        feature = ExpertiseFeature.query.filter_by(
            expertise_report_id=report_id,
            name=feature_name
        ).first()
        
        if not feature:
            print(f"Feature '{feature_name}' not found in report {report_id}")
            return False
        
        # Update the feature
        old_status = feature.status
        feature.status = new_status
        db.session.commit()
        
        print(f"Updated feature '{feature_name}' in report {report_id}")
        print(f"  Old status: {old_status}")
        print(f"  New status: {new_status}")
        
        return True

def list_features(report_id):
    """List all features in an expertise report."""
    app = create_app()
    with app.app_context():
        # Find the expertise report
        report = ExpertiseReport.query.get(report_id)
        if not report:
            print(f"Report {report_id} not found")
            return
        
        print(f"Features in report {report_id} ({report.expertise_type.name}):")
        for feature in report.features:
            print(f"  {feature.name}: {feature.status}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_update_feature.py <report_id> [<feature_name> <new_status>]")
        sys.exit(1)
    
    report_id = int(sys.argv[1])
    
    if len(sys.argv) == 2:
        # Just list features
        list_features(report_id)
    else:
        # Update a feature
        feature_name = sys.argv[2]
        new_status = sys.argv[3]
        update_feature(report_id, feature_name, new_status)
from app import create_app
from app.database import db
from app.models import ExpertiseType
from app.enums import ExpertiseTypeEnum

def add_expertise_types():
    """Add expertise types using Flask app context."""
    app = create_app()
    with app.app_context():
        # Check if expertise types already exist
        existing_count = ExpertiseType.query.count()
        if existing_count > 0:
            print(f"Found {existing_count} existing expertise types.")
            
            # Print existing types
            types = ExpertiseType.query.all()
            for t in types:
                print(f"- {t.name}")
            
            return
        
        # Add expertise types from enum
        print("Adding expertise types...")
        for expertise_enum in ExpertiseTypeEnum:
            expertise_type = ExpertiseType(name=expertise_enum.value)
            db.session.add(expertise_type)
            print(f"Added: {expertise_enum.value}")
        
        # Add combined expertise types
        combined_types = {
            "Interior & Exterior Expertise": [
                ExpertiseTypeEnum.IC.value,
                ExpertiseTypeEnum.DIS.value
            ],
            "Road & Dyno Expertise": [
                ExpertiseTypeEnum.YOL.value,
                ExpertiseTypeEnum.DYNO.value
            ],
            "Paint & Body Expertise": [
                ExpertiseTypeEnum.BOYA.value,
                ExpertiseTypeEnum.KAPORTA.value
            ],
        }
        
        # First commit the individual expertise types
        db.session.commit()
        
        for parent_name, children in combined_types.items():
            # Create parent
            parent = ExpertiseType(name=parent_name)
            db.session.add(parent)
            db.session.commit()
            print(f"Added parent: {parent_name}")
            
            # Update children to reference parent
            for child_name in children:
                child = ExpertiseType.query.filter_by(name=child_name).first()
                if child:
                    child.parent_id = parent.id
                    print(f"Set {parent_name} as parent of {child_name}")
        
        db.session.commit()
        print("Expertise types added successfully!")

if __name__ == "__main__":
    add_expertise_types()
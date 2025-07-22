from app import create_app
from app.database import db
from app.models import ExpertiseType
from app.enums import ExpertiseTypeEnum
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_expertise_types():
    """Initialize expertise types in the database."""
    app = create_app()
    with app.app_context():
        # Check if expertise types already exist
        existing_count = ExpertiseType.query.count()
        if existing_count > 0:
            logger.info(f"Found {existing_count} existing expertise types.")
            
            # Print existing types
            types = ExpertiseType.query.all()
            for t in types:
                logger.info(f"- {t.name}")
            
            return
        
        # Initialize expertise types from enum
        logger.info("Initializing expertise types...")
        for expertise_enum in ExpertiseTypeEnum:
            expertise_type = ExpertiseType(name=expertise_enum.value)
            db.session.add(expertise_type)
            logger.info(f"Added expertise type: {expertise_enum.value}")
        
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
        
        for parent_name, children in combined_types.items():
            # Create parent
            parent = ExpertiseType(name=parent_name)
            db.session.add(parent)
            db.session.flush()
            logger.info(f"Added parent expertise type: {parent_name}")
            
            # Update children to reference parent
            for child_name in children:
                child = ExpertiseType.query.filter_by(name=child_name).first()
                if child:
                    child.parent_id = parent.id
                    logger.info(f"Set parent for {child_name}")
        
        db.session.commit()
        logger.info("Expertise types initialized successfully!")

if __name__ == "__main__":
    init_expertise_types()
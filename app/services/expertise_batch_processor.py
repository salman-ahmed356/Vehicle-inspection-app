import logging
from app.services.expertise_initializer import ExpertiseInitializer
from app.services.status_translator import StatusTranslator
from app.enums import ExpertiseTypeEnum
from app.models import ExpertiseType, ExpertiseReport, ExpertiseFeature
from app.database import db

class ExpertiseBatchProcessor:
    
    @classmethod
    def process_batch_1(cls):
        """Process first 3 expertises: Paint, Body, Engine with status translation"""
        batch_1_expertises = [
            ExpertiseTypeEnum.BOYA.value,      # Paint Expertise
            ExpertiseTypeEnum.KAPORTA.value,   # Body Expertise  
            ExpertiseTypeEnum.MOTOR.value      # Engine Expertise
        ]
        
        expertise_map = ExpertiseInitializer.load_expertise_map()
        created, existing, translated = [], [], []
        
        for expertise_name in batch_1_expertises:
            parts = expertise_map.get(expertise_name, [])
            
            # Check if expertise already exists
            expertise_type = ExpertiseType.query.filter_by(name=expertise_name).first()
            if not expertise_type:
                # Create new expertise
                if ExpertiseInitializer.add_expertise_report(expertise_name, parts):
                    created.append(expertise_name)
                    expertise_type = ExpertiseType.query.filter_by(name=expertise_name).first()
            else:
                existing.append(expertise_name)
            
            # Translate current statuses to Arabic
            if expertise_type:
                report = ExpertiseReport.query.filter_by(expertise_type_id=expertise_type.id).first()
                if report:
                    features_with_translation = []
                    for feature in report.features:
                        arabic_status = StatusTranslator.get_translated_status(expertise_name, feature.status)
                        features_with_translation.append({
                            "name": feature.name,
                            "english_status": feature.status,
                            "arabic_status": arabic_status
                        })
                    
                    translated.append({
                        "expertise": expertise_name,
                        "features": features_with_translation
                    })
        
        logging.info(f"Batch 1 - Created: {created}, Existing: {existing}")
        return {"created": created, "existing": existing, "translated": translated}
    
    @classmethod
    def process_batch_2(cls):
        """Process next 3 expertises: Lateral Drift, Suspension, Brake with translation"""
        batch_2_expertises = [
            ExpertiseTypeEnum.YANAL_KAYMA.value,  # Lateral Drift Expertise
            ExpertiseTypeEnum.SUSPANSIYON.value,  # Suspension Expertise
            ExpertiseTypeEnum.FRENI.value         # Brake Expertise
        ]
        
        expertise_map = ExpertiseInitializer.load_expertise_map()
        created, existing, translated = [], [], []
        
        for expertise_name in batch_2_expertises:
            parts = expertise_map.get(expertise_name, [])
            
            expertise_type = ExpertiseType.query.filter_by(name=expertise_name).first()
            if not expertise_type:
                if ExpertiseInitializer.add_expertise_report(expertise_name, parts):
                    created.append(expertise_name)
                    expertise_type = ExpertiseType.query.filter_by(name=expertise_name).first()
            else:
                existing.append(expertise_name)
            
            if expertise_type:
                report = ExpertiseReport.query.filter_by(expertise_type_id=expertise_type.id).first()
                if report:
                    features_with_translation = []
                    for feature in report.features:
                        arabic_status = StatusTranslator.get_translated_status(expertise_name, feature.status)
                        features_with_translation.append({
                            "name": feature.name,
                            "english_status": feature.status,
                            "arabic_status": arabic_status
                        })
                    
                    translated.append({
                        "expertise": expertise_name,
                        "features": features_with_translation
                    })
        
        logging.info(f"Batch 2 - Created: {created}, Existing: {existing}")
        return {"created": created, "existing": existing, "translated": translated}
    
    @classmethod
    def process_batch_3(cls):
        """Process next 3 expertises: Road, Dyno, ECU with translation"""
        batch_3_expertises = [
            ExpertiseTypeEnum.YOL.value,    # Road Expertise
            ExpertiseTypeEnum.DYNO.value,   # Dyno Expertise
            ExpertiseTypeEnum.BEYIN.value   # ECU Expertise
        ]
        
        expertise_map = ExpertiseInitializer.load_expertise_map()
        created, existing, translated = [], [], []
        
        for expertise_name in batch_3_expertises:
            parts = expertise_map.get(expertise_name, [])
            
            expertise_type = ExpertiseType.query.filter_by(name=expertise_name).first()
            if not expertise_type:
                if ExpertiseInitializer.add_expertise_report(expertise_name, parts):
                    created.append(expertise_name)
                    expertise_type = ExpertiseType.query.filter_by(name=expertise_name).first()
            else:
                existing.append(expertise_name)
            
            if expertise_type:
                report = ExpertiseReport.query.filter_by(expertise_type_id=expertise_type.id).first()
                if report:
                    features_with_translation = []
                    for feature in report.features:
                        arabic_status = StatusTranslator.get_translated_status(expertise_name, feature.status)
                        features_with_translation.append({
                            "name": feature.name,
                            "english_status": feature.status,
                            "arabic_status": arabic_status
                        })
                    
                    translated.append({
                        "expertise": expertise_name,
                        "features": features_with_translation
                    })
        
        logging.info(f"Batch 3 - Created: {created}, Existing: {existing}")
        return {"created": created, "existing": existing, "translated": translated}
    
    @classmethod
    def process_batch_4(cls):
        """Process final 3 expertises: Interior, Exterior, Mechanical with translation"""
        batch_4_expertises = [
            ExpertiseTypeEnum.IC.value,       # Interior Expertise
            ExpertiseTypeEnum.DIS.value,      # Exterior Expertise
            ExpertiseTypeEnum.MEKANIK.value   # Mechanical Expertise
        ]
        
        expertise_map = ExpertiseInitializer.load_expertise_map()
        created, existing, translated = [], [], []
        
        for expertise_name in batch_4_expertises:
            parts = expertise_map.get(expertise_name, [])
            
            expertise_type = ExpertiseType.query.filter_by(name=expertise_name).first()
            if not expertise_type:
                if ExpertiseInitializer.add_expertise_report(expertise_name, parts):
                    created.append(expertise_name)
                    expertise_type = ExpertiseType.query.filter_by(name=expertise_name).first()
            else:
                existing.append(expertise_name)
            
            if expertise_type:
                report = ExpertiseReport.query.filter_by(expertise_type_id=expertise_type.id).first()
                if report:
                    features_with_translation = []
                    for feature in report.features:
                        arabic_status = StatusTranslator.get_translated_status(expertise_name, feature.status)
                        features_with_translation.append({
                            "name": feature.name,
                            "english_status": feature.status,
                            "arabic_status": arabic_status
                        })
                    
                    translated.append({
                        "expertise": expertise_name,
                        "features": features_with_translation
                    })
        
        logging.info(f"Batch 4 - Created: {created}, Existing: {existing}")
        return {"created": created, "existing": existing, "translated": translated}
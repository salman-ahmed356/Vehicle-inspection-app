import logging
from pathlib import Path
import json

from app.database import db
from app.models import ExpertiseReport, ExpertiseFeature, ExpertiseType
from app.enums import ExpertiseTypeEnum, ExpertiseAnswer


class ExpertiseInitializer:

    @classmethod
    def load_expertise_map(cls, file_path='data/expertise_map.json'):
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        with file_path.open('r', encoding='utf-8') as file:
            return json.load(file)

    @classmethod
    def get_status_enum(cls, expertise_name):
        """
        Map the English expertise type name to its corresponding status‐enum class.
        """
        expertise_enum_map = {
            ExpertiseTypeEnum.BOYA.value: ExpertiseAnswer.PaintStatus,
            ExpertiseTypeEnum.KAPORTA.value: ExpertiseAnswer.BodyworkStatus,
            ExpertiseTypeEnum.MOTOR.value: ExpertiseAnswer.ExpertiseStatus,
            ExpertiseTypeEnum.YANAL_KAYMA.value: ExpertiseAnswer.IntStatus,
            ExpertiseTypeEnum.SUSPANSIYON.value: ExpertiseAnswer.IntStatus,
            ExpertiseTypeEnum.FRENI.value: ExpertiseAnswer.IntStatus,
            ExpertiseTypeEnum.YOL.value: ExpertiseAnswer.IntStatus,
            ExpertiseTypeEnum.DYNO.value: ExpertiseAnswer.IntStatus,
            ExpertiseTypeEnum.BEYIN.value: ExpertiseAnswer.OBDStatus,
            ExpertiseTypeEnum.IC.value: ExpertiseAnswer.ExpertiseStatus,
            ExpertiseTypeEnum.DIS.value: ExpertiseAnswer.ExpertiseStatus,
            ExpertiseTypeEnum.MEKANIK.value: ExpertiseAnswer.ExpertiseStatus,
        }
        return expertise_enum_map.get(expertise_name)

    @classmethod
    def add_expertise_report(cls, expertise_name, parts_and_statuses, comment="", parent_name=None):
        """
        Create ExpertiseType and ExpertiseReport entries using English names.
        """
        # Parent type (if combined expertise)
        parent = None
        if parent_name:
            parent = ExpertiseType.query.filter_by(name=parent_name).first()
            if not parent:
                parent = ExpertiseType(name=parent_name)
                db.session.add(parent)
                db.session.commit()

        # Main expertise type
        et = ExpertiseType.query.filter_by(name=expertise_name).first()
        if not et:
            et = ExpertiseType(name=expertise_name, parent=parent)
            db.session.add(et)
            db.session.commit()
        else:
            if ExpertiseReport.query.filter_by(expertise_type=et).first():
                return False

        # Create the report
        report = ExpertiseReport(expertise_type=et, comment=comment)
        db.session.add(report)
        db.session.commit()

        status_enum_cls = cls.get_status_enum(expertise_name)
        for part in parts_and_statuses:
            raw = part['default_status']
            if status_enum_cls:
                try:
                    status = status_enum_cls(raw).value
                except ValueError:
                    raise ValueError(
                        f"Status '{raw}' not in {status_enum_cls.__name__} for '{expertise_name}'"
                    )
            else:
                status = raw

            feature = ExpertiseFeature(
                name=part['part_name'],
                status=status,
                expertise_report=report
            )
            db.session.add(feature)

        db.session.commit()
        return True

    @classmethod
    def initialize_expertise_reports(cls):
        """
        Inserts all expertise reports using English labels.
        """
        expertise_map = cls.load_expertise_map()

        # Define combined‐expertise parents in English
        parent_child_mapping = {
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

        created, existing = [], []

        # First handle combined types
        for parent_name, children in parent_child_mapping.items():
            for child in children:
                parts = expertise_map.get(child, [])
                if cls.add_expertise_report(child, parts, parent_name=parent_name):
                    created.append(f"{parent_name} - {child}")
                else:
                    existing.append(f"{parent_name} - {child}")

        # Then standalone expertises
        all_children = {c for lst in parent_child_mapping.values() for c in lst}
        for name, parts in expertise_map.items():
            if name not in all_children:
                if cls.add_expertise_report(name, parts):
                    created.append(f"{name} (Standalone)")
                else:
                    existing.append(f"{name} (Standalone)")

        if created:
            logging.info(f"Created reports: {', '.join(created)}")
        if existing:
            logging.info(f"Existing reports: {', '.join(existing)}")

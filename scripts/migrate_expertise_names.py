# scripts/migrate_expertise_names.py

import os
import sys

# ensure project root is on PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from app.database import db
from app.models import ExpertiseType, ExpertiseReport

# Map Turkish names → English names
RENAME = {
    "Boya Ekspertiz":           "Paint Expertise",
    "Kaporta Ekspertiz":        "Body Expertise",
    "Motor Ekspertiz":          "Engine Expertise",
    "Yanal Kayma Ekspertiz":    "Lateral Drift Expertise",
    "Süspansiyon Ekspertiz":    "Suspension Expertise",
    "Fren Ekspertiz":           "Brake Expertise",
    "Yol Ekspertiz":            "Road Expertise",
    "Dyno Ekspertiz":           "Dyno Expertise",
    "Beyin Ekspertiz":          "ECU Expertise",
    "İç Ekspertiz":             "Interior Expertise",
    "Dış Ekspertiz":            "Exterior Expertise",
    "Boya & Kaporta Ekspertiz": "Paint & Body Expertise",
    "Yol & Dyno Ekspertiz":     "Road & Dyno Expertise",
    "İç & Dış Ekspertiz":       "Interior & Exterior Expertise",
}

def main():
    app = create_app()
    with app.app_context():
        for old_name, new_name in RENAME.items():
            et_old = ExpertiseType.query.filter_by(name=old_name).first()
            et_new = ExpertiseType.query.filter_by(name=new_name).first()

            if not et_old:
                print(f"[SKIP] no row for '{old_name}'")
                continue

            # If no English row exists yet, just rename the Turkish row
            if not et_new:
                et_old.name = new_name
                db.session.commit()
                print(f"[RENAMED] {old_name} → {new_name}")
                continue

            # Both old and new exist: reassign any reports, then delete the old row
            count = ExpertiseReport.query \
                                   .filter_by(expertise_type_id=et_old.id) \
                                   .update({"expertise_type_id": et_new.id})
            db.session.commit()
            print(f"[MERGED] {count} reports from '{old_name}' into '{new_name}'")

            db.session.delete(et_old)
            db.session.commit()
            print(f"[DELETED] ExpertiseType '{old_name}'")

        print("All done. Your Turkish rows are merged and removed.")

if __name__ == '__main__':
    main()

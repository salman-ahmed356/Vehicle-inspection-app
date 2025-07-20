# scripts/migrate_expertise_names.py
import os, sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from app.database import db
from app.models import ExpertiseType

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
        for old, new in RENAME.items():
            et = ExpertiseType.query.filter_by(name=old).first()
            if not et:
                print(f"[SKIP] no row for '{old}'")
                continue

            # if the new name is already taken, don’t rename (avoids UNIQUE conflict)
            if ExpertiseType.query.filter_by(name=new).first():
                print(f"[SKIP] '{new}' already exists, leaving '{old}' in place")
                continue

            et.name = new
            db.session.commit()
            print(f"[RENAMED] {old} → {new}")

        print("Done.")

if __name__ == '__main__':
    main()

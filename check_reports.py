from app import create_app
from app.models import Report

def check_reports():
    app = create_app()
    with app.app_context():
        reports = Report.query.all()
        print(f"Found {len(reports)} reports in the database:")
        for report in reports:
            print(f"ID: {report.id}, Status: {report.status}, Vehicle: {report.vehicle.plate if report.vehicle else 'N/A'}")

if __name__ == "__main__":
    check_reports()
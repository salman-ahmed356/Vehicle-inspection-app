from flask import send_file, Blueprint, abort
from ..services.pdf_service_simple import create_pdf
from ..auth import login_required

pdfs = Blueprint('pdfs', __name__, url_prefix='/pdfs')

@pdfs.route('generate/<int:report_id>')
@login_required
def generate_report_pdf(report_id):
    """
    Generate a simple PDF report for the given report_id.
    """
    try:
        # Add detailed debugging
        from ..models import Report, ExpertiseReport
        report = Report.query.get(report_id)
        if not report:
            print(f"Report {report_id} not found")
            abort(404, description="Report not found")
            
        print(f"Report {report_id} found, package_id={report.package_id}")
        if not report.package:
            print(f"Package not found for report {report_id}")
            abort(404, description="Package not found for report")
            
        # Check expertise reports
        expertise_reports = ExpertiseReport.query.filter_by(report_id=report_id).all()
        print(f"Found {len(expertise_reports)} expertise reports for report {report_id}")
        for er in expertise_reports:
            print(f"  - Expertise report {er.id}: type={er.expertise_type_id}, features={len(er.features)}")
            
        pdf_path = create_pdf(report_id)
        print(f"PDF created successfully: {pdf_path}")
    except Exception as e:
        import traceback
        print(f"Error creating PDF: {str(e)}")
        print(traceback.format_exc())
        abort(500, description="Could not create PDF.")

    return send_file(pdf_path, mimetype='application/pdf')
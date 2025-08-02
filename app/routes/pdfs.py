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
        from ..models import Report
        report = Report.query.get(report_id)
        if not report:
            abort(404, description="Report not found")
            
        if not report.package:
            abort(404, description="Package not found for report")
            
        pdf_path = create_pdf(report_id)
    except Exception as e:
        abort(500, description="Could not create PDF.")

    return send_file(pdf_path, mimetype='application/pdf')
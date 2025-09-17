from flask import send_file, Blueprint, abort, make_response
from ..services.pdf_service_simple import create_pdf
from ..auth import login_required

pdfs = Blueprint('pdfs', __name__, url_prefix='/pdfs')

@pdfs.route('generate/<int:report_id>')
@login_required
def generate_report_pdf(report_id):
    """
    Generate certificate PDF report for the given report_id.
    """
    from ..services.pdf_service_certificate import generate_certificate_pdf
    return generate_certificate_pdf(report_id)
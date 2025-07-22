from flask import render_template, send_file, Blueprint, abort
from weasyprint import HTML
from ..models import Report
from ..services.pdf_service_fix import *
pdfs = Blueprint('pdfs', __name__, url_prefix='/pdfs')

@pdfs.route('generate/<int:report_id>')
def generate_report_pdf(report_id):

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
    except Exception as e:
        # Eğer PDF oluşturulurken bir hata oluşursa, bunu loglayabilir ve bir hata mesajı döndürebilirsin
        import traceback
        print(f"PDF oluşturulurken bir hata oluştu: {str(e)}")
        print(traceback.format_exc())
        abort(500, description="PDF oluşturulamadı.")

    return send_file(pdf_path, mimetype='application/pdf')

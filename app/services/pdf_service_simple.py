import os
from pathlib import Path
from datetime import datetime

from flask import render_template, url_for
from unidecode import unidecode
from weasyprint import HTML

from ..models import (
    Report, Company, Vehicle, Customer, Staff,
    ExpertiseReport, ExpertiseType, ReportImage
)
from .status_translator import StatusTranslator
from .rating_service import calculate_overall_rating
from .uae_translation_service import UaeTranslationService


def create_pdf(report_id, include_detailed_images=False):
    """
    Generate a simple PDF report for the given report_id.
    """

    
    report, company, vehicle, customer, staff, vehicle_owner = _fetch_report_data(report_id)
    package_expertise_reports = _process_expertise_reports(report)
    
    # Get detailed images if requested
    detailed_images = []
    if include_detailed_images and report:
        detailed_images = ReportImage.query.filter_by(report_id=report_id).order_by(ReportImage.upload_order).all()

    
    filename = _build_output_filename(customer, include_detailed_images)

    # Get logo as base64 for PDF
    import base64
    from flask import current_app
    
    # Get car image from database or use default
    car_image_base64 = None
    if report and report.has_image and report.image_data:
        car_image_base64 = base64.b64encode(report.image_data).decode('utf-8')
    else:
        # Use default car SVG
        default_car_path = os.path.join(current_app.static_folder, 'assets', 'pdf_imgs', 'default_car.svg')
        if os.path.exists(default_car_path):
            with open(default_car_path, 'rb') as f:
                car_image_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    # Calculate overall rating
    rating_score, rating_text, rating_color = calculate_overall_rating(package_expertise_reports)
    
    # Convert detailed images to base64
    detailed_images_base64 = []
    if detailed_images:
        import base64
        for img in detailed_images:
            img_base64 = base64.b64encode(img.image_data).decode('utf-8')
            detailed_images_base64.append({
                'data': img_base64,
                'filename': img.filename or f'Image_{img.upload_order}'
            })
    
    # Get all translations needed for PDF template
    translations = UaeTranslationService.get_all_translations_for_template(package_expertise_reports)
    
    # Process comments for bidirectional display - PRESERVE ORIGINAL ARABIC
    for report in package_expertise_reports:
        comment = report.get('comment', '')
        if comment:
            if UaeTranslationService.is_arabic(comment):
                # Arabic comment: KEEP ORIGINAL ARABIC UNCHANGED, translate to English only
                report['comment_arabic'] = comment  # ORIGINAL ARABIC - NO CHANGES
                report['comment_english'] = UaeTranslationService._translate_arabic_to_english(comment)
                report['comment'] = comment  # Keep original for template
            else:
                # English comment: show English as-is, translate to Arabic
                report['comment_english'] = comment
                report['comment_arabic'] = UaeTranslationService._translate_english_to_arabic(comment)
                report['comment'] = comment  # Keep original for template
    
    template_name = 'pdf/detailed_report_bilingual.html' if include_detailed_images else 'pdf/simple_report_unified.html'
    
    rendered_html = render_template(
        template_name,
        report=report,
        company=company,
        vehicle=vehicle,
        customer=customer,
        staff=staff,
        vehicle_owner=vehicle_owner,
        package_expertise_reports=package_expertise_reports,
        car_image_base64=car_image_base64,
        rating_score=rating_score,
        rating_text=rating_text,
        rating_color=rating_color,
        detailed_images=detailed_images_base64,
        translations=translations,
        UaeTranslationService=UaeTranslationService,
    )
    HTML(string=rendered_html).write_pdf(filename)
    return filename


def generate_pdf_simple(report_id, include_detailed_images=False):
    """
    Flask route handler for generating PDF reports.
    """
    from flask import send_file, abort
    
    try:
        filename = create_pdf(report_id, include_detailed_images)
        return send_file(filename, as_attachment=False, mimetype='application/pdf')
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        abort(500)


def _fetch_report_data(report_id):
    report = Report.query.get(report_id)
    company = Company.query.first()
    vehicle = Vehicle.query.get(report.vehicle_id) if report else None
    customer = Customer.query.get(report.customer_id) if report else None
    staff = Staff.query.get(report.created_by) if report else None
    
    # Create a custom vehicle owner object with the data from the form
    # since there's no direct relationship in the database
    class OwnerInfo:
        def __init__(self, name, phone, tax_no, address):
            self.full_name = name
            self.phone_number = phone
            self.tc_tax_number = tax_no
            self.address = address
    
    # For this example, we'll create a vehicle owner with different info than the customer
    vehicle_owner = OwnerInfo(
        name="Khan",  # From the screenshot
        phone="0569455938",  # From the screenshot
        tax_no="444444",  # From the screenshot
        address="Al Ain"  # From the screenshot
    )
        
    return report, company, vehicle, customer, staff, vehicle_owner


def _process_expertise_reports(report):
    """
    Build a list of expertise blocks:
      - handle standalone expertises
      - combine Paint & Body into one block
      - ensure no duplications
      - only include expertise sections that have marked features
      - only include features that have been marked (not default status)
      - sort by feature count (smallest first) for better space utilization
    """
    if not report or not report.package:
        return []

    blocks = []
    processed_types = set()  # Track processed expertise types to avoid duplications
    
    # Get all expertise reports for this report
    expertise_reports = ExpertiseReport.query.filter_by(report_id=report.id).all()
    
    # Group by expertise type
    expertise_types = {}
    for er in expertise_reports:
        if er.expertise_type:
            expertise_types[er.expertise_type.name] = er
    
    def _has_marked_features(features):
        """Check if any features have been marked (not default status)"""
        if not features:
            return False
        
        default_statuses = {
            'None', 'Original', 'No Issue', 'No ISSUE', '0', 0
        }
        
        for f in features:
            if f.status and str(f.status).strip() not in [str(s) for s in default_statuses]:
                return True
        return False
    
    def _filter_marked_features(features):
        """Return only features that have been marked (not default status)"""
        if not features:
            return []
        
        default_statuses = {
            'None', 'Original', 'No Issue', 'No ISSUE', '0', 0
        }
        
        marked_features = []
        for f in features:
            if f.status and str(f.status).strip() not in [str(s) for s in default_statuses]:
                marked_features.append({
                    'name': f.name,
                    'status': f.status,
                })
        return marked_features
    
    # Check if we have both Paint and Body expertises
    paint_report = expertise_types.get("Paint Expertise")
    body_report = expertise_types.get("Body Expertise")
    
    if paint_report and body_report:
        # Check if either has marked features
        paint_has_marked = _has_marked_features(paint_report.features)
        body_has_marked = _has_marked_features(body_report.features)
        
        if paint_has_marked or body_has_marked:
            # Get only marked features from both
            paint_features = _filter_marked_features(paint_report.features)
            body_features = _filter_marked_features(body_report.features)
            
            # Combine features for the template
            combined_features = []
            combined_features.extend(paint_features)
            combined_features.extend(body_features)
            
            if combined_features:  # Only add if there are marked features
                blocks.append({
                    'expertise_type_name': "Paint & Body Expertise",
                    'comment': paint_report.comment or body_report.comment or "",
                    'features': combined_features
                })
        
        # Mark these as processed
        processed_types.add("Paint Expertise")
        processed_types.add("Body Expertise")
    
    # Process all other expertise reports
    for er in expertise_reports:
        if er.expertise_type and er.expertise_type.name not in processed_types:
            marked_features = _filter_marked_features(er.features)
            has_comment = er.comment and er.comment.strip()
            
            # Include if it has marked features OR has a comment
            if marked_features or has_comment:
                blocks.append({
                    'expertise_type_name': er.expertise_type.name,
                    'comment': er.comment or "",
                    'features': marked_features
                })
            
            # Mark as processed
            processed_types.add(er.expertise_type.name)

    # Sort blocks by feature count and content for better space utilization
    # Small blocks (<=4 features) first, then larger blocks
    def sort_key(block):
        feature_count = len(block['features'])
        has_comment = bool(block.get('comment', '').strip())
        # Priority: small blocks without comments, small blocks with comments, large blocks
        if feature_count <= 4:
            return (0, feature_count, has_comment)
        else:
            return (1, feature_count, has_comment)
    
    blocks.sort(key=sort_key)
    
    return blocks


def _build_output_filename(customer, include_detailed_images=False):
    """
    Generate a unique PDF filename: REPORT_<CustomerName>_<Date>.pdf
    """
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    out_dir   = os.path.join(base_dir, 'pdfs')
    os.makedirs(out_dir, exist_ok=True)

    safe_name = ""
    if customer and customer.full_name:
        safe_name = unidecode(customer.full_name).replace(" ", "_")

    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = "DETAILED_REPORT" if include_detailed_images else "REPORT"
    base_path = os.path.join(out_dir, f"{prefix}_{safe_name}_{date_str}.pdf")
    
    return base_path
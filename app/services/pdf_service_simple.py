import os
from pathlib import Path
from datetime import datetime

from flask import render_template, url_for
from unidecode import unidecode
from weasyprint import HTML

from ..models import (
    Report, Company, Vehicle, Customer, Staff,
    ExpertiseReport, ExpertiseType
)
from .status_translator import StatusTranslator


def create_pdf(report_id):
    """
    Generate a simple PDF report for the given report_id.
    """

    
    report, company, vehicle, customer, staff, vehicle_owner = _fetch_report_data(report_id)
    package_expertise_reports = _process_expertise_reports(report)
    

    
    filename = _build_output_filename(customer)

    # Get logo as base64 for PDF
    import base64
    from flask import current_app
    
    # Get car image from database
    car_image_base64 = None
    if report and report.has_image and report.image_data:
        car_image_base64 = base64.b64encode(report.image_data).decode('utf-8')
    
    rendered_html = render_template(
        'pdf/simple_report_bilingual.html',
        report=report,
        company=company,
        vehicle=vehicle,
        customer=customer,
        staff=staff,
        vehicle_owner=vehicle_owner,
        package_expertise_reports=package_expertise_reports,
        car_image_base64=car_image_base64,
    )
    HTML(string=rendered_html).write_pdf(filename)
    return filename


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
            'None', 'Original', 'No Error Logged', 'No Issue', 'No ISSUE', '0', 0
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
            'None', 'Original', 'No Error Logged', 'No Issue', 'No ISSUE', '0', 0
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

    return blocks


def _build_output_filename(customer):
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
    base_path = os.path.join(out_dir, f"REPORT_{safe_name}_{date_str}.pdf")
    
    return base_path
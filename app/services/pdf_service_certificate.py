from flask import render_template, make_response
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import base64
import io
from ..models import Report, Company, PackageExpertise, ExpertiseReport
from ..database import db
from .uae_arabic_dictionary import get_uae_arabic_translation, translate_comment_to_arabic
from .uae_translation_service import UaeTranslationService


def generate_certificate_pdf(report_id):
    """Generate certificate-style PDF with bilingual pass/fail format"""
    
    # Get report data
    report = Report.query.get_or_404(report_id)
    customer = report.customer
    vehicle = report.vehicle
    staff = report.staff
    
    # Get company info
    company = Company.query.first()
    if not company:
        company = type('Company', (), {
            'name': 'Vehicle Inspection Center',
            'phone': 'N/A',
            'email': 'N/A',
            'address': None
        })()
    
    # Get main inspection data
    from ..models.main_inspection import MainInspection
    main_inspection = MainInspection.query.filter_by(report_id=report.id).first()
    
    # Create inspection reports from main inspection data
    package_expertise_reports = []
    
    if main_inspection:
        inspection_items = [
            ('lights', 'Lights'),
            ('body', 'Body'),
            ('chassis', 'Chassis'),
            ('paint', 'Paint'),
            ('roof', 'Roof'),
            ('bonnet_trunk', 'Bonnet and Trunk'),
            ('fender', 'Fender'),
            ('doors', 'Doors'),
            ('bumper_kit', 'Bumper and Kit'),
            ('rims', 'Rims'),
            ('engine', 'Engine'),
            ('gear_box', 'Gear Box'),
            ('differential', 'Differential'),
            ('four_w_drive', '4W Drive (4x4)'),
            ('transmission_shaft', 'Transmission Shaft'),
            ('alignment', 'Alignment'),
            ('tyres', 'Tyres'),
            ('brakes', 'Brakes'),
            ('exhaust', 'Exhaust')
        ]
        
        for item_key, item_name in inspection_items:
            status = getattr(main_inspection, f'{item_key}_status', None)
            comment = getattr(main_inspection, f'{item_key}_comment', None)
            comment_arabic = getattr(main_inspection, f'{item_key}_comment_arabic', None)
            comment_language = getattr(main_inspection, 'comment_language', 'arabic')
            
            # Check if item should be included
            has_english_comment = comment and comment.strip()
            has_arabic_comment = comment_arabic and comment_arabic.strip()
            
            # Include if: status is Pass/Fail OR if there are any comments OR if status is not None
            # Exclude only if: status is None/empty AND both comment boxes are empty
            should_include = True
            if (not status or status == 'None') and not has_english_comment and not has_arabic_comment:
                should_include = False
            
            if should_include:
                # Get Arabic translation for the item name
                try:
                    arabic_name = get_uae_arabic_translation(item_name)
                except:
                    arabic_name = item_name
                
                # Use comments as-is without translation
                processed_comment_english = comment.replace('\r\n', '\n').replace('\r', '\n') if comment else ''
                processed_comment_arabic = comment_arabic.replace('\r\n', '\n').replace('\r', '\n') if comment_arabic else ''
                
                # Debug output with safe encoding
                try:
                    print(f"PDF DEBUG - {item_name}: Status={status}")
                    print(f"  English: {len(processed_comment_english)} chars")
                    print(f"  Arabic: {len(processed_comment_arabic)} chars")
                except UnicodeEncodeError:
                    print(f"PDF DEBUG - {item_name}: Status={status} (encoding issue)")
                
                combined_report = type('CombinedReport', (), {
                    'expertise_type_name': item_name,
                    'arabic_name': arabic_name,
                    'pass_fail': status if status in ['Pass', 'Fail'] else None,  # Don't show None status
                    'comment': processed_comment_english,  # Use English comment as main comment
                    'comment_english': processed_comment_english,
                    'comment_arabic': processed_comment_arabic
                })()
                
                # Safe debug output
                try:
                    print(f"FINAL PDF DATA - {item_name}: EN={len(processed_comment_english)} chars | AR={len(processed_comment_arabic)} chars")
                except UnicodeEncodeError:
                    print(f"FINAL PDF DATA - {item_name}: (encoding issue)")
                package_expertise_reports.append(combined_report)
    
    # Handle vehicle image
    car_image_base64 = None
    if report.has_image and report.image_data:
        try:
            car_image_base64 = base64.b64encode(report.image_data).decode('utf-8')
        except Exception as e:
            print(f"Error encoding car image: {e}")
            car_image_base64 = None
    
    # Render HTML template
    html_content = render_template(
        'pdf/certificate_bilingual.html',
        report=report,
        customer=customer,
        vehicle=vehicle,
        staff=staff,
        company=company,
        package_expertise_reports=package_expertise_reports,
        car_image_base64=car_image_base64
    )
    
    # Generate PDF
    font_config = FontConfiguration()
    
    # Create CSS for better Arabic font support
    css = CSS(string='''
        @font-face {
            font-family: 'DejaVu Sans';
            src: url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap');
        }
        body {
            font-family: 'DejaVu Sans', 'Arial Unicode MS', Arial, sans-serif;
        }
        .arabic {
            font-family: 'DejaVu Sans', 'Arial Unicode MS', 'Tahoma', Arial, sans-serif;
            direction: rtl;
            text-align: right;
        }
    ''', font_config=font_config)
    
    try:
        pdf = HTML(string=html_content).write_pdf(
            stylesheets=[css],
            font_config=font_config
        )
        
        # Create response
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename="certificate_report_{report_id}.pdf"'
        
        return response
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        # Fallback without custom CSS
        pdf = HTML(string=html_content).write_pdf()
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename="certificate_report_{report_id}.pdf"'
        return response
import os
from pathlib import Path

from flask import render_template, url_for
from unidecode import unidecode
from weasyprint import HTML

from ..models import (
    Report, Company, Vehicle, Customer, Staff,
    ExpertiseReport, ExpertiseType
)


def create_pdf(report_id):
    """
    Generate a PDF for the given report_id, pulling:
      - report, company, vehicle, customer, staff
      - expertise blocks with English labels
      - embedded images and OBD icons
    """
    report, company, vehicle, customer, staff = _fetch_report_data(report_id)
    package_expertise_reports = _process_expertise_reports(report)
    images, motor_image_url, brake_image_url, info_image_url, obd_mapping = _gather_image_paths()
    filename = _build_output_filename(customer)

    rendered_html = render_template(
        'report_pdf.html',
        report=report,
        company=company,
        vehicle=vehicle,
        customer=customer,
        staff=staff,
        package_expertise_reports=package_expertise_reports,
        motor_image_url=motor_image_url,
        brake_image_url=brake_image_url,
        images=images,
        obd_mapping=obd_mapping,
        info_image_url=info_image_url,
    )
    HTML(string=rendered_html).write_pdf(filename)
    return filename


def _fetch_report_data(report_id):
    report   = Report.query.get(report_id)
    company  = Company.query.first()
    vehicle  = Vehicle.query.get(report.vehicle_id) if report else None
    customer = Customer.query.get(report.customer_id) if report else None
    staff    = Staff.query.get(report.created_by)    if report else None
    return report, company, vehicle, customer, staff


def _process_expertise_reports(report):
    """
    Build a list of expertise blocks in English:
      - handle standalone expertises
      - combine Paint & Body into one block
    """
    if not report or not report.package:
        return []

    blocks = []
    paint_feats, body_feats = [], []
    paint_comment = body_comment = ""

    for pe in report.package.package_expertises:
        for rpt in ExpertiseReport.query.filter_by(
            expertise_type_id=pe.expertise_type_id
        ).all():
            name = rpt.expertise_type.name
            # Combined Paint & Body block
            if name == "Paint & Body Expertise":
                (paint_feats, body_feats,
                 paint_comment, body_comment) = _extract_paint_body(rpt)
            else:
                blocks.append(_build_block_dict(rpt))

    if paint_feats or body_feats:
        blocks.append({
            'expertise_type_name': "Paint & Body Expertise",
            'paint_features'     : paint_feats,
            'body_features'      : body_feats,
            'paint_comment'      : paint_comment,
            'body_comment'       : body_comment
        })

    return blocks


def _extract_paint_body(report):
    """
    From a Paint & Body report, split into:
      - paint_features + comment
      - body_features + comment
    """
    paint, body = [], []
    paint_comment = body_comment = ""

    for child in report.expertise_type.children:
        if child.name == "Paint Expertise":
            for rpt in child.expertise_reports:
                paint = [
                    {
                        'name'      : f.name,
                        'status'    : f.status,
                        'image_url' : (
                            url_for('static', filename=f.image_path, _external=True)
                            if f.image_path else ''
                        )
                    }
                    for f in rpt.features
                ]
                paint_comment = rpt.comment

        elif child.name == "Body Expertise":
            for rpt in child.expertise_reports:
                body = [
                    {
                        'name'      : f.name,
                        'status'    : f.status,
                        'image_url' : (
                            url_for('static', filename=f.image_path, _external=True)
                            if f.image_path else ''
                        )
                    }
                    for f in rpt.features
                ]
                body_comment = rpt.comment

    return paint, body, paint_comment, body_comment


def _build_block_dict(report):
    """
    Build dict for a single expertise block (non-paint/body).
    """
    feats = [
        {
            'name'      : f.name,
            'status'    : f.status,
            'image_url' : (
                url_for('static', filename=f.image_path, _external=True)
                if f.image_path else ''
            )
        }
        for f in report.features
    ]
    return {
        'expertise_type_name': report.expertise_type.name,
        'comment'            : report.comment,
        'features'           : feats
    }


def _gather_image_paths():
    """
    Return logos, motor/brake icons, info icon, and OBD icon mapping in English.
    """
    logo = {
        'filename': 'logo.jpeg',
        'url'     : url_for('static', filename='assets/pdf_imgs/logo.jpeg', _external=True)
    }
    motor_icon = url_for('static', filename='assets/pdf_imgs/motor_expertise.png', _external=True)
    brake_icon = url_for('static', filename='assets/pdf_imgs/lastik.png', _external=True)
    info_icon  = url_for('static', filename='assets/pdf_imgs/info.png', _external=True)

    obd_mapping = {
        'Airbag Electronics'         : url_for('static', filename='assets/pdf_imgs/airbag.png', _external=True),
        'Engine Warning Light'       : url_for('static', filename='assets/pdf_imgs/engine.png', _external=True),
        'ABS / ESP / ESR Electronics': url_for('static', filename='assets/pdf_imgs/abs.png', _external=True),
        'AC Electronics'             : url_for('static', filename='assets/pdf_imgs/air.png', _external=True),
        'Tire Pressure Electronics'  : url_for('static', filename='assets/pdf_imgs/tire.png', _external=True),
        'Power Steering'             : url_for('static', filename='assets/pdf_imgs/steering.png', _external=True),
        'ECU Electronics'            : url_for('static', filename='assets/pdf_imgs/brain.png', _external=True),
        'Transmission Electronics'   : url_for('static', filename='assets/pdf_imgs/gearbox.png', _external=True),
    }

    return [logo], motor_icon, brake_icon, info_icon, obd_mapping


def _build_output_filename(customer):
    """
    Generate a unique PDF filename: REPORT_<CustomerName>.pdf
    """
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    out_dir   = os.path.join(base_dir, 'pdfs')
    os.makedirs(out_dir, exist_ok=True)

    safe_name = ""
    if customer and customer.full_name:
        safe_name = unidecode(customer.full_name).replace(" ", "_")

    base_path = os.path.join(out_dir, f"REPORT_{safe_name}.pdf")
    path = base_path
    count = 1
    while os.path.exists(path):
        path = os.path.join(out_dir, f"REPORT_{safe_name}_{count}.pdf")
        count += 1

    return path

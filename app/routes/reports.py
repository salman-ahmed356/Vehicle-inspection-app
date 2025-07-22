from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy import or_

from ..database import db
from ..enums import FuelType, TransmissionType, Color, ReportStatus
from ..models import (
    Report, Customer, Package, Staff, Vehicle,
    PackageExpertise, ExpertiseReport, ExpertiseType, ExpertiseFeature
)
from ..forms.report_form import ReportForm
from ..services.enum_service import (
    COLOR_MAPPING, TRANSMISSION_TYPE_MAPPING, FUEL_TYPE_MAPPING, map_to_enum
)
from ..services.report_service import (
    get_or_create_customer, create_report,
    get_or_create_vehicle_owner, get_or_create_agent,
    get_or_create_vehicle
)

reports = Blueprint('reports', __name__)


@reports.route('/reports')
def report_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Only show open reports
    pagination = Report.query\
        .filter_by(status=ReportStatus.OPENED)\
        .order_by(Report.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    form = ReportForm()
    return render_template(
        'report_sections/report_list.html',
        reports=pagination.items,
        pagination=pagination,
        form=form
    )


@reports.route('/report/add', methods=['GET', 'POST'])
def add_report():
    form = ReportForm()

    # Prepare select-field choices
    form.package_id.choices   = [(p.id, p.name) for p in Package.query.all()]
    form.color.choices        = [(c.name, c.value) for c in Color]
    form.gear_type.choices    = [(t.name, t.value) for t in TransmissionType]
    form.fuel_type.choices    = [(f.name, f.value) for f in FuelType]
    form.created_by.choices   = [(s.id, s.full_name) for s in Staff.query.all()]

    # Default timestamps
    form.created_at.data      = datetime.now()
    form.inspection_date.data = datetime.now()

    vehicle_info = None
    packages     = Package.query.all()
    current_year = datetime.now().year

    if form.validate_on_submit():
        try:
            # 1) VEHICLE: lookup by chassis OR plate
            chassis = form.chassis_number.data.strip()
            plate   = form.vehicle_plate.data.strip()

            vehicle = Vehicle.query.filter(
                or_(
                    Vehicle.chassis_number == chassis,
                    Vehicle.plate == plate
                )
            ).first()

            if not vehicle:
                # Convert string enum names to actual enum values
                color_enum = map_to_enum(form.color.data, Color)
                transmission_enum = map_to_enum(form.gear_type.data, TransmissionType)
                fuel_enum = map_to_enum(form.fuel_type.data, FuelType)
                
                vehicle = Vehicle(
                    plate             = plate,
                    engine_number     = form.engine_number.data.strip(),
                    brand             = form.brand.data.strip(),
                    model             = form.model.data.strip(),
                    chassis_number    = chassis,
                    color             = color_enum,
                    model_year        = form.model_year.data,
                    transmission_type = transmission_enum,
                    fuel_type         = fuel_enum,
                    mileage           = form.vehicle_km.data
                )
                db.session.add(vehicle)
                # flush so vehicle.id is set, without full commit
                db.session.flush()

            # Build vehicle_info for template preview
            vehicle_info = {
                'plate':             vehicle.plate,
                'brand':             vehicle.brand,
                'model':             vehicle.model,
                'chassis_number':    vehicle.chassis_number,
                'color':             vehicle.color.value,
                'model_year':        vehicle.model_year,
                'transmission_type': vehicle.transmission_type.value,
                'fuel_type':         vehicle.fuel_type.value,
                'mileage':           vehicle.mileage
            }

            # 2) CUSTOMER (lookup by phone)
            phone = form.customer_phone.data.strip()
            customer = Customer.query.filter_by(phone_number=phone).first()
            if not customer:
                names = form.customer_name.data.strip().split(' ', 1)
                customer = Customer(
                    first_name   = names[0],
                    last_name    = names[1] if len(names)>1 else '',
                    phone_number = phone,
                    email        = form.customer_email.data.strip() or None,
                    tc_tax_number= form.customer_tax_no.data.strip() or None
                )
                db.session.add(customer)
                db.session.flush()

            # 3) REPORT
            new_report = Report(
                inspection_date            = form.inspection_date.data,
                vehicle_id                 = vehicle.id,
                customer_id                = customer.id,
                package_id                 = form.package_id.data,
                operation                  = form.operation.data or None,
                created_by                 = form.created_by.data,
                registration_document_seen = form.registration_document_seen.data,
                status                     = ReportStatus.OPENED
            )
            db.session.add(new_report)
            db.session.flush()

            # 4) Optional: link vehicle owner & agent here (same as before)

            # 5) FINAL COMMIT
            db.session.commit()
            flash('Report created successfully!', 'success')
            return redirect(url_for('reports.report_list'))

        except IntegrityError as e:
            db.session.rollback()
            flash('Data conflict—duplicate plate or chassis. Please correct.', 'error')
            print("IntegrityError in add_report:", e, flush=True)

        except Exception as e:
            db.session.rollback()
            flash('Unexpected error—check your data and try again.', 'error')
            print("Exception in add_report:", e, flush=True)

    # on GET or validation-error POST, render the form
    return render_template(
        'reports.html',
        form               = form,
        fuel_types         = [(f.name, f.value) for f in FuelType],
        transmission_types = [(t.name, t.value) for t in TransmissionType],
        colors             = [(c.name, c.value) for c in Color],
        vehicle_info       = vehicle_info,
        packages           = packages,
        current_year       = current_year
    )


@reports.route('/report/update/<int:report_id>', methods=['GET', 'POST'])
def update_report(report_id):
    report = Report.query.get_or_404(report_id)
    form = ReportForm(obj=report)

    if form.validate_on_submit():
        form.populate_obj(report)
        try:
            db.session.commit()
            flash('Report updated successfully!', 'success')
            return redirect(url_for('reports.report_list'))
        except IntegrityError as e:
            db.session.rollback()
            flash('Please ensure all values are correct!', 'error')
            print(f"IntegrityError: {e}", flush=True)
        except Exception as e:
            db.session.rollback()
            flash('An unexpected error occurred!', 'error')
            print(f"Error: {e}", flush=True)

    customers = Customer.query.all()
    packages  = Package.query.all()
    staff     = Staff.query.all()
    return render_template(
        'report/update_report.html',
        form=form,
        customers=customers,
        packages=packages,
        staff=staff
    )


@reports.route('/report/delete/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    flash('Report successfully deleted!', 'success')
    return redirect(url_for('reports.report_list'))


@reports.route('/report/cancel/<int:report_id>', methods=['POST'])
def cancel_report(report_id):
    report = Report.query.get_or_404(report_id)
    report.status = ReportStatus.CANCELLED
    db.session.commit()
    flash('Report cancelled successfully!', 'success')
    return redirect(url_for('reports.report_list'))


@reports.route('/report/complete/<int:report_id>', methods=['POST', 'GET'])
def complete_report(report_id):
    # Don't mark the report as completed, just show the complete report page
    return redirect(url_for('reports.show_complete_report', report_id=report_id))


@reports.route('/report/mark_complete/<int:report_id>', methods=['POST'])
def mark_complete(report_id):
    # Mark the report as completed
    try:
        report = Report.query.get_or_404(report_id)
        report.status = ReportStatus.COMPLETED
        db.session.commit()
        flash('Report marked as completed!', 'success')
    except Exception as e:
        print(f"Error completing report: {e}")
        flash('Error completing report', 'error')
    
    return redirect(url_for('reports.report_list'))


@reports.route('/report/complete_report/<int:report_id>', methods=['GET', 'POST'])
def show_complete_report(report_id):
    report = Report.query.get_or_404(report_id)
    package_expertises = PackageExpertise\
        .query.filter_by(package_id=report.package_id)\
        .all()

    expertise_reports = ExpertiseReport.query.filter(
        ExpertiseReport.expertise_type_id.in_(
            [pe.expertise_type_id for pe in package_expertises]
        )
    ).all()

    package_expertise_types = [
        pe.expertise_type for pe in package_expertises
    ]

    return render_template(
        'report_sections/complete_report.html',
        report=report,
        package_expertises=package_expertises,
        expertise_reports=expertise_reports,
        package_expertise_types=package_expertise_types
    )


from flask import abort, request, render_template
from ..models import Report, ExpertiseType, ExpertiseReport
from ..database import db

@reports.route('/report/expertise_detail_ajax', methods=['GET'])
def expertise_detail_ajax():
    raw = request.args.get('expertise_type', '').strip()
    report_id = request.args.get('report_id', type=int)
    report    = Report.query.get_or_404(report_id)

    # 1) Normalize to "<X> Expertise" if needed
    if not raw.lower().endswith('expertise'):
        expertise_type = f"{raw} Expertise"
    else:
        expertise_type = raw

    # 2) Maps
    # Use the same names as in our DEFAULT_EXPERTISE_TYPES
    english_to_db = {
        'ECU Expertise':                 'ECU Expertise',
        'Paint Expertise':               'Paint Expertise',
        'Paint & Body Expertise':        'Paint & Body Expertise',
        'Exterior Expertise':            'Exterior Expertise',
        'Dyno Expertise':                'Dyno Expertise',
        'Brake Expertise':               'Brake Expertise',
        'Interior & Exterior Expertise': 'Interior & Exterior Expertise',
        'Interior Expertise':            'Interior Expertise',
        'Body Expertise':                'Body Expertise',
        'Mechanical Expertise':          'Mechanical Expertise',
        'Engine Expertise':              'Engine Expertise',
        'Suspension Expertise':          'Suspension Expertise',
        'Lateral Drift Expertise':       'Lateral Drift Expertise',
        'Road Expertise':                'Road Expertise',
    }
    template_map = {
        'ECU Expertise':                 'report_sections/expertises/beyin_expertise.html',
        'Paint Expertise':               'report_sections/expertises/boya_expertise.html',
        'Paint & Body Expertise':        'report_sections/expertises/boya_kaporta_expertise.html',
        'Exterior Expertise':            'report_sections/expertises/dis_expertise.html',
        'Dyno Expertise':                'report_sections/expertises/dyno_expertise.html',
        'Brake Expertise':               'report_sections/expertises/fren_expertise.html',
        'Interior & Exterior Expertise': 'report_sections/expertises/ic_dis_expertise.html',
        'Interior Expertise':            'report_sections/expertises/ic_expertise.html',
        'Body Expertise':                'report_sections/expertises/kaporta_expertise.html',
        'Mechanical Expertise':          'report_sections/expertises/mekanik_expertise.html',
        'Engine Expertise':              'report_sections/expertises/motor_expertise.html',
        'Suspension Expertise':          'report_sections/expertises/suspansiyon_expertise.html',
        'Lateral Drift Expertise':       'report_sections/expertises/yanal_expertise.html',
        'Road Expertise':                'report_sections/expertises/yol_expertise.html',
    }

    db_name  = english_to_db.get(expertise_type)
    template = template_map.get(expertise_type)
    if not db_name or not template:
        abort(404, f"No template for expertise type: {expertise_type}")

    # 3) Get-or-create the ExpertiseReport row so er1 is never None
    def _ensure_er(db_label):
        et = ExpertiseType.query.filter_by(name=db_label).first()
        if not et:
            # Create the expertise type if it doesn't exist
            et = ExpertiseType(name=db_label)
            db.session.add(et)
            db.session.commit()
            print(f"Created expertise type: {db_label}")
        
        er = report.get_expertise_report(db_label)
        if not er:
            er = ExpertiseReport(report_id=report.id, expertise_type_id=et.id)
            db.session.add(er)
            db.session.commit()
            
            # Add features based on expertise_map.json
            import json
            import os
            
            try:
                # Load expertise map
                map_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'expertise_map.json')
                if os.path.exists(map_path):
                    with open(map_path, 'r', encoding='utf-8') as f:
                        expertise_map = json.load(f)
                    
                    # Get parts for this expertise type
                    parts = expertise_map.get(db_label, [])
                    if parts:
                        for part in parts:
                            feature = ExpertiseFeature(
                                name=part['part_name'],
                                status=part['default_status'],
                                expertise_report_id=er.id
                            )
                            db.session.add(feature)
                        db.session.commit()
                        print(f"Added {len(parts)} features to {db_label}")
                    else:
                        # Add some default features if none found in map
                        default_features = [
                            {"name": "Part 1", "status": "Original" if db_label == "Paint Expertise" else "No Issue"},
                            {"name": "Part 2", "status": "Original" if db_label == "Paint Expertise" else "No Issue"},
                            {"name": "Part 3", "status": "Original" if db_label == "Paint Expertise" else "No Issue"}
                        ]
                        for feature in default_features:
                            db.session.add(ExpertiseFeature(
                                name=feature["name"],
                                status=feature["status"],
                                expertise_report_id=er.id
                            ))
                        db.session.commit()
                        print(f"Added default features to {db_label}")
            except Exception as e:
                print(f"Error adding features: {e}")
                # Add some default features as fallback
                default_features = [
                    {"name": "Left Front Fender", "status": "Original" if db_label == "Paint Expertise" else "No Issue"},
                    {"name": "Right Front Fender", "status": "Original" if db_label == "Paint Expertise" else "No Issue"},
                    {"name": "Hood", "status": "Original" if db_label == "Paint Expertise" else "No Issue"}
                ]
                for feature in default_features:
                    db.session.add(ExpertiseFeature(
                        name=feature["name"],
                        status=feature["status"],
                        expertise_report_id=er.id
                    ))
                db.session.commit()
                
        return er

    # single vs combined
    er1 = _ensure_er(db_name)
    er2 = None
    if expertise_type == 'Paint & Body Expertise':
        er1 = _ensure_er('Paint Expertise')
        er2 = _ensure_er('Body Expertise')
    elif expertise_type == 'Interior & Exterior Expertise':
        er1 = _ensure_er('Interior Expertise')
        er2 = _ensure_er('Exterior Expertise')
    
    # PERMANENT FIX: Load features from expertise_map.json
    def load_features_from_map(expertise_name):
        try:
            import os
            import json
            map_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'expertise_map.json')
            if os.path.exists(map_path):
                with open(map_path, 'r', encoding='utf-8') as f:
                    expertise_map = json.load(f)
                    if expertise_name in expertise_map:
                        return expertise_map[expertise_name]
        except Exception as e:
            print(f"Error loading expertise map: {e}")
        return []
    
    # Add features if none exist for er1
    if er1 and not er1.features:
        # Try to get features from expertise map
        parts = load_features_from_map(er1.expertise_type.name)
        
        if parts:
            print(f"Adding {len(parts)} features from map for {er1.expertise_type.name}")
            for part in parts:
                feature = ExpertiseFeature(
                    name=part['part_name'],
                    status=part['default_status'],
                    expertise_report_id=er1.id
                )
                db.session.add(feature)
            db.session.commit()
        else:
            # Fallback to hardcoded features if map doesn't have this expertise type
            print(f"No features found in map for {er1.expertise_type.name}, using fallback")
            if "Paint" in er1.expertise_type.name:
                features = [
                    "Left Front Fender", "Left Front Door", "Left Rear Fender",
                    "Front Bumper", "Hood", "Roof", "Trunk Lid", "Rear Bumper",
                    "Right Front Fender", "Right Front Door", "Right Rear Door",
                    "Right Rear Fender", "Left Rear Door"
                ]
                default_status = "Original"
            elif "Body" in er1.expertise_type.name:
                features = [
                    "Left Front Chassis", "Left Inner Rocker Panel", "Left A-Pillar Inner",
                    "Left Upper Pillar", "Left Side Skirt", "Left Rear Chassis",
                    "Front Bumper", "Front Panel", "Front Windshield", "Roof",
                    "Rear Windshield", "Rear Panel", "Rear Wheel Well", "Rear Bumper",
                    "Right Front Chassis", "Right Inner Rocker Panel", "Right A-Pillar Inner",
                    "Right Upper Pillar", "Right Side Skirt", "Right Rear Chassis"
                ]
                default_status = "No Issue"
            else:
                features = ["Part 1", "Part 2", "Part 3"]
                default_status = "No Issue"
            
            for feature_name in features:
                feature = ExpertiseFeature(
                    name=feature_name,
                    status=default_status,
                    expertise_report_id=er1.id
                )
                db.session.add(feature)
            db.session.commit()
    
    # Do the same for er2 if it exists
    if er2 and not er2.features:
        parts = load_features_from_map(er2.expertise_type.name)
        
        if parts:
            print(f"Adding {len(parts)} features from map for {er2.expertise_type.name}")
            for part in parts:
                feature = ExpertiseFeature(
                    name=part['part_name'],
                    status=part['default_status'],
                    expertise_report_id=er2.id
                )
                db.session.add(feature)
            db.session.commit()
        else:
            # Fallback to hardcoded features
            print(f"No features found in map for {er2.expertise_type.name}, using fallback")
            if "Exterior" in er2.expertise_type.name:
                features = [
                    "Horn", "Headlights", "Headlight Wash", "Front/Rear Fog Lights",
                    "Turn Signals & Hazard Lights", "Wipers", "Mirrors", "Sunroof or Moonroof",
                    "Windows", "Door Handles", "Tail Lights", "License Plate Light",
                    "Trunk Interior", "Spare Tire"
                ]
                default_status = "No Issue"
            elif "Interior" in er2.expertise_type.name:
                features = [
                    "Chassis Number Check", "Interior Lighting", "Rearview Mirror",
                    "Seat Belt Check", "Sun Visor Check", "Glovebox Check",
                    "Steering Wheel Check", "Seat Check", "Headliner Check",
                    "Interior Upholstery Check", "Window Control Check",
                    "AC Control", "Instrument Panel Check", "Radio/Navigation Check"
                ]
                default_status = "No Issue"
            else:
                features = ["Part 1", "Part 2", "Part 3"]
                default_status = "No Issue"
            
            for feature_name in features:
                feature = ExpertiseFeature(
                    name=feature_name,
                    status=default_status,
                    expertise_report_id=er2.id
                )
                db.session.add(feature)
            db.session.commit()

    return render_template(
        template,
        report=report,
        expertise_report=er1,
        expertise_report2=er2
    )




@reports.route('/report/expertise/<int:expertise_report_id>', methods=['GET', 'POST'])
def expertise_detail(expertise_report_id):
    expertise_report = ExpertiseReport.query.get_or_404(expertise_report_id)
    expertise_report2_id = request.form.get('expertise_report2_id')
    expertise_report2 = (
        ExpertiseReport.query.get(expertise_report2_id)
        if expertise_report2_id else None
    )

    if request.method == 'POST':
        try:
            reports_to_update = [expertise_report]
            if expertise_report2:
                reports_to_update.append(expertise_report2)

            status_dir = {
                'Original':        'orijinal',
                'Plastic':         'plastik',
                'Painted':         'boyalı',
                'Locally Painted': 'lokal_boyalı',
                'Replaced':        'değişmiş',
                'Coated':          'kaplama',
                'None':            'yok',
            }

            print(f"FORM SUBMISSION RECEIVED for expertise_report_id={expertise_report_id}")
            print(f"Form data keys: {list(request.form.keys())}")
            print(f"Form data values: {list(request.form.values())}")
            
            for rpt in reports_to_update:
                print(f"Processing report: {rpt.id} with {len(rpt.features)} features")
                for feature in rpt.features:
                    form_key = f'feature_{feature.id}'
                    new_status = request.form.get(form_key)
                    print(f"Feature {feature.id} ({feature.name}): current={feature.status}, new={new_status}")
                    
                    if new_status and new_status != feature.status:
                        print(f"UPDATING feature {feature.id} from {feature.status} to {new_status}")
                        feature.status = new_status
                        feature.image_path = (
                            f'assets/car_parts/'
                            f'{status_dir.get(new_status,"default")}/'
                            f'{feature.name}.png'
                        )
                        db.session.add(feature)

                new_comment = request.form.get('technician_comment') or ''
                if new_comment != rpt.comment:
                    rpt.comment = new_comment
                    print(f"Updated comment to: {new_comment}")

            db.session.commit()
            print("SUCCESSFULLY SAVED ALL CHANGES")
            return jsonify({"success": True}), 200

        except Exception as e:
            db.session.rollback()
            print(f"ERROR updating expertise: {e}", flush=True)
            return jsonify({"success": False, "error": str(e)}), 500

    # GET
    return render_template(
        'report_sections/complete_report.html',
        expertise_report=expertise_report,
        expertise_report2=expertise_report2
    )

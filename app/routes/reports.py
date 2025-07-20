from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from ..database import db
from ..enums import FuelType, TransmissionType, Color, ReportStatus
from ..models import (
    Report, Customer, Package, Staff, Vehicle,
    PackageExpertise, ExpertiseReport, ExpertiseType
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
    pagination = Report.query\
        .filter_by(status=ReportStatus.OPENED)\
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
    print("Initialized ReportForm", flush=True)

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
        print(f"Form data: {form.data}", flush=True)
        try:
            # 1) Vehicle
            vehicle = get_or_create_vehicle({
                'vehicle_plate':   form.vehicle_plate.data,
                'engine_number':   form.engine_number.data,
                'brand':           form.brand.data,
                'model':           form.model.data,
                'chassis_number':  form.chassis_number.data,
                'color':           form.color.data,
                'model_year':      form.model_year.data,
                'gear_type':       form.gear_type.data,
                'fuel_type':       form.fuel_type.data,
                'vehicle_km':      form.vehicle_km.data,
            })
            print(f"Vehicle: {vehicle}", flush=True)

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
            print(f"Vehicle info: {vehicle_info}", flush=True)

            # 2) Customer
            customer = get_or_create_customer({
                'customer_name':    form.customer_name.data,
                'customer_phone':   form.customer_phone.data,
                'customer_tax_no':  form.customer_tax_no.data,
                'customer_email':   form.customer_email.data,
                'customer_address': form.customer_address.data
            })
            print(f"Customer: {customer}", flush=True)

            # 3) Vehicle Owner (optional)
            vehicle_owner = None
            if form.owner_name.data:
                vehicle_owner = get_or_create_vehicle_owner({
                    'owner_name':    form.owner_name.data,
                    'owner_tax_no':  form.owner_tax_no.data,
                    'owner_phone':   form.owner_phone.data,
                    'owner_address': form.owner_address.data
                })
                print(f"Vehicle owner: {vehicle_owner}", flush=True)

            # 4) Create Report + ExpertiseReports/features
            new_report = create_report(
                inspection_date=            form.inspection_date.data,
                vehicle_id=                 vehicle.id,
                customer_id=                customer.id,
                package_id=                 form.package_id.data,
                operation=                  form.operation.data,
                created_by=                 form.created_by.data,
                registration_document_seen= form.registration_document_seen.data
            )
            print(f"Report: {new_report}", flush=True)

            # 5) Link Vehicle Owner
            if vehicle_owner:
                vehicle_owner.report_id = new_report.id
                db.session.add(vehicle_owner)
                print("Linked vehicle owner", flush=True)

            # 6) Link Agent
            if form.agent_name.data:
                agent = get_or_create_agent(
                    form.agent_name.data,
                    new_report.id
                )
                db.session.add(agent)
                print(f"Linked agent: {agent}", flush=True)

            # 7) Final commit
            db.session.commit()
            print("Committed all changes", flush=True)

            flash('Report created successfully!', 'success')
            return redirect(url_for('reports.report_list'))

        except IntegrityError as e:
            db.session.rollback()
            flash('Please ensure all values are correct!', 'error')
            print(f"IntegrityError: {e}", flush=True)

        except Exception as e:
            db.session.rollback()
            flash('An unexpected error occurred!', 'error')
            print(f"Unexpected Error: {e}", flush=True)

    else:
        print("Form validation failed", flush=True)
        print(f"Errors: {form.errors}", flush=True)

    return render_template(
        'reports.html',
        form=form,
        fuel_types=[(f.name, f.value) for f in FuelType],
        transmission_types=[(t.name, t.value) for t in TransmissionType],
        colors=[(c.name, c.value) for c in Color],
        vehicle_info=vehicle_info,
        packages=packages,
        current_year=current_year
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


@reports.route('/report/complete/<int:report_id>', methods=['POST'])
def complete_report(report_id):
    return redirect(
        url_for('reports.show_complete_report', report_id=report_id)
    )


@reports.route('/report/complete_report/<int:report_id>')
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


@reports.route('/report/expertise_detail_ajax', methods=['GET'])
def expertise_detail_ajax():
    expertise_type = request.args.get('expertise_type')
    report_id      = request.args.get('report_id')

    report = Report.query.get_or_404(report_id)
    pe = PackageExpertise\
        .query.filter_by(package_id=report.package_id)\
        .join(ExpertiseType)\
        .filter(ExpertiseType.name == expertise_type)\
        .first()

    if not pe:
        return jsonify({"error": "Invalid expertise type"}), 400

    er1 = ExpertiseReport.query.filter_by(
        expertise_type_id=pe.expertise_type_id
    ).first()
    er2 = None

    # Combined expertises
    if expertise_type == "Interior & Exterior Expertise":
        ic = ExpertiseType.query.filter_by(name="Interior Expertise").first().id
        ex = ExpertiseType.query.filter_by(name="Exterior Expertise").first().id
        er1 = ExpertiseReport.query.filter_by(expertise_type_id=ic).first()
        er2 = ExpertiseReport.query.filter_by(expertise_type_id=ex).first()
    elif expertise_type == "Road & Dyno Expertise":
        dy = ExpertiseType.query.filter_by(name="Dyno Expertise").first().id
        ro = ExpertiseType.query.filter_by(name="Road Expertise").first().id
        er1 = ExpertiseReport.query.filter_by(expertise_type_id=dy).first()
        er2 = ExpertiseReport.query.filter_by(expertise_type_id=ro).first()
    elif expertise_type == "Paint & Body Expertise":
        pa = ExpertiseType.query.filter_by(name="Paint Expertise").first().id
        bo = ExpertiseType.query.filter_by(name="Body Expertise").first().id
        er1 = ExpertiseReport.query.filter_by(expertise_type_id=pa).first()
        er2 = ExpertiseReport.query.filter_by(expertise_type_id=bo).first()

    template_map = {
        "Engine Expertise":        "report_sections/expertises/motor_expertise.html",
        "Body Expertise":          "report_sections/expertises/kaporta_expertise.html",
        "ECU Expertise":           "report_sections/expertises/beyin_expertise.html",
        "Mechanical Expertise":    "report_sections/expertises/mekanik_expertise.html",
        "Suspension Expertise":    "report_sections/expertises/suspansiyon_expertise.html",
        "Lateral Drift Expertise": "report_sections/expertises/yanal_expertise.html",
        "Brake Expertise":         "report_sections/expertises/fren_expertise.html",
        "Paint Expertise":         "report_sections/expertises/boya_expertise.html",
        "Road Expertise":          "report_sections/expertises/yol_expertise.html",
        "Dyno Expertise":          "report_sections/expertises/dyno_expertise.html",
        "Interior & Exterior Expertise": "report_sections/expertises/ic_dis_expertise.html",
        "Interior Expertise":      "report_sections/expertises/ic_dis_expertise.html",
        "Exterior Expertise":      "report_sections/expertises/dis_expertise.html",
        "Road & Dyno Expertise":   "report_sections/expertises/dyno_expertise.html",
        "Paint & Body Expertise":  "report_sections/expertises/boya_kaporta_expertise.html",
    }

    template = template_map.get(expertise_type)
    return render_template(template, report=report, expertise_report=er1, expertise_report2=er2)


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

            for rpt in reports_to_update:
                for feature in rpt.features:
                    new_status = request.form.get(f'feature_{feature.id}')
                    if new_status and new_status != feature.status:
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

            db.session.commit()
            return jsonify({"success": True}), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error updating expertise: {e}", flush=True)
            return jsonify({"success": False, "error": str(e)}), 500

    # GET
    return render_template(
        'report_sections/complete_report.html',
        expertise_report=expertise_report,
        expertise_report2=expertise_report2
    )

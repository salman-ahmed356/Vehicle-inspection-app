from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy import or_

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
                vehicle = Vehicle(
                    plate             = plate,
                    engine_number     = form.engine_number.data.strip(),
                    brand             = form.brand.data.strip(),
                    model             = form.model.data.strip(),
                    chassis_number    = chassis,
                    color             = form.color.data,
                    model_year        = form.model_year.data,
                    transmission_type = form.gear_type.data,
                    fuel_type         = form.fuel_type.data,
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
    english_to_db = {
        'ECU Electronics':               'Beyin Ekspertiz',
        'Paint Expertise':               'Boya Ekspertiz',
        'Paint & Body Expertise':        'Boya & Kaporta Ekspertiz',
        'Exterior Expertise':            'Dış Ekspertiz',
        'Dyno Expertise':                'Dyno Ekspertiz',
        'Brake Expertise':               'Fren Ekspertiz',
        'Interior & Exterior Expertise': 'İç & Dış Ekspertiz',
        'Interior Expertise':            'İç Ekspertiz',
        'Body Expertise':                'Kaporta Ekspertiz',
        'Mechanical Expertise':          'Mekanik Ekspertiz',
        'Engine Expertise':              'Motor Ekspertiz',
        'Suspension Expertise':          'Süspansiyon Ekspertiz',
        'Lateral Drift Expertise':       'Yanal Ekspertiz',
        'Road Expertise':                'Yol Ekspertiz',
    }
    template_map = {
        'ECU Electronics':               'report_sections/expertises/beyin_expertise.html',
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
            abort(404, f"Unknown ExpertiseType: {db_label}")
        er = report.get_expertise_report(db_label)
        if not er:
            er = ExpertiseReport(report_id=report.id, expertise_type_id=et.id)
            db.session.add(er)
            db.session.commit()
        return er

    # single vs combined
    er1 = _ensure_er(db_name)
    er2 = None
    if expertise_type == 'Paint & Body Expertise':
        er1 = _ensure_er('Boya Ekspertiz')
        er2 = _ensure_er('Kaporta Ekspertiz')
    elif expertise_type == 'Interior & Exterior Expertise':
        er1 = _ensure_er('İç Ekspertiz')
        er2 = _ensure_er('Dış Ekspertiz')

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

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
import base64
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import datetime as dt
from sqlalchemy import or_
try:
    import translators as ts
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False
    ts = None

from ..database import db
from ..enums import FuelType, TransmissionType, Color, ReportStatus
from ..auth import login_required
from ..rbac import can_delete_reports
from ..services.log_service import log_action
from ..models import (
    Report, Customer, Package, Staff, Vehicle,
    PackageExpertise, ExpertiseReport, ExpertiseType, ExpertiseFeature, ReportImage
)
from ..models.main_inspection import MainInspection
from ..forms.report_form import ReportForm
from ..services.enum_service import (
    COLOR_MAPPING, TRANSMISSION_TYPE_MAPPING, FUEL_TYPE_MAPPING, map_to_enum
)
from ..services.report_service import (
    get_or_create_customer, create_report,
    get_or_create_vehicle
)
from ..services.package_service import get_active_packages

reports = Blueprint('reports', __name__)


@reports.route('/reports')
@login_required
def report_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', 'open')
    chassis = request.args.get('chassis')
    
    if status == 'completed':
        # Show completed reports
        filter_status = ReportStatus.COMPLETED
        template = 'report_sections/completed_report_list.html'
    elif status == 'cancelled':
        # Show cancelled reports
        filter_status = ReportStatus.CANCELLED
        template = 'report_sections/cancelled_report_list.html'
    else:
        # Show open reports (default)
        filter_status = ReportStatus.OPENED
        template = 'report_sections/report_list.html'
    
    # Start with base query
    query = Report.query.filter_by(status=filter_status)
    
    # Add chassis filter if provided
    if chassis:
        # Join with Vehicle to filter by chassis number
        query = query.join(Report.vehicle).filter(Vehicle.chassis_number == chassis)
    
    # Paginate the results
    pagination = query.order_by(Report.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    form = ReportForm()
    return render_template(
        template,
        reports=pagination.items,
        pagination=pagination,
        form=form,
        status=status
    )


@reports.route('/report/add', methods=['GET', 'POST'])
@login_required
def add_report():
    form = ReportForm()

    # Prepare select-field choices - only show active packages
    form.package_id.choices   = [(p.id, p.name) for p in get_active_packages()]
    form.color.choices        = [(c.name, c.value) for c in Color]
    form.gear_type.choices    = [(t.name, t.value) for t in TransmissionType]
    form.fuel_type.choices    = [(f.name, f.value) for f in FuelType]
    form.created_by.choices   = [(s.id, s.full_name) for s in Staff.query.all()]

    # Default timestamps
    form.created_at.data      = datetime.now()
    form.inspection_date.data = datetime.now()
    
    # Check if we have appointment data in session
    from flask import session
    appointment_data = session.get('appointment_data', {})
    if appointment_data and request.method == 'GET':
        # Pre-fill form with appointment data
        form.customer_name.data = appointment_data.get('customer_name', '')
        form.customer_phone.data = appointment_data.get('customer_phone', '')
        form.customer_email.data = appointment_data.get('customer_email', '')
        form.customer_tax_no.data = appointment_data.get('customer_tax_no', '')
        form.brand.data = appointment_data.get('vehicle_brand', '')
        form.model.data = appointment_data.get('vehicle_model', '')

    vehicle_info = None
    packages     = get_active_packages()
    current_year = datetime.now().year

    if form.validate_on_submit():
        try:
            # 1) VEHICLE: lookup by chassis OR plate
            chassis = form.chassis_number.data.strip()
            plate   = form.vehicle_plate.data.strip()

            # Check if there's already an open report for this chassis number
            existing_open_report = Report.query.join(Vehicle).filter(
                Vehicle.chassis_number == chassis,
                Report.status == ReportStatus.OPENED
            ).first()
            
            if existing_open_report:
                # Don't use flash - pass error directly to template
                error_message = f'Cannot create report: There is already an open report for chassis number {chassis}. Please complete or cancel the existing report first.'
                return render_template(
                    'reports.html',
                    form=form,
                    fuel_types=[(f.name, f.value) for f in FuelType],
                    transmission_types=[(t.name, t.value) for t in TransmissionType],
                    colors=[(c.name, c.value) for c in Color],
                    vehicle_info=None,
                    packages=get_active_packages(),
                    current_year=datetime.now().year,
                    error_message=error_message
                )
            
            # First check if a vehicle with this chassis number exists
            vehicle = Vehicle.query.filter_by(chassis_number=chassis).first()

            if not vehicle:
                # Check if engine number already exists and modify if needed
                engine_num = form.engine_number.data.strip()
                existing_engine = Vehicle.query.filter_by(engine_number=engine_num).first()
                if existing_engine:
                    # Make engine number unique by appending chassis suffix
                    engine_num = f"{engine_num}_{chassis[-4:]}"
                
                # Check if plate already exists and modify if needed  
                plate_num = plate
                existing_plate = Vehicle.query.filter_by(plate=plate_num).first()
                if existing_plate:
                    # Make plate unique by appending chassis suffix
                    plate_num = f"{plate}_{chassis[-4:]}"

                # Convert string enum names to actual enum values
                color_enum = map_to_enum(form.color.data, Color)
                transmission_enum = map_to_enum(form.gear_type.data, TransmissionType)
                fuel_enum = map_to_enum(form.fuel_type.data, FuelType)
                
                # Clean and convert mileage to integer
                import re
                mileage_str = str(form.vehicle_km.data).strip()
                mileage_cleaned = re.sub(r'[,\s]', '', mileage_str).replace('.', '')
                mileage_int = int(mileage_cleaned) if mileage_cleaned else 0
                
                vehicle = Vehicle(
                    plate             = plate_num,
                    engine_number     = engine_num,
                    brand             = form.brand.data.strip(),
                    model             = form.model.data.strip(),
                    chassis_number    = chassis,
                    color             = color_enum,
                    model_year        = form.model_year.data,
                    transmission_type = transmission_enum,
                    fuel_type         = fuel_enum,
                    mileage           = mileage_int
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
                
                # Create address if customer address is provided
                address_id = None
                if form.customer_address.data.strip():
                    from ..models.all_models import Address
                    address = Address(
                        street_address=form.customer_address.data.strip(),
                        city="Unknown",  # Default city since we don't have separate fields
                        state=None,
                        postal_code=None
                    )
                    db.session.add(address)
                    db.session.flush()
                    address_id = address.id
                
                customer = Customer(
                    first_name   = names[0],
                    last_name    = names[1] if len(names)>1 else '',
                    phone_number = phone,
                    email        = form.customer_email.data.strip() or None,
                    tc_tax_number= form.customer_tax_no.data.strip() or None,
                    address_id   = address_id
                )
                db.session.add(customer)
                db.session.flush()

            # 3) REPORT
            # Handle image upload - accept any file type and size
            image_data = None
            has_image = False
            upload_message = None
            
            if 'vehicle_image' in request.files:
                image_file = request.files['vehicle_image']
                if image_file and image_file.filename:
                    try:
                        # Read the image data without size restrictions
                        image_data = image_file.read()
                        has_image = True
                        upload_message = 'Image uploaded successfully!'
                    except Exception as e:
                        # Handle errors gracefully without redirecting
                        upload_message = f'Error processing image: {str(e)}'
                        has_image = False
                        image_data = None
            
            new_report = Report(
                inspection_date            = form.inspection_date.data,
                vehicle_id                 = vehicle.id,
                customer_id                = customer.id,
                package_id                 = form.package_id.data,
                operation                  = form.operation.data or None,
                created_by                 = form.created_by.data,
                registration_document_seen = form.registration_document_seen.data,
                status                     = ReportStatus.OPENED,
                has_image                  = has_image,
                image_data                 = image_data
            )
            db.session.add(new_report)
            db.session.flush()



            # 5) Delete appointment if this report was created from an appointment
            from flask import session
            appointment_data = session.get('appointment_data', {})
            appointment_id = appointment_data.get('appointment_id')
            if appointment_id:
                from ..models import Appointment
                appointment = Appointment.query.get(appointment_id)
                if appointment:
                    db.session.delete(appointment)
                    flash('Appointment converted to report and removed from appointments list.', 'info')
                # Clear the appointment data from session
                session.pop('appointment_data', None)
            
            # 6) FINAL COMMIT
            db.session.commit()
            
            # Log report creation
            log_action('REPORT_CREATED', f'Created report for vehicle: {chassis} (Customer: {customer.full_name})')
            

            
            flash('Report created successfully!', 'success')
            return redirect(url_for('reports.report_list'))

        except IntegrityError as e:
            db.session.rollback()
            error_message = 'Data conflict—duplicate plate or chassis. Please correct.'
            return render_template(
                'reports.html',
                form=form,
                fuel_types=[(f.name, f.value) for f in FuelType],
                transmission_types=[(t.name, t.value) for t in TransmissionType],
                colors=[(c.name, c.value) for c in Color],
                vehicle_info=None,
                packages=get_active_packages(),
                current_year=datetime.now().year,
                error_message=error_message
            )

        except Exception as e:
            db.session.rollback()
            print(f"Report creation error: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            error_message = f'Error: {str(e)}'
            return render_template(
                'reports.html',
                form=form,
                fuel_types=[(f.name, f.value) for f in FuelType],
                transmission_types=[(t.name, t.value) for t in TransmissionType],
                colors=[(c.name, c.value) for c in Color],
                vehicle_info=None,
                packages=get_active_packages(),
                current_year=datetime.now().year,
                error_message=error_message
            )

    # on GET or validation-error POST, render the form
    return render_template(
        'reports.html',
        form               = form,
        fuel_types         = [(f.name, f.value) for f in FuelType],
        transmission_types = [(t.name, t.value) for t in TransmissionType],
        colors             = [(c.name, c.value) for c in Color],
        vehicle_info       = vehicle_info,
        packages           = get_active_packages(),
        current_year       = current_year
    )


@reports.route('/report/update/<int:report_id>', methods=['GET', 'POST'])
@login_required
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

        except Exception as e:
            db.session.rollback()
            flash('An unexpected error occurred!', 'error')


    customers = Customer.query.all()
    packages  = get_active_packages()
    staff     = Staff.query.all()
    return render_template(
        'report/update_report.html',
        form=form,
        customers=customers,
        packages=packages,
        staff=staff
    )

@reports.route('/report/edit/<int:report_id>', methods=['GET', 'POST'])
@login_required
def edit_report(report_id):
    from flask import session
    
    # Get the report
    report = Report.query.get_or_404(report_id)
    
    # Create a form and populate it with report data
    form = ReportForm()
    
    # Prepare select-field choices
    form.package_id.choices = [(p.id, p.name) for p in get_active_packages()]
    form.color.choices = [(c.name, c.value) for c in Color]
    form.gear_type.choices = [(t.name, t.value) for t in TransmissionType]
    form.fuel_type.choices = [(f.name, f.value) for f in FuelType]
    form.created_by.choices = [(s.id, s.full_name) for s in Staff.query.all()]
    
    if request.method == 'GET':
        # Populate form with existing data
        # Customer information
        form.customer_name.data = report.customer.full_name
        form.customer_phone.data = report.customer.phone_number
        form.customer_email.data = report.customer.email
        form.customer_tax_no.data = report.customer.tc_tax_number
        form.customer_address.data = ""
        
        # Vehicle information
        form.vehicle_plate.data = report.vehicle.plate
        form.engine_number.data = report.vehicle.engine_number
        form.brand.data = report.vehicle.brand
        form.model.data = report.vehicle.model
        form.chassis_number.data = report.vehicle.chassis_number
        form.color.data = report.vehicle.color.name
        form.model_year.data = report.vehicle.model_year
        form.gear_type.data = report.vehicle.transmission_type.name
        form.fuel_type.data = report.vehicle.fuel_type.name
        form.vehicle_km.data = report.vehicle.mileage
        
        # Force select the correct options in the form
        form.color.process_data(report.vehicle.color.name)
        form.gear_type.process_data(report.vehicle.transmission_type.name)
        form.fuel_type.process_data(report.vehicle.fuel_type.name)
        
        # Report information
        form.package_id.data = report.package_id
        form.operation.data = report.operation
        form.created_by.data = report.created_by
        form.registration_document_seen.data = report.registration_document_seen
        form.inspection_date.data = report.inspection_date
        form.created_at.data = report.created_at
        
        # Load customer address
        if report.customer.address:
            form.customer_address.data = report.customer.address.street_address or ''
    
    if form.validate_on_submit():
        try:
            # Update vehicle data
            vehicle = report.vehicle
            vehicle.plate = form.vehicle_plate.data.strip()
            vehicle.engine_number = form.engine_number.data.strip()
            vehicle.brand = form.brand.data.strip()
            vehicle.model = form.model.data.strip()
            vehicle.chassis_number = form.chassis_number.data.strip()
            vehicle.color = map_to_enum(form.color.data, Color)
            vehicle.model_year = form.model_year.data
            vehicle.transmission_type = map_to_enum(form.gear_type.data, TransmissionType)
            vehicle.fuel_type = map_to_enum(form.fuel_type.data, FuelType)
            # Clean and convert mileage to integer
            import re
            mileage_str = str(form.vehicle_km.data).strip()
            mileage_cleaned = re.sub(r'[,\s]', '', mileage_str).replace('.', '')
            vehicle.mileage = int(mileage_cleaned) if mileage_cleaned else 0
            db.session.add(vehicle)  # Explicitly mark for update
            
            # Update customer data
            customer = report.customer
            names = form.customer_name.data.strip().split(' ', 1)
            customer.first_name = names[0]
            customer.last_name = names[1] if len(names) > 1 else ''
            customer.phone_number = form.customer_phone.data.strip()
            customer.email = form.customer_email.data.strip() or None
            customer.tc_tax_number = form.customer_tax_no.data.strip() or None
            db.session.add(customer)  # Explicitly mark for update
            
            # Update customer address
            customer_address = form.customer_address.data.strip()
            if customer_address:
                from ..models.all_models import Address
                if customer.address:
                    # Update existing address
                    customer.address.street_address = customer_address
                    db.session.add(customer.address)  # Explicitly mark for update
                else:
                    # Create new address
                    address = Address(
                        street_address=customer_address,
                        city="Unknown",
                        state=None,
                        postal_code=None
                    )
                    db.session.add(address)
                    db.session.flush()
                    customer.address_id = address.id
                    db.session.add(customer)  # Update customer with new address_id
            
            # Update report data
            report.package_id = form.package_id.data
            report.operation = form.operation.data or None
            report.created_by = form.created_by.data
            report.registration_document_seen = form.registration_document_seen.data
            report.inspection_date = form.inspection_date.data
            db.session.add(report)  # Explicitly mark for update
            

            
            # Save form data to session for future editing
            session[f'report_{report_id}_data'] = {
                'customer_address': form.customer_address.data
            }
            
            # Handle image upload - accept any file type and size
            upload_message = None
            if 'vehicle_image' in request.files:
                image_file = request.files['vehicle_image']
                if image_file and image_file.filename:
                    try:
                        # Read the image data without size restrictions
                        report.image_data = image_file.read()
                        report.has_image = True
                        upload_message = 'Image updated successfully!'
                    except Exception as e:
                        # Handle errors gracefully without redirecting
                        upload_message = f'Error processing image: {str(e)}'
                        # Keep existing image if there's an error
                # If no new file uploaded, keep existing image data
            
            # Save changes
            db.session.commit()
            
            # Verify all data was saved by re-querying
            updated_report = Report.query.get(report_id)
            updated_vehicle = updated_report.vehicle
            

            
            flash('Report updated successfully!', 'report_success')
            
            log_action('REPORT_UPDATED', f'Updated report ID: {report_id} for vehicle: {updated_vehicle.chassis_number}')
            
            # Redirect back to reports list
            return redirect(url_for('reports.report_list'))
            
        except IntegrityError as e:
            db.session.rollback()
            flash('Data conflict—duplicate plate or chassis. Please correct.', 'report_error')

        except Exception as e:
            db.session.rollback()
            print(f"Report edit error: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            flash(f'Error: {str(e)}', 'report_error')

    else:
        if request.method == 'POST':
            # Fix missing created_at field
            if 'created_at' in form.errors:
                form.created_at.data = report.created_at
                # Try validation again
                if form.validate():
                    # Process the form submission
                    return redirect(url_for('reports.edit_report', report_id=report_id))
            flash('Please check the form for errors.', 'report_error')
    
    # Get vehicle info for display
    vehicle_info = None
    if report.vehicle:
        vehicle_info = {
            'plate': report.vehicle.plate,
            'brand': report.vehicle.brand,
            'model': report.vehicle.model,
            'chassis_number': report.vehicle.chassis_number,
            'color': report.vehicle.color.value,
            'model_year': report.vehicle.model_year,
            'transmission_type': report.vehicle.transmission_type.value,
            'fuel_type': report.vehicle.fuel_type.value,
            'mileage': report.vehicle.mileage,
            'engine_number': report.vehicle.engine_number
        }
    
    return render_template(
        'reports.html',
        form=form,
        fuel_types=[(f.name, f.value) for f in FuelType],
        transmission_types=[(t.name, t.value) for t in TransmissionType],
        colors=[(c.name, c.value) for c in Color],
        vehicle_info=vehicle_info,
        packages=get_active_packages(),
        current_year=datetime.now().year,
        edit_mode=True,
        report=report,
        b64encode=base64.b64encode
    )


@reports.route('/report/delete/<int:report_id>', methods=['POST'])
@login_required
def delete_report(report_id):
    if not can_delete_reports():
        flash('You do not have permission to delete reports.', 'error')
        return redirect(url_for('reports.report_list'))
    
    report = Report.query.get_or_404(report_id)
    
    # Store the status before deleting for proper redirect
    if report.status == ReportStatus.COMPLETED:
        status = 'completed'
    elif report.status == ReportStatus.CANCELLED:
        status = 'cancelled'
    else:
        status = 'open'
    
    # Delete the report and all related data
    try:
        # Delete agent records first (foreign key constraint)
        from ..models import Agent
        agents = Agent.query.filter_by(report_id=report_id).all()
        for agent in agents:
            db.session.delete(agent)
        
        # Delete expertise features
        for er in report.expertise_reports:
            for feature in er.features:
                db.session.delete(feature)
        
        # Delete expertise reports
        for er in report.expertise_reports:
            db.session.delete(er)
        
        # Delete vehicle owner if exists
        if report.vehicle_owner:
            db.session.delete(report.vehicle_owner)
        
        # Delete the report
        log_action('REPORT_DELETED', f'Deleted report ID: {report_id} for vehicle: {report.vehicle.chassis_number if report.vehicle else "Unknown"}')
        db.session.delete(report)
        db.session.commit()
        flash('Report successfully deleted!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting report: {str(e)}', 'report_error')
    
    # Redirect back to the appropriate list based on original status
    return redirect(url_for('reports.report_list', status=status))


@reports.route('/report/cancel/<int:report_id>', methods=['POST'])
@login_required
def cancel_report(report_id):
    report = Report.query.get_or_404(report_id)
    log_action('REPORT_CANCELLED', f'Cancelled report ID: {report_id} for vehicle: {report.vehicle.chassis_number if report.vehicle else "Unknown"}')
    report.status = ReportStatus.CANCELLED
    db.session.commit()
    flash('Report cancelled successfully!', 'success')
    return redirect(url_for('reports.report_list'))


@reports.route('/report/complete/<int:report_id>', methods=['POST', 'GET'])
@login_required
def complete_report(report_id):
    # Don't mark the report as completed, just show the complete report page
    return redirect(url_for('reports.show_complete_report', report_id=report_id))


@reports.route('/report/mark_complete/<int:report_id>', methods=['POST'])
@login_required
def mark_complete(report_id):
    # Mark the report as completed
    try:
        report = Report.query.get_or_404(report_id)
        log_action('REPORT_COMPLETED', f'Completed report ID: {report_id} for vehicle: {report.vehicle.chassis_number if report.vehicle else "Unknown"}')
        report.status = ReportStatus.COMPLETED
        db.session.commit()
        flash('Report marked as completed!', 'success')
    except Exception as e:

        flash('Error completing report', 'error')
    
    return redirect(url_for('reports.report_list'))


@reports.route('/report/complete_report/<int:report_id>', methods=['GET', 'POST'])
@login_required
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
from ..models import Report, ExpertiseType, ExpertiseReport, ExpertiseFeature
from ..database import db

@reports.route('/report/expertise_detail_ajax', methods=['GET'])
@login_required
def expertise_detail_ajax():
    # Force fresh data from database
    db.session.expire_all()
    
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
        'Road & Dyno Expertise':         'Road & Dyno Expertise',
    }
    template_map = {
        'ECU Expertise':                 'report_sections/expertises/beyin_expertise.html',
        'Paint Expertise':               'report_sections/expertises/boya_expertise_interactive.html',
        'Paint & Body Expertise':        'report_sections/expertises/boya_kaporta_expertise.html',
        'Exterior Expertise':            'report_sections/expertises/dis_expertise.html',
        'Dyno Expertise':                'report_sections/expertises/dyno_expertise_fixed.html',
        'Brake Expertise':               'report_sections/expertises/fren_expertise_last.html',
        'Interior & Exterior Expertise': 'report_sections/expertises/ic_dis_expertise_fixed.html',
        'Interior Expertise':            'report_sections/expertises/ic_expertise.html',
        'Body Expertise':                'report_sections/expertises/kaporta_expertise.html',
        'Mechanical Expertise':          'report_sections/expertises/mekanik_expertise.html',
        'Engine Expertise':              'report_sections/expertises/motor_expertise.html',
        'Suspension Expertise':          'report_sections/expertises/suspansiyon_expertise.html',
        'Lateral Drift Expertise':       'report_sections/expertises/yanal_expertise.html',
        'Road Expertise':                'report_sections/expertises/yol_expertise.html',
        'Road & Dyno Expertise':         'report_sections/expertises/yol_dyno_expertise_clean.html',
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
            db.session.flush()  # Use flush instead of commit to get the ID

        
        # Try to find existing expertise report for this report and expertise type

        er = ExpertiseReport.query.filter_by(
            report_id=report.id,
            expertise_type_id=et.id
        ).first()
        
        if er:
            pass
        else:
            pass
        
        if not er:
            er = ExpertiseReport(report_id=report.id, expertise_type_id=et.id)
            db.session.add(er)
            db.session.flush()  # Use flush instead of commit to get the ID

        
        # Double-check that the expertise report has the correct report_id
        if er.report_id != report.id:

            er.report_id = report.id
            db.session.add(er)
            db.session.flush()
            
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
                        db.session.flush()  # Use flush to ensure features are saved

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
                        db.session.flush()  # Use flush to ensure features are saved

            except Exception as e:

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
                db.session.flush()  # Use flush to ensure features are saved
                
        # Force load features relationship
        db.session.refresh(er)
        features_count = len(er.features)

        
        if features_count == 0:
            pass
        else:
            pass
        
        # Don't commit here - let the caller handle commits
        db.session.flush()
        
        # Final refresh to ensure all relationships are loaded
        db.session.refresh(er)
        # Force reload features from database
        er.features = ExpertiseFeature.query.filter_by(expertise_report_id=er.id).order_by(ExpertiseFeature.id).all()
        final_count = len(er.features)

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
    elif expertise_type == 'Road & Dyno Expertise':
        er1 = _ensure_er('Road Expertise')
        er2 = _ensure_er('Dyno Expertise')
    
    # Verify that the expertise reports are properly linked to the report
    if er1 and er1.report_id != report.id:

        er1.report_id = report.id
        db.session.add(er1)
        db.session.commit()
    
    if er2 and er2.report_id != report.id:

        er2.report_id = report.id
        db.session.add(er2)
        db.session.commit()
    
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
            pass
        return []
    
    def ensure_features_exist(er, expertise_name):
        """Ensure features exist for an expertise report, but don't recreate if they already exist"""
        if not er:
            return
            
        # Get all features for this expertise report
        existing_features = ExpertiseFeature.query.filter_by(expertise_report_id=er.id).order_by(ExpertiseFeature.id).all()
        
        if existing_features:

            er.features = existing_features
            return
        
        # Only create features if none exist
        parts = load_features_from_map(expertise_name)
        
        if parts:

            for part in parts:
                feature = ExpertiseFeature(
                    name=part['part_name'],
                    status=part['default_status'],
                    expertise_report_id=er.id
                )
                db.session.add(feature)
            db.session.flush()  # Use flush to ensure features are saved
        else:
            # Fallback to hardcoded features if map doesn't have this expertise type

            if "Paint" in expertise_name:
                features = [
                    "Left Front Fender", "Left Front Door", "Left Rear Fender",
                    "Front Bumper", "Hood", "Roof", "Trunk Lid", "Rear Bumper",
                    "Right Front Fender", "Right Front Door", "Right Rear Door",
                    "Right Rear Fender", "Left Rear Door"
                ]
                default_status = "Original"
            elif "Body" in expertise_name:
                features = [
                    "Left Front Chassis", "Left Inner Rocker Panel", "Left A-Pillar Inner",
                    "Left Upper Pillar", "Left Side Skirt", "Left Rear Chassis",
                    "Front Bumper", "Front Panel", "Front Windshield", "Roof",
                    "Rear Windshield", "Rear Panel", "Rear Wheel Well", "Rear Bumper",
                    "Right Front Chassis", "Right Inner Rocker Panel", "Right A-Pillar Inner",
                    "Right Upper Pillar", "Right Side Skirt", "Right Rear Chassis"
                ]
                default_status = "No Issue"
            elif "Exterior" in expertise_name:
                features = [
                    "Horn", "Headlights", "Headlight Wash", "Front/Rear Fog Lights",
                    "Turn Signals & Hazard Lights", "Wipers", "Mirrors", "Sunroof or Moonroof",
                    "Windows", "Door Handles", "Tail Lights", "License Plate Light",
                    "Trunk Interior", "Spare Tire"
                ]
                default_status = "No Issue"
            elif "Interior" in expertise_name:
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
                    expertise_report_id=er.id
                )
                db.session.add(feature)
            db.session.flush()  # Use flush to ensure features are saved
    
    # Ensure features exist for both expertise reports
    ensure_features_exist(er1, er1.expertise_type.name if er1 else None)
    ensure_features_exist(er2, er2.expertise_type.name if er2 else None)

    # Commit all changes and refresh to ensure features are loaded
    db.session.commit()
    
    # Ensure features are loaded fresh from database
    if er1:
        # Force reload features from database with explicit session refresh
        db.session.expire_all()  # Clear all cached objects
        er1 = ExpertiseReport.query.get(er1.id)  # Re-fetch from database
        er1.features = ExpertiseFeature.query.filter_by(expertise_report_id=er1.id).order_by(ExpertiseFeature.id).all()

    
    if er2:
        # Force reload features from database with explicit session refresh
        er2 = ExpertiseReport.query.get(er2.id)  # Re-fetch from database
        er2.features = ExpertiseFeature.query.filter_by(expertise_report_id=er2.id).order_by(ExpertiseFeature.id).all()

    
    # Final debug before rendering template - verify data from DB

    
    # Double-check by querying database directly with fresh session
    if er1:
        db.session.expire_all()  # Clear all cached objects again
        db_features = ExpertiseFeature.query.filter_by(expertise_report_id=er1.id).order_by(ExpertiseFeature.id).all()

        # Update er1.features with fresh data
        er1.features = db_features
    
    if er1 and er1.features:
        pass
    
    from flask import make_response
    response = make_response(render_template(
        template,
        report=report,
        expertise_report=er1,
        expertise_report2=er2,
        current_expertise_type=expertise_type
    ))
    # Prevent browser caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response




@reports.route('/report/expertise/<int:expertise_report_id>', methods=['GET', 'POST'])
@login_required
def expertise_detail(expertise_report_id):
    expertise_report = ExpertiseReport.query.get_or_404(expertise_report_id)
    expertise_report2_id = request.form.get('expertise_report2_id')
    expertise_report2 = (
        ExpertiseReport.query.get(expertise_report2_id)
        if expertise_report2_id else None
    )
    
    # Get the current expertise type from the form
    current_expertise_type = request.form.get('current_expertise_type')

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

                
                # Don't rely on the relationship - process features directly from form
                # Normal processing for all expertise types
                # No special processing needed for brake expertise anymore
                
                # Process features by their IDs from the form (bypass relationship issues)
                for form_key in request.form.keys():
                    if form_key.startswith('feature_'):
                        feature_id = int(form_key.replace('feature_', ''))
                        new_status = request.form.get(form_key)
                        
                        # Query the feature directly by ID
                        feature = ExpertiseFeature.query.get(feature_id)
                        if feature:
                            if new_status != feature.status:
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
                    
                    # Store original comment and create translation for PDF
                    rpt.comment = new_comment  # Always store original comment
                    
                    # Auto-translate for PDF generation if translation is available
                    if new_comment.strip() and TRANSLATION_AVAILABLE:
                        try:
                            # Try to detect if it's Arabic (contains Arabic characters)
                            import re
                            arabic_pattern = re.compile(r'[\u0600-\u06FF]')
                            has_arabic = bool(arabic_pattern.search(new_comment))
                            
                            if has_arabic:  # Arabic comment - translate to English for PDF
                                translated = ts.translate_text(new_comment, translator='bing', from_language='ar', to_language='en')
                                rpt.comment_arabic = new_comment  # Store original Arabic
                                # Don't change the main comment, keep it in Arabic
                            else:  # English comment - translate to Arabic for PDF
                                from ..services.uae_arabic_dictionary import get_uae_arabic_translation
                                translated = get_uae_arabic_translation(new_comment)
                                rpt.comment_arabic = translated  # Store translated Arabic
                        except Exception as e:
                            print(f"Translation error: {e}")
                            # If translation fails, just store the original comment
                    
                    db.session.merge(rpt)  # Explicitly mark as modified
                
                # Handle pass_fail field
                new_pass_fail = request.form.get('pass_fail') or None
                if new_pass_fail != rpt.pass_fail:
                    rpt.pass_fail = new_pass_fail
                    db.session.merge(rpt)  # Explicitly mark as modified


            db.session.commit()
            # Refresh the expertise reports to ensure changes are reflected
            for rpt in reports_to_update:
                db.session.refresh(rpt)
            
            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": True}), 200
            else:
                # Regular form submission - redirect back to the complete report page
                flash('Expertise updated successfully!', 'success')
                url = url_for('reports.show_complete_report', report_id=expertise_report.report_id)
                return redirect(url)

        except Exception as e:
            db.session.rollback()

            return jsonify({"success": False, "error": str(e)}), 500

    # GET
    return render_template(
        'report_sections/complete_report.html',
        expertise_report=expertise_report,
        expertise_report2=expertise_report2
    )


@reports.route('/reports/upload_detailed_images', methods=['POST'])
@login_required
def upload_detailed_images():
    try:
        report_id = request.form.get('report_id', type=int)
        if not report_id:
            return jsonify({'success': False, 'error': 'Report ID is required'}), 400
        
        report = Report.query.get_or_404(report_id)
        
        # Get uploaded files
        files = request.files.getlist('images')
        if not files:
            return jsonify({'success': False, 'error': 'No images provided'}), 400
        
        # Check current image count
        current_count = len(report.detailed_images) if report.detailed_images else 0
        if current_count + len(files) > 18:
            return jsonify({'success': False, 'error': f'Maximum 18 images allowed. You can upload {18 - current_count} more images.'}), 400
        
        uploaded_count = 0
        for i, file in enumerate(files):
            if file and file.filename:
                try:
                    image_data = file.read()
                    if len(image_data) > 0:
                        report_image = ReportImage(
                            report_id=report_id,
                            image_data=image_data,
                            filename=file.filename,
                            upload_order=current_count + i + 1
                        )
                        db.session.add(report_image)
                        uploaded_count += 1
                except Exception as e:
                    print(f"Error processing image {file.filename}: {str(e)}")
                    continue
        
        db.session.commit()
        
        # Get updated total count
        total_images = len(report.detailed_images)
        
        return jsonify({
            'success': True,
            'count': uploaded_count,
            'total_images': total_images
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Upload error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@reports.route('/reports/delete_detailed_image', methods=['POST'])
@login_required
def delete_detailed_image():
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        report_id = data.get('report_id')
        
        if not image_id or not report_id:
            return jsonify({'success': False, 'error': 'Missing image_id or report_id'}), 400
        
        # Verify the image belongs to the report
        image = ReportImage.query.filter_by(id=image_id, report_id=report_id).first()
        if not image:
            return jsonify({'success': False, 'error': 'Image not found'}), 404
        
        # Delete the image
        db.session.delete(image)
        db.session.commit()
        
        # Get remaining count
        remaining_count = ReportImage.query.filter_by(report_id=report_id).count()
        
        return jsonify({
            'success': True,
            'remaining_count': remaining_count
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete image error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# PDF routes moved to pdfs.py blueprint


@reports.route('/report/main_inspection_ajax', methods=['GET'])
@login_required
def main_inspection_ajax():
    report_id = request.args.get('report_id', type=int)
    report = Report.query.get_or_404(report_id)
    
    # Get or create main inspection
    main_inspection = MainInspection.query.filter_by(report_id=report_id).first()
    if not main_inspection:
        main_inspection = MainInspection(report_id=report_id)
        db.session.add(main_inspection)
        db.session.commit()
    
    # Convert to dict for template
    main_inspection_data = {}
    if main_inspection:
        for attr in dir(main_inspection):
            if not attr.startswith('_') and attr not in ['id', 'report_id', 'report']:
                main_inspection_data[attr] = getattr(main_inspection, attr)
    
    # Get saved language preference
    saved_language = getattr(main_inspection, 'comment_language', 'arabic') or 'arabic'
    
    return render_template(
        'report_sections/main_inspection.html',
        report=report,
        main_inspection=main_inspection_data,
        saved_language=saved_language
    )


@reports.route('/report/save_main_inspection/<int:report_id>', methods=['POST'])
@login_required
def save_main_inspection(report_id):
    try:
        report = Report.query.get_or_404(report_id)
        
        # Get or create main inspection
        main_inspection = MainInspection.query.filter_by(report_id=report_id).first()
        if not main_inspection:
            main_inspection = MainInspection(report_id=report_id)
            db.session.add(main_inspection)
        
        # Get language selection and save it
        comment_language = request.form.get('comment_language', 'arabic')
        main_inspection.comment_language = comment_language
        
        # Update all fields
        inspection_items = [
            'lights', 'body', 'chassis', 'paint', 'roof', 'bonnet_trunk',
            'fender', 'doors', 'bumper_kit', 'rims', 'engine', 'gear_box',
            'differential', 'four_w_drive', 'transmission_shaft', 'alignment',
            'tyres', 'brakes', 'exhaust'
        ]
        
        for item in inspection_items:
            # Update status
            status_field = f'{item}_status'
            status_value = request.form.get(status_field)
            setattr(main_inspection, status_field, status_value)
            
            # Update comment
            comment_field = f'{item}_comment'
            comment_value = request.form.get(comment_field, '').strip()
            old_comment = getattr(main_inspection, comment_field, '')
            
            # Only translate if comment actually changed
            if comment_value != old_comment:
                setattr(main_inspection, comment_field, comment_value)
                
                # Use new translation service with explicit language
                if comment_value:
                    try:
                        from ..services.uae_translation_service import UaeTranslationService
                        
                        # Store original comment
                        setattr(main_inspection, comment_field, comment_value)
                        
                        # Auto-translate for PDF generation if translation is available
                        if comment_value.strip() and TRANSLATION_AVAILABLE:
                            try:
                                # Try to detect if it's Arabic (contains Arabic characters)
                                import re
                                arabic_pattern = re.compile(r'[\u0600-\u06FF]')
                                has_arabic = bool(arabic_pattern.search(comment_value))
                                
                                if has_arabic:  # Arabic comment - use working translation service
                                    try:
                                        from ..services.uae_translation_service import UaeTranslationService
                                        translated_english = UaeTranslationService.translate_comment(comment_value, 'arabic')
                                        setattr(main_inspection, f'{comment_field}_arabic', translated_english)  # Store English translation in _arabic field
                                        print(f"Arabic->English: Used UaeTranslationService")
                                    except Exception as e:
                                        print(f"Arabic translation failed: {e}")
                                        setattr(main_inspection, f'{comment_field}_arabic', comment_value)  # Keep original as fallback
                                else:  # English comment - use working translation service
                                    try:
                                        from ..services.uae_translation_service import UaeTranslationService
                                        translated_arabic = UaeTranslationService.translate_comment(comment_value, 'english')
                                        setattr(main_inspection, f'{comment_field}_arabic', translated_arabic)
                                        print(f"English->Arabic: Used UaeTranslationService")
                                    except Exception as e:
                                        print(f"English translation failed: {e}")
                                        setattr(main_inspection, f'{comment_field}_arabic', comment_value)  # Keep original as fallback
                            except Exception as e:
                                print(f"Translation error: {e}")
                                # If translation fails, just store the original comment
                        
                        db.session.add(main_inspection)  # Explicitly mark as modified
                            
                    except Exception as e:
                        print(f"Translation error: {e}")
                elif not comment_value:
                    # Clear translations if comment is empty
                    setattr(main_inspection, f'{comment_field}_arabic', '')
        
        db.session.commit()
        print(f"Saved language: {comment_language} for report {report_id}")
        
        # Debug: Print what was actually saved
        for item in inspection_items:
            comment_field = f'{item}_comment'
            comment_value = getattr(main_inspection, comment_field, '')
            comment_arabic = getattr(main_inspection, f'{comment_field}_arabic', '')
            if comment_value or comment_arabic:
                print(f"{item}: main='{comment_value}', arabic='{comment_arabic}', lang={comment_language}")
        
        return jsonify({'success': True, 'language': comment_language})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving main inspection: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
import base64
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import datetime as dt
from sqlalchemy import or_

from ..database import db
from ..enums import FuelType, TransmissionType, Color, ReportStatus
from ..auth import login_required
from ..rbac import can_delete_reports
from ..services.log_service import log_action
from ..models import (
    Report, Customer, Package, Staff, Vehicle, Agent, VehicleOwner,
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
                    print(f"DEBUG: Created customer address: {address.street_address}")
                
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
                print(f"DEBUG: Created customer with address_id: {address_id}")

            # 3) REPORT
            # Handle image upload if has_image is 'yes'
            has_image = request.form.get('has_image') == 'yes'
            image_data = None
            
            if has_image:
                if 'vehicle_image' in request.files:
                    image_file = request.files['vehicle_image']
                    if image_file and image_file.filename:
                        # Read the image data
                        image_data = image_file.read()
                    # If no file uploaded but has_image is yes, just continue without image
                # If no file field, just continue without image
            
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

            # 4) Create Agent and VehicleOwner records if provided
            if form.agent_name.data.strip():
                agent_names = form.agent_name.data.strip().split(' ', 1)
                agent = Agent(
                    first_name=agent_names[0],
                    last_name=agent_names[1] if len(agent_names) > 1 else '',
                    report_id=new_report.id
                )
                db.session.add(agent)
                print(f"DEBUG: Created agent: {agent.first_name} {agent.last_name}")
            
            if form.owner_name.data.strip():
                owner_names = form.owner_name.data.strip().split(' ', 1)
                
                # Create owner address if provided
                address_id = None
                owner_address = form.owner_address.data.strip()
                if owner_address:
                    from ..models.all_models import Address
                    address = Address(
                        street_address=owner_address,
                        city="Unknown",
                        state=None,
                        postal_code=None
                    )
                    db.session.add(address)
                    db.session.flush()
                    address_id = address.id
                    print(f"DEBUG: Created owner address: {owner_address}")
                
                owner = VehicleOwner(
                    first_name=owner_names[0],
                    last_name=owner_names[1] if len(owner_names) > 1 else '',
                    tc_tax_number=form.owner_tax_no.data.strip() or None,
                    phone_number=form.owner_phone.data.strip() or f"owner-{new_report.id}",
                    address_id=address_id,
                    report_id=new_report.id
                )
                db.session.add(owner)
                print(f"DEBUG: Created vehicle owner: {owner.first_name} {owner.last_name} with address_id: {address_id}, phone: {owner.phone_number}")
            print(f"DEBUG: Owner will be searchable with phone pattern: owner-{new_report.id}")

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
            
            # Save form data to session for later editing (backup)
            from flask import session
            session[f'report_{new_report.id}_data'] = {
                'owner_name': form.owner_name.data,
                'owner_phone': form.owner_phone.data or f"owner-{new_report.id}",
                'owner_tax_no': form.owner_tax_no.data,
                'owner_address': form.owner_address.data,
                'agent_name': form.agent_name.data,
                'customer_address': form.customer_address.data
            }
            print(f"DEBUG: Saved session data for report {new_report.id}")
            owner_phone = form.owner_phone.data or f"owner-{new_report.id}"
            print(f"DEBUG: Owner data in session: name='{form.owner_name.data}', phone='{owner_phone}', tax='{form.owner_tax_no.data}', address='{form.owner_address.data}'")
            
            flash('Report created successfully!', 'success')
            return redirect(url_for('reports.report_list'))

        except IntegrityError as e:
            db.session.rollback()
            error_message = 'Data conflict—duplicate plate or chassis. Please correct.'
            print("IntegrityError in add_report:", e, flush=True)
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
            error_message = 'Unexpected error—check your data and try again.'
            print("Exception in add_report:", e, flush=True)
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
    
    print(f"DEBUG: Request method: {request.method}")
    if request.method == 'POST':
        print(f"DEBUG: Form data received: {dict(request.form)}")
        print(f"DEBUG: Form validation result: {form.validate()}")
        if form.errors:
            print(f"DEBUG: Form errors: {form.errors}")
    
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
        print(f"DEBUG: Set created_at to: {form.created_at.data}")
        
        # Load agent information from the database
        agent = Agent.query.filter_by(report_id=report_id).first()
        print(f"DEBUG: Looking for agent with report_id={report_id}, found: {agent}")
        if agent:
            form.agent_name.data = f"{agent.first_name} {agent.last_name}"
            print(f"DEBUG: Agent name set to: {form.agent_name.data}")
        else:
            form.agent_name.data = ""
            print("DEBUG: No agent found, setting empty")
        
        # Load owner information - query directly by report_id
        print(f"DEBUG: Looking for vehicle owner with report_id={report_id}")
        all_owners = VehicleOwner.query.all()
        print(f"DEBUG: All owners in database: {[(o.id, o.first_name, o.last_name, o.report_id) for o in all_owners]}")
        
        vehicle_owner = VehicleOwner.query.filter_by(report_id=report_id).first()
        print(f"DEBUG: Found vehicle_owner: {vehicle_owner}")
        
        if vehicle_owner:
            print(f"DEBUG: Owner details - name: {vehicle_owner.first_name} {vehicle_owner.last_name}, phone: {vehicle_owner.phone_number}, tax: {vehicle_owner.tc_tax_number}")
            form.owner_name.data = vehicle_owner.full_name
            form.owner_phone.data = vehicle_owner.phone_number
            form.owner_tax_no.data = vehicle_owner.tc_tax_number
            if vehicle_owner.address:
                form.owner_address.data = vehicle_owner.address.street_address
                print(f"DEBUG: Owner address: {vehicle_owner.address.street_address}")
            else:
                form.owner_address.data = ''
                print(f"DEBUG: No address for owner")
            print(f"DEBUG: Owner loaded successfully: {vehicle_owner.full_name}")
        else:
            # Try to get from session as fallback
            session_data = session.get(f'report_{report_id}_data', {})
            print(f"DEBUG: Session data for report {report_id}: {session_data}")
            form.owner_name.data = session_data.get('owner_name', '')
            form.owner_phone.data = session_data.get('owner_phone', '')
            form.owner_tax_no.data = session_data.get('owner_tax_no', '')
            form.owner_address.data = session_data.get('owner_address', '')
            print(f"DEBUG: No owner found in DB for report {report_id}, loaded from session: name='{form.owner_name.data}', phone='{form.owner_phone.data}'")
        
        # Load customer address
        if report.customer.address:
            form.customer_address.data = report.customer.address.street_address or ''
        else:
            session_data = session.get(f'report_{report_id}_data', {})
            form.customer_address.data = session_data.get('customer_address', '')
        
        print(f"DEBUG: FINAL Form data populated - owner_name: '{form.owner_name.data}', owner_phone: '{form.owner_phone.data}', owner_tax_no: '{form.owner_tax_no.data}', owner_address: '{form.owner_address.data}', agent_name: '{form.agent_name.data}', customer_address: '{form.customer_address.data}'")
        print(f"DEBUG: Session data keys: {list(session.keys())}")
        print(f"DEBUG: Report created at: {report.created_at}")
        
        # If no session data, try to get from customer's address relationship
        if not form.customer_address.data and report.customer.address:
            address = report.customer.address
            form.customer_address.data = address.street_address or ''
            print(f"DEBUG: Customer address from DB: {form.customer_address.data}")
        elif not form.customer_address.data:
            print("DEBUG: No customer address found in session or DB")
    
    if form.validate_on_submit():
        try:
            print(f"DEBUG: Starting edit_report save for report_id={report_id}")
            
            # Update vehicle data
            vehicle = report.vehicle
            print(f"DEBUG: Updating vehicle - old plate: {vehicle.plate}, new plate: {form.vehicle_plate.data.strip()}")
            vehicle.plate = form.vehicle_plate.data.strip()
            vehicle.engine_number = form.engine_number.data.strip()
            vehicle.brand = form.brand.data.strip()
            vehicle.model = form.model.data.strip()
            vehicle.chassis_number = form.chassis_number.data.strip()
            vehicle.color = map_to_enum(form.color.data, Color)
            vehicle.model_year = form.model_year.data
            vehicle.transmission_type = map_to_enum(form.gear_type.data, TransmissionType)
            vehicle.fuel_type = map_to_enum(form.fuel_type.data, FuelType)
            vehicle.mileage = form.vehicle_km.data
            db.session.add(vehicle)  # Explicitly mark for update
            print(f"DEBUG: Vehicle data updated and marked for save")
            
            # Update customer data
            customer = report.customer
            names = form.customer_name.data.strip().split(' ', 1)
            print(f"DEBUG: Updating customer - old name: {customer.first_name} {customer.last_name}, new name: {names[0]} {names[1] if len(names) > 1 else ''}")
            customer.first_name = names[0]
            customer.last_name = names[1] if len(names) > 1 else ''
            customer.phone_number = form.customer_phone.data.strip()
            customer.email = form.customer_email.data.strip() or None
            customer.tc_tax_number = form.customer_tax_no.data.strip() or None
            db.session.add(customer)  # Explicitly mark for update
            print(f"DEBUG: Customer data updated and marked for save")
            
            # Update customer address
            customer_address = form.customer_address.data.strip()
            if customer_address:
                from ..models.all_models import Address
                if customer.address:
                    # Update existing address
                    print(f"DEBUG: Updating existing address from '{customer.address.street_address}' to '{customer_address}'")
                    customer.address.street_address = customer_address
                    db.session.add(customer.address)  # Explicitly mark for update
                    print(f"DEBUG: Updated customer address: {customer_address}")
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
                    print(f"DEBUG: Created new customer address: {customer_address}")
            
            # Update report data
            print(f"DEBUG: Updating report - old package_id: {report.package_id}, new package_id: {form.package_id.data}")
            report.package_id = form.package_id.data
            report.operation = form.operation.data or None
            report.created_by = form.created_by.data
            report.registration_document_seen = form.registration_document_seen.data
            report.inspection_date = form.inspection_date.data
            db.session.add(report)  # Explicitly mark for update
            print(f"DEBUG: Report data updated and marked for save")
            
            # Update or create agent if agent name is provided
            agent_name = form.agent_name.data.strip()
            print(f"DEBUG: Processing agent name: '{agent_name}'")
            if agent_name:
                # Try to find existing agent
                agent = Agent.query.filter_by(report_id=report_id).first()
                agent_names = agent_name.split(' ', 1)
                agent_first_name = agent_names[0]
                agent_last_name = agent_names[1] if len(agent_names) > 1 else ''
                
                if not agent:
                    # Create new agent
                    agent = Agent(
                        first_name=agent_first_name,
                        last_name=agent_last_name,
                        report_id=report_id
                    )
                    db.session.add(agent)
                    print(f"DEBUG: Created new agent during edit: {agent_first_name} {agent_last_name}")
                else:
                    # Update existing agent
                    print(f"DEBUG: Updating agent from '{agent.first_name} {agent.last_name}' to '{agent_first_name} {agent_last_name}'")
                    agent.first_name = agent_first_name
                    agent.last_name = agent_last_name
                    print(f"DEBUG: Updated existing agent: {agent_first_name} {agent_last_name}")
                    db.session.add(agent)  # Ensure it's marked for update
            else:
                # Delete existing agent if name is cleared
                existing_agent = Agent.query.filter_by(report_id=report_id).first()
                if existing_agent:
                    db.session.delete(existing_agent)
                    print(f"DEBUG: Deleted existing agent because name was cleared")
            
            # Update or create vehicle owner if owner name is provided
            owner_name = form.owner_name.data.strip()
            existing_owner = VehicleOwner.query.filter_by(report_id=report_id).first()
            
            if owner_name:
                print(f"DEBUG: Processing owner name: {owner_name}")
                owner_names = owner_name.split(' ', 1)
                
                if existing_owner:
                    # Update existing owner
                    existing_owner.first_name = owner_names[0]
                    existing_owner.last_name = owner_names[1] if len(owner_names) > 1 else ''
                    existing_owner.phone_number = form.owner_phone.data.strip() or existing_owner.phone_number
                    existing_owner.tc_tax_number = form.owner_tax_no.data.strip() or None
                    
                    # Update owner address
                    owner_address = form.owner_address.data.strip()
                    if owner_address:
                        from ..models.all_models import Address
                        if existing_owner.address:
                            existing_owner.address.street_address = owner_address
                            db.session.add(existing_owner.address)
                        else:
                            address = Address(
                                street_address=owner_address,
                                city="Unknown",
                                state=None,
                                postal_code=None
                            )
                            db.session.add(address)
                            db.session.flush()
                            existing_owner.address_id = address.id
                    
                    db.session.add(existing_owner)
                    print(f"DEBUG: Updated existing owner: {existing_owner.first_name} {existing_owner.last_name}")
                else:
                    # Create new owner
                    owner_phone = form.owner_phone.data.strip() or f"owner-{report_id}"
                    
                    # Create owner address if provided
                    address_id = None
                    owner_address = form.owner_address.data.strip()
                    if owner_address:
                        from ..models.all_models import Address
                        address = Address(
                            street_address=owner_address,
                            city="Unknown",
                            state=None,
                            postal_code=None
                        )
                        db.session.add(address)
                        db.session.flush()
                        address_id = address.id
                    
                    new_owner = VehicleOwner(
                        first_name=owner_names[0],
                        last_name=owner_names[1] if len(owner_names) > 1 else '',
                        tc_tax_number=form.owner_tax_no.data.strip() or None,
                        phone_number=owner_phone,
                        address_id=address_id,
                        report_id=report_id
                    )
                    db.session.add(new_owner)
                    print(f"DEBUG: Created new owner during edit: {new_owner.first_name} {new_owner.last_name}")
            else:
                # If owner name is cleared, delete existing owner
                if existing_owner:
                    if existing_owner.address:
                        db.session.delete(existing_owner.address)
                    db.session.delete(existing_owner)
                    print(f"DEBUG: Deleted existing owner because name was cleared")
            
            # Save form data to session for future editing
            session[f'report_{report_id}_data'] = {
                'owner_name': form.owner_name.data,
                'owner_phone': form.owner_phone.data,
                'owner_tax_no': form.owner_tax_no.data,
                'owner_address': form.owner_address.data,
                'agent_name': form.agent_name.data,
                'customer_address': form.customer_address.data
            }
            print(f"DEBUG: Updated session data for report {report_id}")
            print(f"DEBUG: Updated owner data in session: name='{form.owner_name.data}', phone='{form.owner_phone.data}', tax='{form.owner_tax_no.data}', address='{form.owner_address.data}'")
            
            # Handle image upload if has_image is 'yes'
            has_image = request.form.get('has_image') == 'yes'
            if has_image:
                if 'vehicle_image' in request.files:
                    image_file = request.files['vehicle_image']
                    if image_file and image_file.filename:
                        # Read the image data
                        report.image_data = image_file.read()
                        report.has_image = True
            else:
                # If has_image is 'no', set image fields to False/None
                report.has_image = False
                report.image_data = None
            
            # Save changes
            print(f"DEBUG: About to commit all changes to database")
            db.session.commit()
            print(f"DEBUG: Successfully committed changes to database")
            
            # Verify all data was saved by re-querying
            updated_report = Report.query.get(report_id)
            updated_vehicle = updated_report.vehicle
            updated_customer = updated_report.customer
            updated_agent = Agent.query.filter_by(report_id=report_id).first()
            
            print(f"DEBUG: Verification - Vehicle plate: {updated_vehicle.plate}")
            print(f"DEBUG: Verification - Customer name: {updated_customer.first_name} {updated_customer.last_name}")
            print(f"DEBUG: Verification - Customer address: {updated_customer.address.street_address if updated_customer.address else 'None'}")
            print(f"DEBUG: Verification - Agent: {updated_agent.first_name + ' ' + updated_agent.last_name if updated_agent else 'None'}")
            print(f"DEBUG: Verification - Report package_id: {updated_report.package_id}")
            
            # Verify owner data
            updated_owner = VehicleOwner.query.filter_by(report_id=report_id).first()
            if updated_owner:
                print(f"DEBUG: Verification - Owner: {updated_owner.first_name} {updated_owner.last_name}, phone: {updated_owner.phone_number}, tax: {updated_owner.tc_tax_number}")
                print(f"DEBUG: Verification - Owner address: {updated_owner.address.street_address if updated_owner.address else 'None'}")
            else:
                print(f"DEBUG: Verification - No owner found for report {report_id}")
            
            flash('Report updated successfully!', 'report_success')
            
            log_action('REPORT_UPDATED', f'Updated report ID: {report_id} for vehicle: {updated_vehicle.chassis_number}')
            
            # Redirect back to reports list
            return redirect(url_for('reports.report_list'))
            
        except IntegrityError as e:
            db.session.rollback()
            flash('Data conflict—duplicate plate or chassis. Please correct.', 'report_error')
            print(f"IntegrityError in edit_report: {e}", flush=True)
        except Exception as e:
            db.session.rollback()
            flash('Unexpected error—check your data and try again.', 'report_error')
            print(f"Exception in edit_report: {e}", flush=True)
    else:
        if request.method == 'POST':
            print(f"DEBUG: Form validation failed on POST request")
            print(f"DEBUG: Form errors: {form.errors}")
            # Fix missing created_at field
            if 'created_at' in form.errors:
                form.created_at.data = report.created_at
                print(f"DEBUG: Fixed created_at field with: {form.created_at.data}")
                # Try validation again
                if form.validate():
                    print(f"DEBUG: Form validation passed after fixing created_at")
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
        # Delete expertise features
        for er in report.expertise_reports:
            for feature in er.features:
                db.session.delete(feature)
        
        # Delete expertise reports
        for er in report.expertise_reports:
            db.session.delete(er)
        
        # Delete agents
        agents = Agent.query.filter_by(report_id=report_id).all()
        for agent in agents:
            db.session.delete(agent)
        
        # Delete vehicle owners linked to this report
        owners = VehicleOwner.query.filter_by(report_id=report_id).all()
        for owner in owners:
            if owner.address:
                db.session.delete(owner.address)
            db.session.delete(owner)
        
        # Delete the report
        log_action('REPORT_DELETED', f'Deleted report ID: {report_id} for vehicle: {report.vehicle.chassis_number if report.vehicle else "Unknown"}')
        db.session.delete(report)
        db.session.commit()
        flash('Report successfully deleted!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting report: {str(e)}', 'error')
        print(f"Error deleting report: {e}")
    
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
from ..models import Report, ExpertiseType, ExpertiseReport, ExpertiseFeature
from ..database import db

@reports.route('/report/expertise_detail_ajax', methods=['GET'])
def expertise_detail_ajax():
    # Clear all database session cache to ensure fresh data
    db.session.expire_all()
    db.session.close()
    db.session.remove()
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
            print(f"Created expertise type: {db_label}")
        
        # Try to find existing expertise report for this report and expertise type
        print(f"DEBUG: Looking for existing ExpertiseReport with report_id={report.id}, expertise_type_id={et.id}")
        er = ExpertiseReport.query.filter_by(
            report_id=report.id,
            expertise_type_id=et.id
        ).first()
        
        if er:
            print(f"DEBUG: Found existing ExpertiseReport {er.id} for {db_label}")
        else:
            print(f"DEBUG: No existing ExpertiseReport found for {db_label}, will create new one")
        
        if not er:
            er = ExpertiseReport(report_id=report.id, expertise_type_id=et.id)
            db.session.add(er)
            db.session.flush()  # Use flush instead of commit to get the ID
            print(f"DEBUG: Created new ExpertiseReport {er.id} for {db_label} with report_id={report.id}")
        
        # Double-check that the expertise report has the correct report_id
        if er.report_id != report.id:
            print(f"ERROR: ExpertiseReport {er.id} has wrong report_id: {er.report_id} (should be {report.id})")
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
                        db.session.flush()  # Use flush to ensure features are saved
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
                db.session.flush()  # Use flush to ensure features are saved
                
        # Force load features relationship
        db.session.refresh(er)
        features_count = len(er.features)
        print(f"DEBUG: ExpertiseReport {er.id} has {features_count} features after refresh")
        
        if features_count == 0:
            print(f"DEBUG: ExpertiseReport {er.id} has no features, will be populated later")
        else:
            print(f"DEBUG: ExpertiseReport {er.id} already has {features_count} features")
        
        # Don't commit here - let the caller handle commits
        db.session.flush()
        
        # Final refresh to ensure all relationships are loaded
        db.session.refresh(er)
        # Force reload features from database
        er.features = ExpertiseFeature.query.filter_by(expertise_report_id=er.id).order_by(ExpertiseFeature.id).all()
        final_count = len(er.features)
        print(f"DEBUG: After final refresh, ExpertiseReport {er.id} has {final_count} features")
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
        print(f"ERROR: er1.report_id ({er1.report_id}) != report.id ({report.id})")
        er1.report_id = report.id
        db.session.add(er1)
        db.session.commit()
    
    if er2 and er2.report_id != report.id:
        print(f"ERROR: er2.report_id ({er2.report_id}) != report.id ({report.id})")
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
            print(f"Error loading expertise map: {e}")
        return []
    
    def ensure_features_exist(er, expertise_name):
        """Ensure features exist for an expertise report, but don't recreate if they already exist"""
        if not er:
            return
            
        # Get all features for this expertise report
        existing_features = ExpertiseFeature.query.filter_by(expertise_report_id=er.id).order_by(ExpertiseFeature.id).all()
        
        if existing_features:
            print(f"DEBUG: Found {len(existing_features)} existing features for {expertise_name}, not recreating")
            er.features = existing_features
            return
        
        # Only create features if none exist
        parts = load_features_from_map(expertise_name)
        
        if parts:
            print(f"Adding {len(parts)} features from map for {expertise_name}")
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
            print(f"No features found in map for {expertise_name}, using fallback")
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
        print(f"DEBUG: er1 (report_id={er1.report_id}) has {len(er1.features)} features loaded")
        for feature in er1.features:
            print(f"DEBUG: Feature {feature.id}: {feature.name} = '{feature.status}' (type: {type(feature.status)})")
            print(f"DEBUG: Feature {feature.id} status repr: {repr(feature.status)}")
    
    if er2:
        # Force reload features from database with explicit session refresh
        er2 = ExpertiseReport.query.get(er2.id)  # Re-fetch from database
        er2.features = ExpertiseFeature.query.filter_by(expertise_report_id=er2.id).order_by(ExpertiseFeature.id).all()
        print(f"DEBUG: er2 (report_id={er2.report_id}) has {len(er2.features)} features loaded")
        for feature in er2.features:
            print(f"DEBUG: Feature {feature.id}: {feature.name} = '{feature.status}' (type: {type(feature.status)})")
            print(f"DEBUG: Feature {feature.id} status repr: {repr(feature.status)}")
    
    # Final debug before rendering template - verify data from DB
    print(f"DEBUG: About to render template {template}")
    print(f"DEBUG: expertise_report has {len(er1.features) if er1 else 0} features")
    
    # Double-check by querying database directly with fresh session
    if er1:
        db.session.expire_all()  # Clear all cached objects again
        db_features = ExpertiseFeature.query.filter_by(expertise_report_id=er1.id).order_by(ExpertiseFeature.id).all()
        print(f"DEBUG: Direct DB query shows {len(db_features)} features for expertise_report {er1.id}")
        for db_feature in db_features:
            print(f"DEBUG: DB Feature {db_feature.id}: {db_feature.name} = '{db_feature.status}'")
        # Update er1.features with fresh data
        er1.features = db_features
    
    if er1 and er1.features:
        print(f"DEBUG: First feature for template: {er1.features[0].name} = '{er1.features[0].status}'")
    
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

            print(f"FORM SUBMISSION RECEIVED for expertise_report_id={expertise_report_id}")
            print(f"Form data keys: {list(request.form.keys())}")
            print(f"Form data values: {list(request.form.values())}")
            
            # Debug the reports being updated
            print(f"Reports to update: {[r.id for r in reports_to_update]}")
            
            for rpt in reports_to_update:
                print(f"Processing report: {rpt.id} with {len(rpt.features)} features")
                
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
                            print(f"Feature {feature.id} ({feature.name}): current={feature.status}, new={new_status}")
                            
                            if new_status != feature.status:
                                print(f"UPDATING feature {feature.id} from {feature.status} to {new_status}")
                                feature.status = new_status
                                feature.image_path = (
                                    f'assets/car_parts/'
                                    f'{status_dir.get(new_status,"default")}/'
                                    f'{feature.name}.png'
                                )
                                db.session.add(feature)
                            else:
                                print(f"Feature {feature.id} status unchanged: {feature.status}")
                        else:
                            print(f"WARNING: Could not find feature with ID {feature_id}")

                new_comment = request.form.get('technician_comment') or ''
                if new_comment != rpt.comment:
                    rpt.comment = new_comment
                    db.session.merge(rpt)  # Explicitly mark as modified
                    print(f"Updated comment to: {new_comment}")

            db.session.commit()
            print("SUCCESSFULLY SAVED ALL CHANGES")
            
            # Refresh the expertise reports to ensure changes are reflected
            for rpt in reports_to_update:
                db.session.refresh(rpt)
                print(f"DEBUG: After save, report {rpt.id} has {len(rpt.features)} features")
                for feature in rpt.features:
                    print(f"DEBUG: Feature {feature.id}: {feature.name} = {feature.status}")
            
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
            print(f"ERROR updating expertise: {e}", flush=True)
            return jsonify({"success": False, "error": str(e)}), 500

    # GET
    return render_template(
        'report_sections/complete_report.html',
        expertise_report=expertise_report,
        expertise_report2=expertise_report2
    )
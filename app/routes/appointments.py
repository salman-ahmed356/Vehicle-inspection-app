from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..database import db
from ..models import Appointment, Customer
from datetime import datetime, date
from ..forms import AppointmentForm
from ..auth import login_required
from ..services.log_service import log_action

appointments = Blueprint('appointments', __name__)


@appointments.route('/appointments')
@login_required
def appointment_list():
    page = request.args.get('page', 1, type=int)  # Get the current page, default is 1
    per_page = request.args.get('per_page', 10, type=int)  # per_page, default is 10
    
    # Filter out past appointments
    today = date.today()
    paginated_appointments = Appointment.query.filter(Appointment.date >= today).order_by(Appointment.date, Appointment.time).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('appointment/appointment_list.html', appointments=paginated_appointments.items,
                           pagination=paginated_appointments)


@appointments.route('/appointment/add', methods=['GET', 'POST'])
@login_required
def add_appointment():
    form = AppointmentForm()
    if request.method == 'POST' and form.validate_on_submit():
        customer_name = form.customer_name.data
        name_parts = customer_name.split(' ', 1)
        
        # Ensure that we have at least a first name
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''  # Default to empty string if no last name

        phone_number = form.phone_number.data
        date_obj = form.date.data
        time_obj = form.time.data
        brand = form.brand.data
        model = form.model.data

        # Find customer by first name, last name, and phone number
        customer = Customer.query.filter_by(first_name=first_name, last_name=last_name, phone_number=phone_number).first()
        
        # If customer not found, create a new customer
        if not customer:
            customer = Customer(first_name=first_name, last_name=last_name, phone_number=phone_number)
            db.session.add(customer)
            db.session.commit()

        # Create a new appointment
        new_appointment = Appointment(
            customer_id=customer.id,
            date=date_obj,
            time=time_obj,
            brand=brand,
            model=model
        )
        db.session.add(new_appointment)
        db.session.commit()
        log_action('APPOINTMENT_CREATED', f'Created appointment for {customer.full_name} on {date_obj} at {time_obj} ({brand} {model})')
        flash('New appointment successfully created!', 'success')
        return redirect(url_for('appointments.appointment_list'))
    elif request.method == 'POST':
        flash('Appointment creation failed. Please check your information.', 'error')
        print("Form failed validation:", form.errors)

    # Initialize form with default values
    if not form.date.data:
        form.date.data = datetime.now().date()
    if not form.time.data:
        form.time.data = datetime.now().time()

    customers = Customer.query.all()
    # For GET requests, render the full page, not just the modal
    return render_template('appointment/add_appointment_page.html', form=form, customers=customers)


@appointments.route('/appointment/update/<int:appointment_id>', methods=['GET', 'POST'])
def update_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    form = AppointmentForm(obj=appointment)  # Populate the form with existing data

    if form.validate_on_submit():  # This checks if the form is submitted and passes validation
        # Split the customer name into first and last names
        customer_name = form.customer_name.data
        name_parts = customer_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''  # Default to empty string if no last name

        # Update the customer details
        appointment.customer.first_name = first_name
        appointment.customer.last_name = last_name
        appointment.customer.phone_number = form.phone_number.data
        appointment.date = form.date.data
        appointment.time = form.time.data
        appointment.brand = form.brand.data
        appointment.model = form.model.data
        appointment.reminder_sent = form.reminder_sent.data

        db.session.commit()
        log_action('APPOINTMENT_UPDATED', f'Updated appointment for {appointment.customer.full_name} on {appointment.date}')
        flash('Randevu başarıyla güncellendi!')
        return redirect(url_for('appointments.appointment_list'))

    return render_template('appointment/update_appointment.html', form=form, appointment=appointment)


@appointments.route('/appointment/cancel/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Delete the appointment
    log_action('APPOINTMENT_CANCELLED', f'Cancelled appointment for {appointment.customer.full_name} on {appointment.date}')
    db.session.delete(appointment)
    db.session.commit()
    
    flash('Appointment successfully cancelled!', 'success')
    
    # Check if the request came from the dashboard
    from_dashboard = request.form.get('from_dashboard') == 'true'
    if from_dashboard:
        return redirect('/dashboard')
    else:
        return redirect(url_for('appointments.appointment_list'))


@appointments.route('/appointment/create-report/<int:appointment_id>')
def create_report_from_appointment(appointment_id):
    # Get the appointment
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Store appointment data in session to pre-fill the report form
    from flask import session
    session['appointment_data'] = {
        'customer_name': appointment.customer.full_name,
        'customer_phone': appointment.customer.phone_number,
        'customer_email': appointment.customer.email,
        'customer_tax_no': appointment.customer.tc_tax_number,
        'vehicle_brand': appointment.brand,
        'vehicle_model': appointment.model,
        'appointment_id': appointment_id  # Store the appointment ID to delete it later
    }
    
    # Redirect to the report creation page
    return redirect(url_for('reports.add_report'))


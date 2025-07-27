# app/routes/companies.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.database import db
from ..forms import CompanyForm, StaffForm
from ..services.company_service import (
    update_company_service,
    delete_company as delete_cmp
)
from ..models import Company, Address, Branch, Staff
import logging
from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash
from ..auth import login_required
from ..rbac import can_access_company_settings
from ..services.log_service import log_action

logger = logging.getLogger(__name__)

companies = Blueprint('companies', __name__)


@companies.route('/company')
@login_required
def company_detail():
    if not can_access_company_settings():
        flash('You do not have permission to access company settings.', 'error')
        return redirect(url_for('main.index'))
    import logging
    logger = logging.getLogger(__name__)
    
    active_tab = request.args.get('active_tab', 'company')
    
    # Try to get company, handle missing column gracefully
    try:
        company = Company.query.order_by(Company.id).first()
    except OperationalError as e:
        if 'no such column: company.my_business_address_link' in str(e):
            # Create the missing column
            try:
                db.engine.execute('ALTER TABLE company ADD COLUMN my_business_address_link TEXT')
                db.session.commit()
                logger.info("Added my_business_address_link column to company table")
                # Try again after adding the column
                company = Company.query.order_by(Company.id).first()
            except Exception as e2:
                logger.error(f"Failed to add column: {e2}")
                company = None
        else:
            logger.error(f"Database error: {e}")
            company = None
    
    # Log company details for debugging
    if company:
        logger.info(f"Found company: ID={company.id}, Name={company.name}")
    else:
        logger.info("No company found in database")
    
    # Always create a form, with or without company data
    form = CompanyForm(obj=company) if company else CompanyForm()
    
    # If we have a company, populate all fields
    if company:
        # Populate company fields
        form.name.data = company.name
        form.phone.data = company.phone
        form.fax.data = company.fax
        form.email.data = company.email
        form.website.data = company.website
        # Removed my_business_address_link temporarily
        
        # Populate address fields if available
        if company.address:
            form.street_address.data = company.address.street_address
            form.city.data = company.address.city
            form.state.data = company.address.state
            form.postal_code.data = company.address.postal_code
            
        logger.info(f"Populated form with company data: {company.name}, {company.phone}, {company.email}")
    
    first_staff = None
    staff_form = None
    
    # Handle staff form creation
    if company and company.branches:
        branch = company.branches[0]
        logger.info(f"Found branch: ID={branch.id}, Name={branch.name}")
        
        if branch.staff_members:
            first_staff = branch.staff_members[0]
            logger.info(f"Found staff: ID={first_staff.id}, Name={first_staff.first_name}")
            staff_form = StaffForm(obj=first_staff)
        else:
            logger.info("No staff members found for branch")
            staff_form = StaffForm()
    else:
        # Create an empty staff form even if no company exists yet
        staff_form = StaffForm()

    return render_template(
        'settings/settings.html',
        company=company,
        form=form,
        first_staff=first_staff,
        staff_form=staff_form,
        active_tab=active_tab
    )


@companies.route('/company/update', methods=['POST'])
@login_required
def update_company():
    if not can_access_company_settings():
        flash('You do not have permission to update company settings.', 'error')
        return redirect(url_for('main.index'))
    import logging
    logger = logging.getLogger(__name__)
    
    # Try to get company, handle missing column gracefully
    try:
        company = Company.query.order_by(Company.id).first()
    except OperationalError as e:
        if 'no such column: company.my_business_address_link' in str(e):
            # Create the missing column
            try:
                db.engine.execute('ALTER TABLE company ADD COLUMN my_business_address_link TEXT')
                db.session.commit()
                logger.info("Added my_business_address_link column to company table")
                # Try again after adding the column
                company = Company.query.order_by(Company.id).first()
            except Exception as e2:
                logger.error(f"Failed to add column: {e2}")
                company = None
        else:
            logger.error(f"Database error: {e}")
            company = None
    form = CompanyForm(request.form)

    # Process form data regardless of validation
    data = {
        'name': form.name.data or 'Company Name',
        'phone': form.phone.data,
        'fax': form.fax.data,
        'email': form.email.data,
        'website': form.website.data,
        'street_address': form.street_address.data,
        'city': form.city.data or 'City',  # City is required but provide default
        'state': form.state.data,
        'postal_code': form.postal_code.data
        # Removed my_business_address_link temporarily
    }
    
    # Log the form data for debugging
    logger.info(f"Form data: name={form.name.data}, phone={form.phone.data}, email={form.email.data}")
    logger.info(f"Address data: street={form.street_address.data}, city={form.city.data}, state={form.state.data}, postal_code={form.postal_code.data}")

    try:
        if company:
            # update existing Company + Address
            logger.info(f"Updating existing company: {company.id}")
            logger.info(f"Company has address: {company.address is not None}")
            
            # If company doesn't have an address, create one
            if not company.address:
                logger.info("Creating new address for existing company")
                addr = Address(
                    street_address=data['street_address'],
                    city=data['city'],
                    state=data['state'],
                    postal_code=data['postal_code']
                )
                db.session.add(addr)
                db.session.flush()
                company.address_id = addr.id
                logger.info(f"Created address with ID: {addr.id}")
            else:
                logger.info(f"Current address: {company.address.street_address}, {company.address.city}, {company.address.state}, {company.address.postal_code}")
                
            update_company_service(company, data)
            log_action('COMPANY_UPDATED', f'Updated company settings: {company.name}')
            flash('Company settings updated!', 'success')
        else:
            # create Address
            logger.info("Creating new company")
            addr = Address(
                street_address=data['street_address'],
                city=data['city'],
                state=data['state'],
                postal_code=data['postal_code']
            )
            db.session.add(addr)
            db.session.flush()
            logger.info(f"Created address with ID: {addr.id}")

            # create Company without my_business_address_link for now
            company = Company(
                name=data['name'],
                phone=data['phone'],
                fax=data['fax'],
                email=data['email'],
                website=data['website'],
                address_id=addr.id
            )
            db.session.add(company)
            db.session.flush()
            logger.info(f"Created company with ID: {company.id}")

            # create a default Branch
            branch = Branch(
                name='Main',
                company_id=company.id,
                address_id=addr.id
            )
            db.session.add(branch)
            db.session.flush()
            logger.info(f"Created branch with ID: {branch.id}")
            
            # Create a default staff member for the branch
            from werkzeug.security import generate_password_hash
            default_staff = Staff(
                first_name="Admin",
                last_name="User",
                password=generate_password_hash("password123", method='pbkdf2:sha256', salt_length=16),
                phone_number=data['phone'] or "000-000-0000",
                department="Management",
                role="Manager",
                branch_id=branch.id
            )
            db.session.add(default_staff)
            db.session.commit()
            logger.info(f"Created staff with ID: {default_staff.id}")
            
            log_action('COMPANY_CREATED', f'Created company: {company.name} with default admin user')
            flash('Company created with default staff member!', 'success')
            # Redirect to staff tab after company creation
            return redirect(url_for('companies.company_detail', active_tab='staff'))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating/updating company: {str(e)}")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('companies.company_detail', active_tab='company'))

    return redirect(url_for('companies.company_detail', active_tab='company'))

    flash('Please correct errors in the Company form.', 'error')
    return redirect(url_for('companies.company_detail', active_tab='company'))


@companies.route('/company/update-staff', methods=['POST'])
def update_company_staff():
    logger = logging.getLogger(__name__)
    staff_form = StaffForm(request.form)
    
    # For existing staff, password is optional
    staff_id = request.form.get('staff_id')
    if staff_id:
        staff_form.password.validators = []
        staff_form.confirm_password.validators = []
        
        if staff_form.validate_on_submit():
            staff = Staff.query.get_or_404(staff_id)
            staff.first_name = staff_form.first_name.data
            staff.last_name = staff_form.last_name.data
            staff.phone_number = staff_form.phone_number.data
            
            # Only update password if provided
            password_changed = False
            if staff_form.password.data:
                # Check if passwords match
                if staff_form.password.data != staff_form.confirm_password.data:
                    flash('Passwords do not match!', 'error')
                    return redirect(url_for('companies.company_detail', active_tab='staff'))
                
                # Check if current password is provided and correct
                current_password = request.form.get('current_password')
                if current_password:
                    from werkzeug.security import check_password_hash
                    if not check_password_hash(staff.password, current_password):
                        flash('Current password is incorrect!', 'error')
                        return redirect(url_for('companies.company_detail', active_tab='staff'))
                    
                    # Only update password if current password is correct
                    hashed_password = generate_password_hash(
                        staff_form.password.data,
                        method='pbkdf2:sha256',
                        salt_length=16
                    )
                    staff.password = hashed_password
                    password_changed = True
                    logger.info(f"Password changed for staff member {staff.id}")
                else:
                    flash('Current password is required to change password!', 'error')
                    return redirect(url_for('companies.company_detail', active_tab='staff'))
                
            try:
                db.session.commit()
                if password_changed:
                    flash('Staff member updated successfully! Password has been changed.', 'success')
                else:
                    flash('Staff member updated successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error updating staff: {str(e)}")
                flash(f'Error updating staff: {str(e)}', 'error')
        else:
            flash('Please correct the errors in the form.', 'error')
            logger.error(f"Form validation errors: {staff_form.errors}")
    else:
        # Creating new staff
        if staff_form.validate_on_submit():
            # Check if passwords match
            if staff_form.password.data != staff_form.confirm_password.data:
                flash('Passwords do not match!', 'error')
                return redirect(url_for('companies.company_detail', active_tab='staff'))
                
            # Get the first branch
            branch = Branch.query.first()
            if not branch:
                flash('No branch found. Please create a company first.', 'error')
                return redirect(url_for('companies.company_detail', active_tab='company'))
                
            # Hash password
            hashed_password = generate_password_hash(
                staff_form.password.data,
                method='pbkdf2:sha256',
                salt_length=16
            )
            
            # Create new staff
            new_staff = Staff(
                first_name=staff_form.first_name.data,
                last_name=staff_form.last_name.data,
                password=hashed_password,
                phone_number=staff_form.phone_number.data,
                department="Management",
                role="Staff",
                branch_id=branch.id
            )
            
            try:
                db.session.add(new_staff)
                db.session.commit()
                flash('New staff member created successfully with secure password!', 'success')
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error creating staff: {str(e)}")
                flash(f'Error creating staff: {str(e)}', 'error')
        else:
            flash('Please correct the errors in the form.', 'error')
            logger.error(f"Form validation errors: {staff_form.errors}")
    
    return redirect(url_for('companies.company_detail', active_tab='staff'))


@companies.route('/company/delete', methods=['POST'])
def delete_company():
    company = Company.query.order_by(Company.id).first()
    if company:
        delete_cmp(company)
        flash('Company successfully deleted!', 'success')
    else:
        flash('No company found to delete.', 'error')
    return redirect(url_for('companies.company_detail'))

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

logger = logging.getLogger(__name__)

companies = Blueprint('companies', __name__)


@companies.route('/company')
def company_detail():
    import logging
    logger = logging.getLogger(__name__)
    
    active_tab = request.args.get('active_tab', 'company')
    company = Company.query.order_by(Company.id).first()
    
    # Log company details for debugging
    if company:
        logger.info(f"Found company: ID={company.id}, Name={company.name}")
    else:
        logger.info("No company found in database")
    
    # Always create a form, with or without company data
    form = CompanyForm(obj=company) if company else CompanyForm()
    
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
def update_company():
    import logging
    logger = logging.getLogger(__name__)
    
    company = Company.query.order_by(Company.id).first()
    form = CompanyForm()

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
        'postal_code': form.postal_code.data,
        'my_business_address_link': form.my_business_address_link.data if hasattr(form, 'my_business_address_link') else None
    }

    try:
        if company:
            # update existing Company + Address
            logger.info(f"Updating existing company: {company.id}")
            update_company_service(company, data)
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

            # create Company
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


@companies.route('/company/delete', methods=['POST'])
def delete_company():
    company = Company.query.order_by(Company.id).first()
    if company:
        delete_cmp(company)
        flash('Company successfully deleted!', 'success')
    else:
        flash('No company found to delete.', 'error')
    return redirect(url_for('companies.company_detail'))

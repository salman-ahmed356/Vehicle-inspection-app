from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..forms import CompanyForm, StaffForm
from ..services.company_service import (
    get_first_company,
    create_default_company,
    update_company_service,
    create_company,
    delete_company as delete_cmp
)
from ..models import Staff

companies = Blueprint('companies', __name__)


@companies.route('/company')
def company_detail():
    active_tab = request.args.get('active_tab', 'company')
    company    = get_first_company()
    
    # Company form
    form = CompanyForm(obj=company)

    # Staff form for the first staff member
    first_staff = None
    staff_form  = None
    if company and company.branches:
        branch = company.branches[0]
        if branch.staff_members:
            first_staff = branch.staff_members[0]
            staff_form  = StaffForm(obj=first_staff)

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
    company = get_first_company() or create_default_company()
    form    = CompanyForm(obj=company)

    if form.validate_on_submit():
        data = {
            'name'                    : form.name.data,
            'phone'                   : form.phone.data,
            'fax'                     : form.fax.data,
            'email'                   : form.email.data,
            'website'                 : form.website.data,
            'street_address'          : form.street_address.data,
            'city'                    : form.city.data,
            'state'                   : form.state.data,
            'postal_code'             : form.postal_code.data,
            'my_business_address_link': form.my_business_address_link.data
        }
        update_company_service(company, data)
        flash('Company settings updated!', 'success')
        return redirect(url_for('companies.company_detail', active_tab='company'))

    flash('Please correct errors in the Company form.', 'error')
    return redirect(url_for('companies.company_detail', active_tab='company'))


@companies.route('/company/add', methods=['GET', 'POST'])
def add_company():
    form = CompanyForm()
    if form.validate_on_submit():
        data = {
            'name'                    : form.name.data,
            'phone'                   : form.phone.data,
            'fax'                     : form.fax.data,
            'email'                   : form.email.data,
            'website'                 : form.website.data,
            'street_address'          : form.street_address.data,
            'city'                    : form.city.data,
            'state'                   : form.state.data,
            'postal_code'             : form.postal_code.data,
            'my_business_address_link': form.my_business_address_link.data
        }
        create_company(data)
        flash('New company successfully created!', 'success')
        return redirect(url_for('companies.company_detail'))
    return render_template('settings/add_company.html', form=form)


@companies.route('/company/delete', methods=['POST'])
def delete_company():
    company = get_first_company()
    if company:
        delete_cmp(company)
        flash('Company successfully deleted!', 'success')
    else:
        flash('No company found to delete.', 'error')
    return redirect(url_for('companies.company_detail'))

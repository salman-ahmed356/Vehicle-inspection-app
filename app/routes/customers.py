from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import Customer
from ..database import db
from ..forms.customer_form import CustomerForm

customers = Blueprint('customers', __name__)

# Customer List with Pagination
@customers.route('/customers')
def customer_list():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of customers per page
    paginated_customers = Customer.query.paginate(page=page, per_page=per_page)
    form = CustomerForm()

    return render_template('customers.html', paginated_customers=paginated_customers, form=form)

@customers.route('/customers/add', methods=['GET', 'POST'])
def add_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        new_customer = Customer(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            tc_tax_number=form.tc_tax_number.data
        )
        try:
            db.session.add(new_customer)
            db.session.commit()
            flash('Customer added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding customer: {str(e)}', 'error')
        
        return redirect(url_for('customers.customer_list'))
    
    return render_template('customer/add_customer.html', form=form)

@customers.route('/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    form = CustomerForm(obj=customer)
    
    if form.validate_on_submit():
        customer.first_name = form.first_name.data
        customer.last_name = form.last_name.data
        customer.phone_number = form.phone_number.data
        customer.email = form.email.data
        customer.tc_tax_number = form.tc_tax_number.data
        
        try:
            db.session.commit()
            flash('Customer updated successfully!', 'success')
            return redirect(url_for('customers.customer_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating customer: {str(e)}', 'error')
    
    return render_template('customer/edit_customer.html', form=form, customer=customer)

@customers.route('/customers/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    try:
        db.session.delete(customer)
        db.session.commit()
        flash('Customer deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting customer: {str(e)}', 'error')
    
    return redirect(url_for('customers.customer_list'))

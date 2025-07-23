from sqlite3 import IntegrityError
from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..database import db
from ..models import Staff
from ..forms import StaffForm
from ..auth import login_required

staff = Blueprint('staff', __name__)


@staff.route('/staff')
@login_required
def staff_list():
    staff_members = Staff.query.all()
    form = StaffForm()
    return render_template('staff/staff_list.html', staff=staff_members, form=form)


@staff.route('/staff/add', methods=['GET', 'POST'])
def add_staff():
    form = StaffForm()
    if form.validate_on_submit():
        # Check if passwords match
        if form.password.data != form.confirm_password.data:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('staff.staff_list'))
            
        # Get the first branch from the first company
        from ..models import Branch
        branch = Branch.query.first()
        
        if not branch:
            flash('No branch found. Please create a company first.', 'error')
            return redirect(url_for('companies.company_detail', active_tab='company'))
            
        # Hash the password
        hashed_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=16
        )
        
        new_staff = Staff(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            password=hashed_password,
            phone_number=form.phone_number.data,
            department=form.department.data or "Default",
            role=form.role.data,
            branch_id=branch.id
        )
        try:
            db.session.add(new_staff)
            db.session.commit()
            flash('Staff member successfully added!', 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash('Please make sure all values are correct!', 'error')
            print(f"IntegrityError: {e}")

    # After adding, return to the staff list page
    return redirect(url_for('staff.staff_list'))


@staff.route('/staff/edit/<int:id>', methods=['POST'])
def edit_staff(id):
    staff_member = Staff.query.get_or_404(id)
    form = StaffForm(request.form)
    
    # For edit, password is optional, so remove validators
    form.password.validators = []
    form.confirm_password.validators = []

    if form.validate_on_submit():
        staff_member.first_name   = form.first_name.data
        staff_member.last_name    = form.last_name.data
        staff_member.phone_number = form.phone_number.data
        staff_member.role         = form.role.data
        if form.department.data:
            staff_member.department = form.department.data

        # Password is handled separately - only update if provided
        password_changed = False
        if form.password.data:
            # Check if passwords match
            if form.password.data != form.confirm_password.data:
                flash('Passwords do not match!', 'error')
                return redirect(url_for('staff.staff_list'))
            
            # Check if current password is provided and correct
            current_password = request.form.get('current_password')
            if current_password:
                from werkzeug.security import check_password_hash
                if not check_password_hash(staff_member.password, current_password):
                    flash('Current password is incorrect!', 'error')
                    return redirect(url_for('staff.staff_list'))
                
                # Only update password if current password is correct
                hashed_password = generate_password_hash(
                    form.password.data,
                    method='pbkdf2:sha256',
                    salt_length=16
                )
                staff_member.password = hashed_password
                password_changed = True
                print(f"Password changed for staff member {staff_member.id}")
            else:
                flash('Current password is required to change password!', 'error')
                return redirect(url_for('staff.staff_list'))

        try:
            db.session.commit()
            if password_changed:
                flash('Staff member updated successfully! Password has been changed.', 'success')
                print("Password changed successfully for staff member")
            else:
                flash('Staff member updated successfully!', 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash('Update error! Please make sure all values are correct.', 'error')
            print(f"IntegrityError: {e}")
    else:
        flash('Please fill all fields correctly.', 'error')
        print("Form errors:", form.errors)

    # Redirect back to staff list page
    return redirect(url_for('staff.staff_list'))


@staff.route('/staff/delete/<int:id>', methods=['POST'])
def delete_staff(id):
    from flask import session
    
    staff_member = Staff.query.get_or_404(id)
    current_user_id = session.get('user_id')
    is_self_delete = current_user_id and int(current_user_id) == staff_member.id
    
    try:
        db.session.delete(staff_member)
        db.session.commit()
        flash('Staff member successfully deleted!', 'success')
        
        # If user deleted themselves, log them out
        if is_self_delete:
            session.clear()
            flash('You have deleted your account. Please log in with another account.', 'info')
            return redirect(url_for('auth.login'))
            
    except IntegrityError as e:
        db.session.rollback()
        flash('Error during deletion. Please try again.', 'error')
        print(f"IntegrityError: {e}")

    # Redirect back to staff list page
    return redirect(url_for('staff.staff_list'))

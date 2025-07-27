from sqlite3 import IntegrityError
from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..database import db
from ..models import Staff
from ..forms import StaffForm
from ..auth import login_required
from ..rbac import role_required, get_visible_staff, can_edit_staff, can_delete_staff, can_add_staff
from ..services.log_service import log_action

staff = Blueprint('staff', __name__)


@staff.route('/staff')
@login_required
def staff_list():
    staff_members = get_visible_staff()
    form = StaffForm()
    return render_template('staff/staff_list.html', staff=staff_members, form=form)


@staff.route('/staff/add', methods=['GET', 'POST'])
@login_required
def add_staff():
    if not can_add_staff():
        flash('You do not have permission to add staff members.', 'error')
        return redirect(url_for('staff.staff_list'))
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
        
        # Role validation based on current user
        from flask import session
        current_user_role = session.get('user_role', '').lower()
        requested_role = form.role.data.lower()
        
        # Manager can only create workers
        if current_user_role == 'manager' and requested_role != 'worker':
            flash('Managers can only create worker accounts.', 'error')
            return redirect(url_for('staff.staff_list'))
        
        new_staff = Staff(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            password=hashed_password,
            phone_number=form.phone_number.data,
            department=form.department.data or "Default",
            role=requested_role,
            branch_id=branch.id
        )
        try:
            db.session.add(new_staff)
            db.session.commit()
            log_action('STAFF_CREATED', f'Created staff member: {new_staff.full_name} with role: {new_staff.role}')
            flash('Staff member successfully added!', 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash('Please make sure all values are correct!', 'error')
            print(f"IntegrityError: {e}")

    # After adding, return to the staff list page
    return redirect(url_for('staff.staff_list'))


@staff.route('/staff/edit/<int:id>', methods=['POST'])
@login_required
def edit_staff(id):
    if not can_edit_staff(id):
        flash('You do not have permission to edit this staff member.', 'error')
        return redirect(url_for('staff.staff_list'))
    
    staff_member = Staff.query.get_or_404(id)
    form = StaffForm(request.form)
    
    # For edit, password is optional, so remove validators
    form.password.validators = []
    form.confirm_password.validators = []

    if form.validate_on_submit():
        # Role validation based on current user
        from flask import session
        current_user_role = session.get('user_role', '').lower()
        current_user_id = session.get('user_id')
        requested_role = form.role.data.lower()
        
        # Manager can only set role to worker (unless editing themselves)
        if current_user_role == 'manager' and int(current_user_id) != staff_member.id and requested_role != 'worker':
            flash('Managers can only set worker role for other users.', 'error')
            return redirect(url_for('staff.staff_list'))
        
        staff_member.first_name   = form.first_name.data
        staff_member.last_name    = form.last_name.data
        staff_member.phone_number = form.phone_number.data
        staff_member.role         = requested_role
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
            
            # Update session if user is editing their own profile
            from flask import session
            current_user_id = session.get('user_id')
            if current_user_id and int(current_user_id) == staff_member.id:
                # Update the session with new name
                session['user_name'] = staff_member.full_name
                print(f"DEBUG: Updated session user_name to: {staff_member.full_name}")
            
            log_action('STAFF_UPDATED', f'Updated staff member: {staff_member.full_name}')
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
@login_required
def delete_staff(id):
    if not can_delete_staff(id):
        flash('You do not have permission to delete this staff member.', 'error')
        return redirect(url_for('staff.staff_list'))
    
    from flask import session
    
    staff_member = Staff.query.get_or_404(id)
    current_user_id = session.get('user_id')
    is_self_delete = current_user_id and int(current_user_id) == staff_member.id
    
    try:
        # Update reports created by this staff member to avoid foreign key constraint
        from ..models import Report
        admin_user = Staff.query.filter_by(role='admin').first()
        if admin_user:
            reports = Report.query.filter_by(created_by=staff_member.id).all()
            for report in reports:
                report.created_by = admin_user.id  # Assign to admin user
        
        log_action('STAFF_DELETED', f'Deleted staff member: {staff_member.full_name}')
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

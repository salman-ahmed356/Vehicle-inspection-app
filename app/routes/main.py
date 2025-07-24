from flask import Blueprint, render_template, session
from datetime import datetime, date, timedelta
from sqlalchemy import desc
from ..models import Report, Appointment, Customer, Vehicle, Staff
from ..enums import ReportStatus
from ..auth import login_required

main = Blueprint('main', __name__)

# Home Page
@main.route('/dashboard')
@login_required
def index():
    # Get counts for dashboard
    today = date.today()
    month_start = date(today.year, today.month, 1)
    
    # Open reports count
    open_reports_count = Report.query.filter_by(status=ReportStatus.OPENED).count()
    
    # Upcoming appointments count
    upcoming_appointments_count = Appointment.query.filter(Appointment.date >= today).count()
    
    # This week's completed reports (Monday to Sunday)
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Since we don't have a completion_date field, we'll use created_at as proxy
    # In a real system, you'd want a separate completion_date field
    weekly_completed_reports = Report.query.filter(
        Report.status == ReportStatus.COMPLETED,
        Report.created_at >= datetime.combine(week_start, datetime.min.time()),
        Report.created_at <= datetime.combine(week_end, datetime.max.time())
    ).count()
    
    # Debug
    print(f"Weekly completed reports: {weekly_completed_reports}")
    print(f"Week start: {week_start}, Week end: {week_end}")
    print(f"All reports: {Report.query.count()}")
    print(f"Completed reports: {Report.query.filter_by(status=ReportStatus.COMPLETED).count()}")
    
    # Get recent activities for the dashboard
    recent_reports = Report.query.order_by(desc(Report.created_at)).limit(5).all()
    recent_appointments = Appointment.query.filter(Appointment.date >= today).order_by(Appointment.date, Appointment.time).limit(5).all()
    
    # Get total counts
    total_customers = Customer.query.count()
    total_vehicles = Vehicle.query.count()
    
    # Get current staff member
    current_staff = None
    if 'user_id' in session:
        current_staff = Staff.query.get(session['user_id'])
    
    return render_template(
        'home.html',
        open_reports_count=open_reports_count,
        upcoming_appointments_count=upcoming_appointments_count,
        weekly_completed_reports=weekly_completed_reports,
        recent_reports=recent_reports,
        recent_appointments=recent_appointments,
        total_customers=total_customers,
        total_vehicles=total_vehicles,
        current_staff=current_staff
    )

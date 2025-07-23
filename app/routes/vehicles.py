from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..database import db
from ..models import Vehicle, Report
from ..enums import TransmissionType, FuelType, Color
from sqlalchemy.exc import IntegrityError
import base64
from datetime import datetime

vehicles = Blueprint('vehicles', __name__)

@vehicles.route('/vehicles')
def vehicle_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    chassis = request.args.get('chassis')
    
    # Get all vehicles with their latest report (for images)
    vehicles_with_data = []
    
    # Filter by chassis number if provided
    if chassis:
        vehicles = Vehicle.query.filter(Vehicle.chassis_number == chassis).order_by(Vehicle.brand, Vehicle.model).all()
    else:
        vehicles = Vehicle.query.order_by(Vehicle.brand, Vehicle.model).all()
    
    for vehicle in vehicles:
        # Find the latest report for this vehicle that has an image
        latest_report = Report.query.filter_by(vehicle_id=vehicle.id, has_image=True).order_by(Report.inspection_date.desc()).first()
        
        vehicle_data = {
            'vehicle': vehicle,
            'has_image': False,
            'image_data': None
        }
        
        if latest_report and latest_report.image_data:
            vehicle_data['has_image'] = True
            vehicle_data['image_data'] = latest_report.image_data
        
        vehicles_with_data.append(vehicle_data)
    
    # Manual pagination
    total = len(vehicles_with_data)
    start = (page - 1) * per_page
    end = min(start + per_page, total)
    
    # Create a simple pagination object
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'items': vehicles_with_data[start:end],
        'has_prev': page > 1,
        'has_next': end < total,
        'prev_num': page - 1,
        'next_num': page + 1,
        'iter_pages': lambda: range(1, (total // per_page) + (1 if total % per_page > 0 else 0) + 1)
    }
    
    return render_template(
        'vehicle/vehicle_list.html',
        vehicles=pagination['items'],
        pagination=pagination,
        b64encode=base64.b64encode
    )

@vehicles.route('/vehicle/edit/<int:vehicle_id>', methods=['GET', 'POST'])
def edit_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Find the latest report for this vehicle that has an image
    latest_report = Report.query.filter_by(vehicle_id=vehicle.id, has_image=True).order_by(Report.inspection_date.desc()).first()
    
    vehicle_info = {
        'has_image': False,
        'image_data': None
    }
    
    if latest_report and latest_report.image_data:
        vehicle_info['has_image'] = True
        vehicle_info['image_data'] = latest_report.image_data
    
    if request.method == 'POST':
        vehicle.plate = request.form.get('plate')
        vehicle.engine_number = request.form.get('engine_number')
        vehicle.brand = request.form.get('brand')
        vehicle.model = request.form.get('model')
        vehicle.chassis_number = request.form.get('chassis_number')
        vehicle.model_year = int(request.form.get('model_year'))
        vehicle.color = Color[request.form.get('color')]
        vehicle.transmission_type = TransmissionType[request.form.get('gear_type')]
        vehicle.fuel_type = FuelType[request.form.get('fuel_type')]
        vehicle.mileage = int(request.form.get('vehicle_km'))
        
        try:
            db.session.commit()
            flash('Vehicle updated successfully!', 'success')
            return redirect(url_for('vehicles.vehicle_list'))
        except IntegrityError as e:
            db.session.rollback()
            flash(f'Error updating vehicle: {str(e)}', 'error')
    
    # Get enum values for dropdowns
    transmission_types = [(t.name, t.value) for t in TransmissionType]
    fuel_types = [(f.name, f.value) for f in FuelType]
    colors = [(c.name, c.value) for c in Color]
    current_year = datetime.now().year
    
    return render_template(
        'vehicle/edit_vehicle.html', 
        vehicle=vehicle,
        vehicle_info=vehicle_info,
        transmission_types=transmission_types,
        fuel_types=fuel_types,
        colors=colors,
        current_year=current_year,
        b64encode=base64.b64encode
    )

@vehicles.route('/vehicle/delete/<int:vehicle_id>', methods=['POST'])
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    try:
        # Check if the vehicle is associated with any reports
        if vehicle.reports:
            flash('Cannot delete vehicle as it is associated with reports.', 'error')
            return redirect(url_for('vehicles.vehicle_list'))
        
        db.session.delete(vehicle)
        db.session.commit()
        flash('Vehicle deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting vehicle: {str(e)}', 'error')
    
    return redirect(url_for('vehicles.vehicle_list'))
from flask import Blueprint, jsonify, request, send_file, Response
from io import BytesIO
from ..models import Vehicle, Report
from ..auth import login_required
from ..services.expertise_batch_processor import ExpertiseBatchProcessor

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/search/vehicles', methods=['GET'])
@login_required
def search_vehicles():
    query = request.args.get('query', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    # Search for vehicles by chassis number (starting with the query)
    vehicles = Vehicle.query.filter(
        Vehicle.chassis_number.like(f'{query}%')
    ).limit(10).all()
    
    results = []
    for vehicle in vehicles:
        has_image = False
        image_url = None
        
        # Check if the vehicle has an image through a report
        if vehicle.reports:
            for report in vehicle.reports:
                if report.has_image and report.image_data:
                    has_image = True
                    # Use data URL for the image
                    import base64
                    image_data_b64 = base64.b64encode(report.image_data).decode('utf-8')
                    image_url = f"data:image/jpeg;base64,{image_data_b64}"
                    break
        
        results.append({
            'id': vehicle.id,
            'brand': vehicle.brand,
            'model': vehicle.model,
            'chassis_number': vehicle.chassis_number,
            'plate': vehicle.plate,
            'has_image': has_image,
            'image_url': image_url
        })
    
    return jsonify(results)

@api.route('/vehicle/image/<int:vehicle_id>', methods=['GET'])
@login_required
def vehicle_image(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Find a report with an image for this vehicle
    report = Report.query.filter_by(vehicle_id=vehicle_id).filter(Report.has_image == True).first()
    
    if not report or not report.image_data:
        # Return a default image or 404
        return Response(status=404)
    
    # Return the image data
    return send_file(
        BytesIO(report.image_data),
        mimetype='image/jpeg'
    )

@api.route('/expertise/batch/<int:batch_num>', methods=['POST'])
@login_required
def process_expertise_batch(batch_num):
    """Process expertise batches 3 at a time"""
    try:
        if batch_num == 1:
            result = ExpertiseBatchProcessor.process_batch_1()
        elif batch_num == 2:
            result = ExpertiseBatchProcessor.process_batch_2()
        elif batch_num == 3:
            result = ExpertiseBatchProcessor.process_batch_3()
        elif batch_num == 4:
            result = ExpertiseBatchProcessor.process_batch_4()
        else:
            return jsonify({"error": "Invalid batch number. Use 1-4."}), 400
        
        return jsonify({
            "success": True,
            "batch": batch_num,
            "result": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
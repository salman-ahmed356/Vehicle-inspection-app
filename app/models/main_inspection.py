from ..database import db

class MainInspection(db.Model):
    __tablename__ = 'main_inspections'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False, unique=True)
    
    # 19 inspection items with status and comments
    lights_status = db.Column(db.String(10), nullable=True)  # Pass/Fail/None
    lights_comment = db.Column(db.Text, nullable=True)
    lights_comment_arabic = db.Column(db.Text, nullable=True)
    
    body_status = db.Column(db.String(10), nullable=True)
    body_comment = db.Column(db.Text, nullable=True)
    body_comment_arabic = db.Column(db.Text, nullable=True)
    
    chassis_status = db.Column(db.String(10), nullable=True)
    chassis_comment = db.Column(db.Text, nullable=True)
    chassis_comment_arabic = db.Column(db.Text, nullable=True)
    
    paint_status = db.Column(db.String(10), nullable=True)
    paint_comment = db.Column(db.Text, nullable=True)
    paint_comment_arabic = db.Column(db.Text, nullable=True)
    
    roof_status = db.Column(db.String(10), nullable=True)
    roof_comment = db.Column(db.Text, nullable=True)
    roof_comment_arabic = db.Column(db.Text, nullable=True)
    
    bonnet_trunk_status = db.Column(db.String(10), nullable=True)
    bonnet_trunk_comment = db.Column(db.Text, nullable=True)
    bonnet_trunk_comment_arabic = db.Column(db.Text, nullable=True)
    
    fender_status = db.Column(db.String(10), nullable=True)
    fender_comment = db.Column(db.Text, nullable=True)
    fender_comment_arabic = db.Column(db.Text, nullable=True)
    
    doors_status = db.Column(db.String(10), nullable=True)
    doors_comment = db.Column(db.Text, nullable=True)
    doors_comment_arabic = db.Column(db.Text, nullable=True)
    
    bumper_kit_status = db.Column(db.String(10), nullable=True)
    bumper_kit_comment = db.Column(db.Text, nullable=True)
    bumper_kit_comment_arabic = db.Column(db.Text, nullable=True)
    
    rims_status = db.Column(db.String(10), nullable=True)
    rims_comment = db.Column(db.Text, nullable=True)
    rims_comment_arabic = db.Column(db.Text, nullable=True)
    
    engine_status = db.Column(db.String(10), nullable=True)
    engine_comment = db.Column(db.Text, nullable=True)
    engine_comment_arabic = db.Column(db.Text, nullable=True)
    
    gear_box_status = db.Column(db.String(10), nullable=True)
    gear_box_comment = db.Column(db.Text, nullable=True)
    gear_box_comment_arabic = db.Column(db.Text, nullable=True)
    
    differential_status = db.Column(db.String(10), nullable=True)
    differential_comment = db.Column(db.Text, nullable=True)
    differential_comment_arabic = db.Column(db.Text, nullable=True)
    
    four_w_drive_status = db.Column(db.String(10), nullable=True)
    four_w_drive_comment = db.Column(db.Text, nullable=True)
    four_w_drive_comment_arabic = db.Column(db.Text, nullable=True)
    
    transmission_shaft_status = db.Column(db.String(10), nullable=True)
    transmission_shaft_comment = db.Column(db.Text, nullable=True)
    transmission_shaft_comment_arabic = db.Column(db.Text, nullable=True)
    
    alignment_status = db.Column(db.String(10), nullable=True)
    alignment_comment = db.Column(db.Text, nullable=True)
    alignment_comment_arabic = db.Column(db.Text, nullable=True)
    
    tyres_status = db.Column(db.String(10), nullable=True)
    tyres_comment = db.Column(db.Text, nullable=True)
    tyres_comment_arabic = db.Column(db.Text, nullable=True)
    
    brakes_status = db.Column(db.String(10), nullable=True)
    brakes_comment = db.Column(db.Text, nullable=True)
    brakes_comment_arabic = db.Column(db.Text, nullable=True)
    
    exhaust_status = db.Column(db.String(10), nullable=True)
    exhaust_comment = db.Column(db.Text, nullable=True)
    exhaust_comment_arabic = db.Column(db.Text, nullable=True)
    
    # Relationship
    report = db.relationship('Report', backref='main_inspection', lazy=True)
    
    def __repr__(self):
        return f'<MainInspection {self.report_id}>'
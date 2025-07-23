from ..database import db

class ReportSettings(db.Model):
    __tablename__ = 'report_settings'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    
    # Report Customization
    show_customer_info = db.Column(db.Boolean, default=True)
    show_vehicle_info = db.Column(db.Boolean, default=True)
    show_inspection_details = db.Column(db.Boolean, default=True)
    show_photos = db.Column(db.Boolean, default=True)
    
    # Default Values
    default_comments = db.Column(db.Text, nullable=True)
    default_rating = db.Column(db.String(20), default='good')
    
    # PDF Export Settings
    paper_size = db.Column(db.String(10), default='a4')
    orientation = db.Column(db.String(10), default='portrait')
    
    # Branding Options
    logo_position = db.Column(db.String(20), default='top_left')
    primary_color = db.Column(db.String(10), default='#3b82f6')
    
    # Signature Requirements
    require_inspector_signature = db.Column(db.Boolean, default=True)
    require_customer_signature = db.Column(db.Boolean, default=True)
    require_manager_signature = db.Column(db.Boolean, default=False)
    
    # Relationship
    company = db.relationship('Company', backref=db.backref('report_settings', uselist=False))
    
    def __repr__(self):
        return f'<ReportSettings for Company {self.company_id}>'
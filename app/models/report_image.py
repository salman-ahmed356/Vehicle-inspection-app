from ..database import db
from datetime import datetime


class ReportImage(db.Model):
    __tablename__ = 'report_images'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=False)
    filename = db.Column(db.String(255), nullable=True)
    upload_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    report = db.relationship('Report', back_populates='detailed_images')
    
    def __repr__(self):
        return f'<ReportImage {self.id} for Report {self.report_id}>'
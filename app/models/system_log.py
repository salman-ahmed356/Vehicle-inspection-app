from ..database import db
from datetime import datetime

class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    
    user = db.relationship('Staff', backref='system_logs')
    
    def __repr__(self):
        return f'<SystemLog {self.action} by {self.user.full_name if self.user else "System"} at {self.timestamp}>'
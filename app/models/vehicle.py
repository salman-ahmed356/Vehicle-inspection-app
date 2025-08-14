from ..database import db
from ..enums import TransmissionType, FuelType, Color


class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(255), nullable=True)
    engine_number = db.Column(db.String(255), nullable=True)
    brand = db.Column(db.String(255), nullable=True)
    model = db.Column(db.String(255), nullable=True)
    chassis_number = db.Column(db.String(255), nullable=True)
    color = db.Column(db.Enum(Color), nullable=True)
    model_year = db.Column(db.Integer, nullable=True)
    transmission_type = db.Column(db.Enum(TransmissionType), nullable=True)
    fuel_type = db.Column(db.Enum(FuelType), nullable=True)
    mileage = db.Column(db.Integer, nullable=True)

    reports = db.relationship('Report', back_populates='vehicle', lazy=True)

    def __repr__(self):
        return f'<Vehicle {self.plate} - {self.brand} {self.model}>'
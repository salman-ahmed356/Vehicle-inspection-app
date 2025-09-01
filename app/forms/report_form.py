from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, IntegerField, BooleanField, SelectField, SubmitField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Optional, Length, ValidationError
from ..enums import ReportStatus
import re


class ReportForm(FlaskForm):
    # Customer Information
    customer_name = StringField('Customer Name', validators=[DataRequired()])
    customer_phone = StringField('Customer Phone', validators=[DataRequired()])
    customer_tax_no = StringField('Customer Tax No (Optional)', validators=[Optional()])
    customer_email = StringField('Customer Email (Optional)', validators=[Optional()])
    customer_address = TextAreaField('Customer Address (Optional)', validators=[Optional()])


    
    # Vehicle Image - Accept all file types and sizes
    vehicle_image = FileField('Vehicle Image', validators=[Optional()])

    # Vehicle Information
    vehicle_plate = StringField('Vehicle Plate', validators=[DataRequired()])
    brand = StringField('Brand', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    chassis_number = StringField('Chassis Number', validators=[DataRequired()])
    color = SelectField('Color', choices=[], validators=[DataRequired()])
    model_year = IntegerField('Model Year', validators=[DataRequired()])
    gear_type = SelectField('Gear Type', choices=[], validators=[DataRequired()])
    fuel_type = SelectField('Fuel Type', choices=[], validators=[DataRequired()])
    vehicle_km = StringField('Vehicle KM/Mileage', validators=[DataRequired()])
    
    def validate_vehicle_km(self, field):
        """Custom validator for mileage field to handle commas and dots"""
        if field.data:
            # Remove commas, dots, and spaces
            cleaned_value = re.sub(r'[,\s]', '', str(field.data))
            # Replace dots with empty string (assuming they're thousand separators)
            cleaned_value = cleaned_value.replace('.', '')
            
            try:
                # Try to convert to integer
                int_value = int(cleaned_value)
                if int_value < 0:
                    raise ValidationError('Mileage must be a positive number.')
                # Store the cleaned integer value back to the field
                field.data = str(int_value)
            except ValueError:
                raise ValidationError('Please enter a valid mileage number.')
    engine_number = StringField('Engine Number (Optional)', validators=[Optional()])

    # Inspection Information
    created_at = DateTimeField('Created At', validators=[Optional()], format='%Y-%m-%dT%H:%M')
    inspection_date = DateTimeField('Inspection Date', validators=[Optional()], format='%Y-%m-%dT%H:%M')
    package_id = SelectField('Package ID', coerce=int, validators=[DataRequired()], choices=[])
    created_by = SelectField('Created By', coerce=int, validators=[DataRequired()], choices=[])
    registration_document_seen = BooleanField('Registration Document Seen')
    operation = StringField('Operation (Optional)', validators=[Optional()])



    # Submit button
    submit = SubmitField('Create Report')

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, TextAreaField, SubmitField
from wtforms.validators import Optional

class ReportSettingsForm(FlaskForm):
    # Report Customization
    show_customer_info = BooleanField('Show Customer Information')
    show_vehicle_info = BooleanField('Show Vehicle Information')
    show_inspection_details = BooleanField('Show Inspection Details')
    show_photos = BooleanField('Show Vehicle Photos')
    
    # Default Values
    default_comments = TextAreaField('Default Comments', validators=[Optional()])
    default_rating = SelectField('Default Rating', choices=[
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ])
    
    # PDF Export Settings
    paper_size = SelectField('Paper Size', choices=[
        ('a4', 'A4'),
        ('letter', 'Letter'),
        ('legal', 'Legal')
    ])
    orientation = SelectField('Orientation', choices=[
        ('portrait', 'Portrait'),
        ('landscape', 'Landscape')
    ])
    
    # Branding Options
    logo_position = SelectField('Logo Position', choices=[
        ('top_left', 'Top Left'),
        ('top_center', 'Top Center'),
        ('top_right', 'Top Right')
    ])
    primary_color = StringField('Primary Color')
    
    # Signature Requirements
    require_inspector_signature = BooleanField('Require Inspector Signature')
    require_customer_signature = BooleanField('Require Customer Signature')
    require_manager_signature = BooleanField('Require Manager Signature')
    
    submit = SubmitField('Save Settings')
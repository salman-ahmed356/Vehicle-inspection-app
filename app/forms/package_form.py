from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectMultipleField, SelectField, SubmitField
from wtforms.validators import DataRequired

# Hardcoded expertise types as fallback
DEFAULT_EXPERTISE_TYPES = [
    "Paint Expertise",
    "Body Expertise",
    "Engine Expertise",
    "Lateral Drift Expertise",
    "Suspension Expertise",
    "Brake Expertise",
    "Road Expertise",
    "Dyno Expertise",
    "ECU Expertise",
    "Interior Expertise",
    "Exterior Expertise",
    "Mechanical Expertise",
    "Interior & Exterior Expertise",
    "Road & Dyno Expertise",
    "Paint & Body Expertise"
]

class PackageForm(FlaskForm):
    name = StringField(
        'Package Name',
        validators=[DataRequired()]
    )
    price = DecimalField(
        'Package Price (excl. VAT)',
        validators=[DataRequired()]
    )
    contents = SelectMultipleField(
        'Applied Expertises',
        choices=[(et, et) for et in DEFAULT_EXPERTISE_TYPES],  # Default hardcoded choices
        validators=[DataRequired()]
    )
    active = SelectField(
        'Package Status',
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Save')
    
    def populate_expertise_choices(self):
        """Populate the expertise choices from the database if available"""
        # Always use the hardcoded choices to ensure all expertise types are available
        self.contents.choices = [(et, et) for et in DEFAULT_EXPERTISE_TYPES]
        return self

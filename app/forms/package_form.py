from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectMultipleField, SelectField, SubmitField
from wtforms.validators import DataRequired
from app.enums import ExpertiseTypeEnum

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
        choices=[(et.value, et.value) for et in ExpertiseTypeEnum],
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

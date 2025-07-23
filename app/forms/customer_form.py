from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email

class CustomerForm(FlaskForm):
    first_name = StringField(
        'First Name',
        validators=[
            DataRequired(message="First name is required."),
            Length(min=2, max=50, message="First name must be between 2 and 50 characters.")
        ]
    )
    last_name = StringField(
        'Last Name',
        validators=[
            Optional(),
            Length(max=50, message="Last name must be less than 50 characters.")
        ]
    )
    phone_number = StringField(
        'Phone Number',
        validators=[
            DataRequired(message="Phone number is required."),
            Length(min=9, max=15, message="Phone number must be between 9 and 15 characters.")
        ]
    )
    email = StringField(
        'Email',
        validators=[
            Optional(),
            Email(message="Please enter a valid email address.")
        ]
    )
    tc_tax_number = StringField(
        'TC/Tax Number',
        validators=[
            Optional(),
            Length(min=10, max=11, message="TC/Tax number must be between 10 and 11 characters.")
        ]
    )
    submit = SubmitField('Save Customer')
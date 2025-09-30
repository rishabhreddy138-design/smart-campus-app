from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FileField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from .models import User

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters long.")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match.")])
    role = SelectField('Role', choices=[('student', 'Student'), ('faculty', 'Faculty')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class MaterialUploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    file = FileField('Material File (e.g., PDF, DOCX, PPTX)', validators=[DataRequired()])
    submit = SubmitField('Upload Material')
    
class AssignmentCreationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    deadline = DateTimeLocalField('Deadline', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    attachment = FileField('Optional Attachment')
    submit = SubmitField('Create Assignment')

class SubmissionForm(FlaskForm):
    file = FileField('Upload your submission file')
    text_content = TextAreaField('Or paste your submission text here')
    submit = SubmitField('Submit')

    def validate(self, extra_validators=None):
        initial_validation = super(SubmissionForm, self).validate(extra_validators)
        if initial_validation and not self.file.data and not self.text_content.data:
            self.file.errors.append('You must provide either a file or text content.')
            return False
        return initial_validation

class ProfileUpdateForm(FlaskForm):
    name = StringField('Full Name', validators=[Length(min=2, max=150)])
    department = StringField('Department', validators=[Length(max=120)])
    bio = TextAreaField('Bio')
    avatar = FileField('Profile Picture')
    submit = SubmitField('Save Changes')
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, URLField, TimeField, SelectField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm for creating a new cafe
class CafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[DataRequired()])
    map_url = URLField('Map URL', validators=[DataRequired(), URL()])
    img_url = URLField('Image URL', validators=[DataRequired(), URL()])
    location = StringField('Location', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    open_time = TimeField('Open time', validators=[DataRequired()])
    close_time = TimeField('Close time', validators=[DataRequired()])
    coffee_rating = SelectField('Coffee Rating', validators=[DataRequired()],
                                choices=["✘", "☕️", "☕☕", "☕☕☕", "☕☕☕☕", "☕☕☕☕☕"])
    food_rating = SelectField('Food Rating', validators=[DataRequired()],
                                choices=["✘", "🥐", "🥐🥐", "🥐🥐🥐", "🥐🥐🥐🥐", "🥐🥐🥐🥐🥐"])
    wifi_rating = SelectField('Wifi Rating', validators=[DataRequired()],
                                choices=["✘", "📡", "📡📡", "📡📡📡", "📡📡📡📡", "📡📡📡📡📡"])
    power_outlet = SelectField('Power Outlet', validators=[DataRequired()],
                                choices=["✘", "🔌", "🔌🔌", "🔌🔌🔌", "🔌🔌🔌🔌", "🔌🔌🔌🔌🔌"])
    coffee_price = StringField('Average Coffee Price', validators=[DataRequired()])
    body = CKEditorField("Tell us more!", validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create a form to register new users
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


# Create a form to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


# Create a form to add comments
class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")

from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Time
from functools import wraps
from forms import CafeForm, RegisterForm, LoginForm, CommentForm
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import os
import smtplib


# Setting up Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]
ckeditor = CKEditor(app)
Bootstrap5(app)


# Setting up Database
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe Table Configuration
class Cafe(db.Model):
    __tablename__ = "cafes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    phone: Mapped[str] = mapped_column(String(250), nullable=False)
    open_time: Mapped[str] = mapped_column(Time, nullable=False)
    close_time: Mapped[str] = mapped_column(Time, nullable=False)
    coffee_rating: Mapped[str] = mapped_column(String(250), nullable=False)
    food_rating: Mapped[str] = mapped_column(String(250), nullable=False)
    wifi_rating: Mapped[str] = mapped_column(String(250), nullable=False)
    power_outlet: Mapped[str] = mapped_column(String(250), nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    # Create Foreign Key, "users.id" the users refers to the table name of User
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    # Create reference to the User object. The "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="cafes")
    # Parent relationship to the comments
    comments = relationship("Comment", back_populates="parent_cafe")

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# Create a User table for all your registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    # This will act like a list of Cafe objects attached to each User.
    # The "author" refers to the author property in the Cafe class.
    cafes = relationship("Cafe", back_populates="author")
    # Parent relationship: "comment_author" refers to the comment_author property in the Comment class.
    comments = relationship("Comment", back_populates="comment_author")


# Create a table for the comments on the blog posts
class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    # Child relationship:"users.id" The users refers to the table name of the User class.
    # "comments" refers to the comments property in the User class.
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    # Child Relationship to the Cafe
    cafe_id: Mapped[str] = mapped_column(Integer, db.ForeignKey("cafes.id"))
    parent_cafe = relationship("Cafe", back_populates="comments")


with app.app_context():
    db.create_all()


# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# Create an admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is 1 or 2 continue with the route function
        if current_user.id == 1:
            return f(*args, **kwargs)
        elif current_user.id == 2:
            return f(*args, **kwargs)
        # Otherwise return abort with 403 error
        return abort(403)

    return decorated_function


# Register new users into the User database
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/', methods=["GET"])
def home():
    return render_template("index.html", current_user=current_user)


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


# Find Cafes, add Cafes, edit cafes and delete cafe
@app.route('/find-cafes')
def get_all_cafes():
    result = db.session.execute(db.select(Cafe))
    cafes = result.scalars().all()
    return render_template("find-cafes.html", all_cafes=cafes, current_user=current_user)


# Add a POST method to be able to post comments
@app.route("/cafe/<int:cafe_id>", methods=["GET", "POST"])
def show_cafe(cafe_id):
    requested_cafe = db.get_or_404(Cafe, cafe_id)
    # Add the CommentForm to the route
    comment_form = CommentForm()
    # Only allow logged-in users to comment on posts
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_cafe=requested_cafe
        )
        db.session.add(new_comment)
        db.session.commit()
    return render_template("cafe.html", cafe=requested_cafe, current_user=current_user, form=comment_form)


@app.route("/add-cafe", methods=["GET", "POST"])
def add_new_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            phone=form.phone.data,
            open_time=form.open_time.data,
            close_time=form.close_time.data,
            coffee_rating=form.coffee_rating.data,
            food_rating=form.food_rating.data,
            wifi_rating=form.wifi_rating.data,
            power_outlet=form.power_outlet.data,
            coffee_price=form.coffee_price.data,
            body=form.body.data,
            date=date.today().strftime("%B %d, %Y"),
            author=current_user,
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("get_all_cafes"))
    return render_template("add-cafe.html", form=form, current_user=current_user)


# Use a decorator so only an admin user can edit a post
@app.route("/edit-cafe/<int:cafe_id>", methods=["GET", "POST"])
@admin_only
def edit_cafe(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    edit_form = CafeForm(
        name=cafe.name,
        map_url=cafe.map_url,
        img_url=cafe.img_url,
        location=cafe.location,
        phone=cafe.phone,
        open_time=cafe.open_time,
        close_time=cafe.close_time,
        coffee_rating=cafe.coffee_rating,
        food_rating=cafe.food_rating,
        wifi_rating=cafe.wifi_rating,
        power_outlet=cafe.power_outlet,
        coffee_price=cafe.coffee_price,
        body=cafe.body,
        author=cafe.author,
    )
    if edit_form.validate_on_submit():
        cafe.name = edit_form.name.data
        cafe.map_url = edit_form.map_url.data
        cafe.img_url = edit_form.img_url.data
        cafe.location = edit_form.location.data
        cafe.phone = edit_form.phone.data
        cafe.open_time = edit_form.open_time.data
        cafe.close_time = edit_form.close_time.data
        cafe.coffee_rating = edit_form.coffee_rating.data
        cafe.food_rating = edit_form.food_rating.data
        cafe.wifi_rating = edit_form.wifi_rating.data
        cafe.power_outlet = edit_form.power_outlet.data
        cafe.coffee_price = edit_form.coffee_price.data
        cafe.body = edit_form.body.data
        cafe.date = date.today().strftime("%B %d, %Y")
        db.session.commit()
        return redirect(url_for("show_cafe", cafe_id=cafe.id))
    return render_template("add-cafe.html", form=edit_form, is_edit=True, current_user=current_user)


# Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:cafe_id>")
@admin_only
def delete_cafe(cafe_id):
    cafe_to_delete = db.get_or_404(Cafe, cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_cafes'))


# Setting up contact page
MAIL_ADDRESS = os.environ.get("EMAIL_KEY")
MAIL_APP_PW = os.environ.get("PASSWORD_KEY")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = request.form
        send_email(data["name"], data["email"], data["phone"], data["message"])
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False)


def send_email(name, email, phone, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(MAIL_ADDRESS, MAIL_APP_PW)
        connection.sendmail(MAIL_ADDRESS, MAIL_APP_PW, email_message)


if __name__ == "__main__":
    app.run(debug=True, port=5001)

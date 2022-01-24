# Creating a web application for an animal rescue centre
# called 'Paws Rescue Centre'

from tkinter import Variable
from flask import Flask, abort, render_template
from sqlalchemy.orm import backref
from wtforms.validators import Email
from forms import SignUpForm, LoginForm, EditPetForm
from flask import session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dfewfew123213rwdsgert34tgfd1234trgf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///paws.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

"""Model for Pets."""


class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    age = db.Column(db.String)
    bio = db.Column(db.String)
    posted_by = db.Column(db.String, db.ForeignKey('user.id'))


"""Model for Users."""


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    pets = db.relationship('Pet', backref='user')


db.create_all()

# Create "team" user and add it to session
team = User(full_name="Pet Rescue Team",
            email="team@petrescue.co", password="adminpass")
db.session.add(team)

# Create all pets
nelly = Pet(name="Nelly", age="5 weeks",
            bio="I am a tiny kitten rescued by the good people at Paws Rescue Center. I love squeaky toys and cuddles.")
yuki = Pet(name="Yuki", age="8 months",
           bio="I am a handsome gentle-cat. I like to dress up in bow ties.")
basker = Pet(name="Basker", age="1 year",
             bio="I love barking. But, I love my friends more.")
mrfurrkins = Pet(name="Mr. Furrkins", age="5 years", bio="Probably napping.")

# Add all pets to the session
db.session.add(nelly)
db.session.add(yuki)
db.session.add(basker)
db.session.add(mrfurrkins)

# Commit changes in the session
try:
    db.session.commit() # Fails to show all animals after delete pet on the next code run, issue with deleting entry and adding
except Exception as e:
    db.session.rollback()
finally:
    db.session.close()

# """Information regarding the Pets in the System."""
# pets = [
#             {"id": 1, "name": "Nelly", "age": "5 weeks", "bio": "I am a tiny kitten rescued by the good people at Paws Rescue Center. I love squeaky toys and cuddles."},
#             {"id": 2, "name": "Yuki", "age": "8 months", "bio": "I am a handsome gentle-cat. I like to dress up in bow ties."},
#             {"id": 3, "name": "Basker", "age": "1 year", "bio": "I love barking. But, I love my friends more."},
#             {"id": 4, "name": "Mr. Furrkins", "age": "5 years", "bio": "Probably napping."},
#         ]

# """Information regarding the Users in the System."""
# users = [
#             {"id": 1, "full_name": "Pet Rescue Team", "email": "team@pawsrescue.co", "password": "adminpass"},
#         ]


@app.route('/')
def home():
    """View function for homepage"""
    # return "Paws Rescue Center 🐾"
    pets = Pet.query.all()
    return render_template('pawsHome.html', pets=pets)


@app.route('/about')
def about():
    """View function for about page"""
    # statement = '''We are a non-profit organization working as an animal rescue. We aim to help you connect with the purrfect furbaby for you! \
    # The animals you find on our website are rescued and rehabilitated animals. Our mission is to promote the ideology "adopt, don't Shop"! '''
    # return statement
    return render_template('pawsAbout.html')


@app.route('/details/<int:pet_id>', methods=["POST", "GET"])
def details(pet_id):
    """View function for the details page"""
    # pet = next((pet for pet in pets if pet["id"] == pet_id), None)
    form = EditPetForm()
    pet = Pet.query.get(pet_id)
    if pet is None:
        abort(404, "No pet was found with the given ID")
    if form.validate_on_submit():
        pet.name = form.name.data
        pet.age = form.age.data
        pet.bio = form.bio.data
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return render_template("pawsDetails.html", pet=pet, form=form, message="A pet with same name already exists.")
    return render_template('pawsDetails.html', pet=pet, form=form)


# @app.route('/<int:number>')
# def multiplier(number):
#     multiplied = number * 10
#     return "This is " + str(multiplied)

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """View function for the sign up page"""

    form = SignUpForm()
    if form.validate_on_submit():
        # new_user = {"id": len(users)+1, "full_name": form.name.data, "email": form.email.data, "password": form.password.data}
        # users.append(new_user)
        new_user = User(full_name=form.full_name.data,
                        email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return render_template("signup.html", form=form, message="This Email already exists in the system! Please Log in instead.")
        finally:
            db.session.close()
        return render_template("signup.html", message="Successfully signed up")
    return render_template("signup.html", form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # user = next((user for user in users if user["email"] == form.email.data and user["password"] == form.password.data), None)
        user = User.query.filter_by(
            email=form.email.data, password=form.password.data).first()
        if user is None:
            return render_template("login.html", form=form, message="User not found. Please sign up.")
        elif user.email == form.email.data and user.password == form.password.data:
            session['user'] = user.user_id
            # Removing the form paramter in render template shows only message in the login page.
            return render_template("login.html", message="Successfully Logged In")
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('home', _external=True))


@app.route('/delete_pet/<int:pet_id>')
def delete_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if pet is None:
        abort(404, description="No Pet was found with the given ID")
    db.session.delete(pet)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('home', _external=True))


if __name__ == "__main__":
    app.run(debug=True)

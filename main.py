from flask import Flask, render_template, url_for, flash, redirect,session
from forms import RegistrationForm, ResearchForm, LoginForm
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from util import get_weather,places_api,get_places,filter_categories


app = Flask(__name__)

proxied = FlaskBehindProxy(app)  ## add this line
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'eae4d31ce5ddcbd006c3fca0d8183dd2'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
crypt = Bcrypt(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False) 


    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    def check_user_credentials(username,password_candidate):
        user = User.query.filter_by( username = username).first()
        if user is None:
            return False
        else:
            password = user.password
            return crypt.check_password_hash(password,password_candidate)

@app.route("/")
def home():
    return render_template('home.html', subtitle='Home Page', text='This is the home page')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit(): # checks if entries are valid
        password = crypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('search')) # if so - send to home page
    return render_template('register.html', title='Register', form=form)
 

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit(): # checks if entries are valid
        if User.check_user_credentials(form.username.data,form.password.data) == False:
            print("Invalid credential",form.username.data,form.password.data)
            print(User.check_user_credentials(form.username.data,form.password.data))
            flash(f'Invalid username or password')
            return redirect(url_for('login'))
        else:
            print("valid credential")
            return redirect(url_for('search')) # if so - send to home page
    return render_template('login.html', title='Login', form=form)


@app.route("/search", methods=['GET', 'POST'])
def search():
    form = ResearchForm()
    if form.validate_on_submit():
        session["weather"] = get_weather(city = form.city_name.data)
        places_resp = places_api(city = form.city_name.data, rad = int(form.distance.data),\
                                        how_many_places = 10,category = form.activity.data,\
                                             condition = form.condition.data)
        session["places"] = get_places(places_resp)
        suggested_places = places_api(city = form.city_name.data, rad = int(form.distance.data),\
                                        how_many_places = 5,category = filter_categories(session["weather"]),\
                                             condition = "")

        session["suggested_places"] = get_places(suggested_places)
        return redirect(url_for('result'))
    return render_template('search_place.html', title='Search Page', form= form)

@app.route("/result", methods=['GET', 'POST'])
def result():
    category = filter_categories(session["weather"])
    return render_template('result.html', places = session['places'],suggested_places = session['suggested_places'])

# driver code
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
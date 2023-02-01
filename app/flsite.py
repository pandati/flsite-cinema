from flask import Flask, render_template, url_for, request, flash , redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
import  random
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

## __init__

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sdlkfnslkdfslkdfsldfmskdfmsdf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db/postgres'
manager = LoginManager(app)
db = SQLAlchemy(app)

##Models
class list_cinema(db.Model):
    cinema_id = db.Column(db.Integer, primary_key=True)
    cinema_name = db.Column(db.String(1024), nullable=True)
    actors =  db.Column(db.String(1024), nullable=True)
    description = db.Column(db.String(1024), nullable=True)
    release_date =  db.Column(db.String(1024), nullable=True)
    country_of_origin =  db.Column(db.String(1024), nullable=True)
    genre =  db.Column(db.String(1024), nullable=True)
    # user_id =  db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False )
    # user = db.relationship('User', backref =db.backref('list', lazy=True))
    def __init__(self, cinema_name, actors, description, release_date, country_of_origin, genre):
        self.cinema_name = cinema_name
        self.actors = actors
        self.description = description
        self.release_date = release_date
        self.country_of_origin = country_of_origin
        self.genre = genre

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1024), nullable=False, unique=True)
    password = db.Column(db.String(1024), nullable=False)
    def get_id(self):
        return (self.user_id)
    def __init__(self, username, password,):
        self.username = username
        self.password = password

@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)







with app.app_context():
    db.create_all()


## routes


@app.route("/")
def index():
    print( url_for('index'))
    return render_template('index.html' )



@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html'), 404

@app.route("/my_list")
@login_required
def my_list():
    print(url_for('my_list'))
    lists_cinema= list_cinema.query.all()
    return render_template('my_list.html', lists_cinema=lists_cinema)

@app.route("/add_list")
@login_required
def add_list():
    print(url_for('add_list'))
    return render_template('add_list.html')

@app.route("/login", methods = ['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username and password:
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return render_template('my_list.html')
        else:
            flash ('Не верный логин или пороль')
    else:
        flash ('Введите логин и пороль')
    return render_template('login.html')



@app.route('/logout', methods = ['POST', 'GET'] )
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods = ['GET', 'POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    if request.method == 'POST':
        if not (login or password or password2):
            flash('Пожалуйста заполнийте все поля')
        elif password != password2:
            flash('Пороли не совпадают')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(username = username, password = hash_pwd)
            db.session.add(new_user)
            db.session.commit()
            return render_template('login.html')

    return render_template('register.html')
@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login') + '?next=' + request.url)
    return response
##  Надо как то обойти капчу 
@app.route('/add_cinema', methods=['POST', 'GET'])
def add_cinema():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    url = request.form.get('url_cinema')
    browser = webdriver.Chrome('/home/<user>/chromedriver',chrome_options=chrome_options)
    browser.get(url)
    browser.implicitly_wait(random.randint(3,5))
    soup1 = BeautifulSoup(browser.page_source, 'lxml')
    cinema_name1 = soup1.find('span', {'data-tid': '75209b22'})
    if  cinema_name1 == None: 
        button = browser.find_element(By.XPATH, '/html/body/div[1]/div/div/form/div[2]/div/div/div[1]/input')
        browser.implicitly_wait(random.randint(3,7))
        button.click()
        browser.implicitly_wait(random.randint(3,7))
    soup = BeautifulSoup(browser.page_source, 'lxml')
    browser.implicitly_wait(random.randint(3,5))
    cinema_name = soup.find('span', {'data-tid': '75209b22'}).text
    actors = soup.find('a', class_='styles_link__Act80').text
    description = soup.find('p', class_='styles_paragraph__wEGPz').text
    release_date =  soup.find('div', {'data-tid': 'cfbe5a01'}).find('a').text
    country_of_origin = soup.find('div', {'data-tid': 'd5ff4cc'}).find('a').text
    genre = soup.find('div', {'data-tid': '28726596'}).find('a').text

    db.session.add(list_cinema(cinema_name, actors, description, release_date, country_of_origin, genre))
    db.session.commit()


    return render_template('add_list.html')
## start app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
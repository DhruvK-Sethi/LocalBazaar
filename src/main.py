from flask import Flask, redirect, session,url_for,render_template,request
from flask_sqlalchemy import SQLAlchemy, query
from geopy import distance
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from decimal import Decimal
import random
from numpy import require

from sqlalchemy.util import NoneType

# set up server and database and config
app = Flask(__name__)
app.secret_key = "siteee" #security reasons, can be any random word
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///db.sqlite3' #db file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False #makes server sqlite logs less verbose
db = SQLAlchemy(app)

class Buyer(db.Model):
    __tablename__ = 'buyers'
    email = db.Column(db.String(100),unique=True,primary_key=True,nullable=False)
    name = db.Column(db.String(100),nullable=False)
    password = db.Column(db.String(100),nullable=False)
    latitude = db.Column(db.String(100),nullable=True)
    longitude = db.Column(db.String(100),nullable=True)
    state = db.Column(db.String(100),nullable=False)
    city = db.Column(db.String(100),nullable=False)
    phone = db.Column(db.String(100),nullable=False)
    wishlist = db.Column(db.String(2048),nullable=False)
    notification = db.Column(db.String(4096))
    def __init__(self,email,name,password,latitude,longitude,state,city,phone):
        self.email = email
        self.name = name
        self.phone = phone
        self.password = password
        self.latitude = latitude
        self.longitude = longitude
        self.state = state
        self.city = city
        self.wishlist = ' '
        self.notification= "Welcome to the Website |"

class Seller(db.Model):
    __tablename__ = 'sellers'
    email = db.Column(db.String(100),unique=True,primary_key=True,nullable=False)
    name = db.Column(db.String(100),nullable=False)
    password = db.Column(db.String(100),nullable=False)
    latitude = db.Column(db.String(100),nullable=False)
    longitude = db.Column(db.String(100),nullable=False)
    shop_state = db.Column(db.String(100),nullable=False)
    shop_city = db.Column(db.String(100),nullable=False)
    shop_name = db.Column(db.String(100),nullable=False)
    phone = db.Column(db.String(100),nullable=False)
    category = db.Column(db.String(100),nullable=False)
    products = db.relationship('Product',backref='sellers',lazy=True)
    notification = db.Column(db.String(4096))
    item_request = db.Column(db.String(4096))
    views = db.Column(db.Integer)
    def __init__(self,email,name,password,latitude,longitude,shop_state,shop_city,shop_name,phone,category):
        self.email = email
        self.name = name
        self.password = password
        self.latitude = latitude
        self.longitude = longitude
        self.shop_name = shop_name
        self.shop_state = shop_state
        self.shop_city = shop_city
        self.phone = phone
        self.category = category
        self.notification = "Welcome to the Website |"
        self.item_request = ""
        self.views = 0

class Product(db.Model):
    __tablename__ = 'products'
    id= db.Column(db.Integer,primary_key=True,unique=True,nullable=False)
    identifier= db.Column(db.Integer,nullable=False)
    shop = db.Column(db.String(100),db.ForeignKey('sellers.email'),nullable=False)
    name = db.Column(db.String(100),nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100),nullable=False)
    stock = db.Column(db.Integer)
    tags = db.Column(db.String(200))
    category = db.Column(db.String(200))
    description = db.Column(db.String(512))
    stock_over_time = db.Column(db.String(256),nullable=False)
    review = db.Column(db.Float,nullable=False)
    def __init__(self,id,identifier,shop,name,price,stock,tags,description,image):
        self.id = id
        self.shop = shop
        self.name = name
        self.price = price
        self.stock = stock
        self.image = image
        self.tags = tags
        self.category = tags.split(' ')[0]
        self.identifier = identifier
        self.description = description
        self.stock_over_time = ''
        self.review = 0.0

class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer,primary_key=True,unique=True,nullable=True)
    score = db.Column(db.Float,nullable=True)
    score_over_time = db.Column(db.String(256),nullable=False)
    def __init__(self,id):
        self.id = id
        self.score = 0
        self.score_over_time = ''

def calcDistance(product):
    user = None
    if session['type'] == 'b':
        user = Buyer.query.filter_by(email=session['email']).first()
    else:
        user = Seller.query.filter_by(email=session['email']).first()
    point1 = (user.latitude,user.longitude)
    shop = Seller.query.filter_by(email=product.shop).first()
    point2 = (shop.latitude,shop.longitude)
    return geodesic(point1,point2).km

@app.route("/notifications")
def notifications():
    ntfs = Seller.query.filter_by(email=session['email']).first().notification
    notifs = []
    for notif in ntfs.split('|'):
        notifs.append(notif)
    return render_template('notifications.html',notifications=notifs)

@app.route("/search",methods=["GET", "POST"])
def search():
    products = Product.query.all()
    results = []
    words = session['query'].split(' ')
    for product in products:
        tags = product.tags
        for word in words:
            if word in tags.split(' '):
                score = Score.query.filter_by(id=product.identifier).first()
                score.score = Decimal(score.score) + Decimal('0.1')
                strList = score.score_over_time.split(' ')
                strList.pop(-1)
                score.score_over_time = " ".join(strList) + ' ' + "{:.1f}".format(score.score)
                db.session.commit()
                product.distance = calcDistance(product)
                results.append(product)
    return render_template('search.html',query=session['query'],username=session['name'],results=results)

@app.route("/wishlist")
def wishlist():
    user = None
    if session['type'] == 'b':
        user = Buyer.query.filter_by(email=session['email']).first()
    else:
        user = Seller.query.filter_by(email=session['email']).first()
    return render_template('wishlist.html',wishlist=user.wishlist)

@app.route("/graphs")
def graphs():
    if session['type'] != 's':
        return redirect(url_for('home'))
    shop = Seller.query.filter_by(email=session['email']).first()
    products = Product.query.filter_by(category=shop.category)
    id_list = []
    for product in products:
        id_list.append(product.identifier)
        results = db.session.query(Score).filter(Score.id.in_(id_list)).order_by(Score.score).all()
    datas = []
    labels = []
    i=0
    for result in results:
        if(i>=10):
            break
        stonks = result.score_over_time.split(' ')
        int_stonks = list(map(int,stonks))
        datas.append(int_stonks)
        labels.append(Product.query.filter_by(identifier=result.id).first().name)
        i+=1
    return render_template('graphs.html',datas=datas,labels=labels)

@app.route("/shop/<shp>",methods=["GET", "POST"])
def shop(shp):
    shop = Seller.query.filter_by(email=shp).first()
    products = Product.query.filter_by(shop=shop.email)
    return render_template('shop.html',username=session['name'],shop=shop,products=products)
@app.route("/product/<shop>/<prod>",methods=["GET", "POST"])
def product(shop,prod):
    message = ''
    product = Product.query.filter_by(id=prod).first()
    if request.method == "POST":
        if request.form['id'] == 'request':
            shp = Seller.query.filter_by(email=shop).first()
            shp.notification += "|" + "New request for " + product.name
            message = 'Request sent'
        else:
            user = None
            if session['type'] == 'b':
                user = Buyer.query.filter_by(email=session['email']).first()
            else:
                user = Seller.query.filter_by(email=session['email']).first()
            if not prod in user.wishlist.split(' '):
                user.wishlist += prod + " "
                db.session.commit()
                message = "Added to Wishlist"
                score = Score.query.filter_by(id=product.identifier).first()
                score.score = score.score + 5
                strList = score.score_over_time.split(' ')
                strList.pop(-1)
                score.score_over_time = " ".join(strList) + ' ' + "{:.1f}".format(score.score)
                db.session.commit()
            else:
                message = 'Already in wishlist'
    score = Score.query.filter_by(id=product.identifier).first()
    score.score += 1
    strList = score.score_over_time.split(' ')
    strList.pop(-1)
    score.score_over_time = " ".join(strList) + ' ' + "{:.1f}".format(score.score)
    db.session.commit()
    product.distance = calcDistance(product)
    shp = Seller.query.filter_by(email=shop).first()
    shp.views += 1
    db.session.commit()
    return render_template('product.html',username=session['name'],product=product,shp=shp,message=message)

@app.route("/admin/update-stock",methods=["GET", "POST"])
def update_stock():
    if request.method == 'POST':
        for key,value in request.form.items():
            prd = Product.query.filter_by(id=key).first()
            prd.stock = value
            db.session.commit();
    products_list = Seller.query.filter_by(email=session['email']).first().products
    if products_list:
        return render_template('update_stock.html',products_list=products_list)
    return render_template('update_stock.html',products_list=[])

@app.route("/admin/add-stock",methods=["GET", "POST"])
def add_stock():
    if request.method == "POST":
        shop = session['email']
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        tags = request.form['tags']
        description = request.form['description']
        identifier = random.randint(10000,99999)
        id = random.randint(10000,99999)
        image = request.files['image']
        image_path = 'daveydark/src/static/' + str(image.filename) 
        image.save(image_path)
        pdt = Product(id,identifier,shop,name,price,stock,tags,description,url_for('static',filename=image.filename))
        scr = Score(identifier)
        db.session.add(scr)
        db.session.add(pdt)
        db.session.commit()
        return render_template('add_stock.html',message="Added successfully")
    return render_template('add_stock.html')

@app.route("/admin/view-stock")
def view_stock():
    products_list = Seller.query.filter_by(email=session['email']).first().products
    if products_list:
        return render_template('view_stock.html',products_list=products_list)
    return render_template('view_stock.html',products_list=[])

@app.route("/admin")
def admin():
    if session['type'] != 's':
        return redirect(url_for('home'))
    shop = Seller.query.filter_by(email=session['email']).first()
    products = Product.query.filter_by(category=shop.category)
    id_list = []
    for product in products:
        id_list.append(product.identifier)
        results = db.session.query(Score).filter(Score.id.in_(id_list)).order_by(Score.score).all()
    datas = []
    labels = []
    i=0
    for result in results:
        if(i>=10):
            break
        stonks = result.score_over_time.split(' ')
        int_stonks = list(map(int,stonks))
        datas.append(int_stonks)
        labels.append(Product.query.filter_by(identifier=result.id).first().name)
        i+=1
    if session['type'] == 'b':
        return redirect(url_for('home'))
    shop_products = Product.query.filter_by(shop=session['email'])
    sales = []
    for product in shop_products:
        sale = int(product.stock_over_time.split(' ')[-2]) - int(product.stock_over_time.split(' ')[-1])
        if sale <0:
            sale = 0
        sales.append(sale * product.price)
    shop_data = []
    shop_labels = []
    for product in shop_products:
        scorez = Score.query.filter_by(id=product.identifier).first().score_over_time.split(' ')
        int_scorez = list(map(float,scorez))
        shop_data.append(int_scorez)
        shop_labels.append(product.name)
    return render_template('admin.html',datas=datas,labels=labels,shop=shop,sales=format(sum(sales),'.2f'),shop_data=shop_data,shop_labels=shop_labels)

@app.route("/home",methods=["GET", "POST"])
#home page route
def home():
    if request.method == "POST":
        session['query'] = request.form['query'];
        return redirect(url_for('search'))
    if 'name' in session:
        usr = None
        if session['type'] == 'b':
            usr = Buyer.query.filter_by(email=session['email']).first()
        else:
            usr = Seller.query.filter_by(email=session['email']).first()
        shops = Seller.query.all();
        return render_template('home.html',username=session['name'],shops=shops,user=usr)
    return redirect(url_for('login'))

@app.route("/bakery",methods=["GET", "POST"])
def bakery():
    return render_template('bakery.html')

@app.route("/gadgets",methods=["GET", "POST"])
def gadgets():
    return render_template('gadgets.html')

@app.route("/household",methods=["GET", "POST"])
def household():
    return render_template('household.html')

@app.route("/stationary",methods=["GET", "POST"])
def stationary():
    return render_template('stationary.html')

@app.route("/profile",methods=["GET", "POST"])
def profile():
    if session['type'] == 's':
        return redirect(url_for('admin'))
    return "profile of " + session['name']

@app.route("/login",methods=["GET", "POST"])
#login page route
def login():
    if request.method == "POST":
        #check login info
        email = request.form["email"]
        password = request.form["password"]
        usr = Buyer.query.filter_by(email=email).first()
        type = 'b'
        if not usr:
            usr = Seller.query.filter_by(email=email).first()
            type = 's'
        if not usr:
            return redirect(url_for('register'))
        if(usr.password == password):
            session["name"] = usr.name
            session["email"] = usr.email
            session["type"] = type
            return redirect(url_for('home'))
        else:
            return redirect(url_for('register'))
    return render_template("login.html")

@app.route("/request_item",methods=["GET", "POST"])
def request_item():
    return render_template('request_item.html')

@app.route("/register",methods=["GET", "POST"])
#register page route
def register():
    if request.method == "POST":
        form = request.form["form_id"]
        if(form == 'buyer'):
            email = request.form['email']
            name = request.form['name']
            password = request.form['password']
            state = request.form['state']
            city = request.form['city']
            geolocator = Nominatim(user_agent="geoapi")
            latitude = 0
            longitude = 0
            if request.form['latitude'] == '' or request.form['longitude'] == '':
                loc = geolocator.geocode(city + ", " + state + ", India")
                latitude = loc.latitude
                longitude = loc.longitude
            else:
                latitude = request.form['latitude'].split('°')[0]
                longitude = request.form['longitude'].split('°')[0]
            phone = request.form['phone']
            if Seller.query.filter_by(email=email).first():
                #email already used
                return render_template("registeration.html")
            if latitude == "" or longitude == "":
                #location not entered
                return render_template("registeration.html")
            if email=="" or name == "" or password == "" or state=="" or city=="" or phone=="":
                #details not entered
                return render_template("registeration.html")
            byr = Buyer(email,name,password,latitude,longitude,state,city,phone)
            db.session.add(byr)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            #seller form
            email = request.form['email']
            name = request.form['name']
            password = request.form['password']
            shop_state = request.form['state']
            shop_city = request.form['city']
            geolocator = Nominatim(user_agent="geoapi")
            latitude = 0
            longitude = 0
            if request.form['latitude'] == '' or request.form['longitude'] == '':
                loc = geolocator.geocode(shop_city + ", " + shop_state + ", India")
                latitude = loc.latitude
                longitude = loc.longitude
            else:
                latitude = request.form['latitude'].split('°')[0]
                longitude = request.form['longitude'].split('°')[0]
            shop_name = request.form['shopName']
            shop_category = request.form['category']
            phone = request.form['phone']
            if Buyer.query.filter_by(email=email).first():
                #email already used
                return render_template("registeration.html")
            if latitude == "" or longitude == "":
                #location not entered
                return render_template("registeration.html")
            if email=="" or name == "" or password == "" or shop_name == "" or shop_state == "" or shop_city=="" or phone=="":
                #details not entered
                return render_template("registeration.html")
            sllr = Seller(email,name,password,latitude,longitude,shop_state,shop_city,shop_name,phone,shop_category)
            db.session.add(sllr)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template("registeration.html")

@app.route("/")
#main redirect
def root():
    return redirect(url_for("login"))

if __name__ == "__main__":
    # Uncomment when we start using db
    with app.app_context():
        db.create_all()
        print("----------------- DATABASE CREATED -----------------")

    # launch app in production or debug mode
    # Debug mode updates live
    # app.run();
    app.run(debug=True)



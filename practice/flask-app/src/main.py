from flask import Flask,url_for,redirect, render_template,request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "just_do_nothing"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3';
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(100),unique=True,primary_key=True,nullable=False)
    name = db.Column(db.String(100),nullable=False)
    password = db.Column(db.String(100))

    def __init__(self,username,name,password):
        self.username = username
        self.name = name
        self.password = password

class Application(db.Model):
    __tablename__ = 'applications'
    email = db.Column(db.String(100),unique=True,primary_key=True,nullable=False)
    name = db.Column(db.String(100),nullable=False)
    address = db.Column(db.String(100),nullable=False)
    species = db.Column(db.String(100),nullable=False)
    feedback = db.Column(db.String(100),nullable=True)

    def __init__(self,email,name,address,species,feedback):
        self.email = email
        self.name = name
        self.address = address
        self.species = species
        self.feedback = feedback

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/form",methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form["name"];
        email = request.form["email"];
        address = request.form["address"];
        feedback = request.form["notes"];
        species = request.form["species"];
        appl = Application(email,name,address,species,feedback)
        db.session.add(appl);
        db.session.commit();
        return render_template("form_submitted.html",name=name,email=email,address=address,species=species,feedback=feedback)
    return render_template("form.html")

@app.route("/admin",methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user:
            if(user.password == password):
                users_list = User.query.all()
                applications_list = Application.query.all()
                return render_template("admin_panel.html",user=username,users_list=users_list,applications_list=applications_list)
    return render_template("admin_login.html")

@app.route("/admin/register",methods=["GET","POST"])
def admin_register():
    if request.method == "POST":
        username = request.form["username"]
        name = request.form["name"]
        password = request.form["password"]
        confirmPassword = request.form["confirmPassword"];
        if(password != confirmPassword):
            #TODO
            pass
            return render_template("admin_register.html")
        usr = User(username,name,password)
        db.session.add(usr)
        db.session.commit()
        return redirect(url_for("admin_login"))
    return render_template("admin_register.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/")
def root():
    return redirect(url_for("home"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True);




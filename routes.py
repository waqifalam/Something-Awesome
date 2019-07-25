from flask import Flask, render_template, url_for, request, redirect, jsonify, escape
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user, logout_user, login_required
from flask_login import UserMixin
from flask_login import LoginManager
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.init_app(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    post = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f"'{self.title}': '{self.post}')"


@login_manager.user_loader
def load_user(id):
    user = User.query.filter_by(id=id).first()
    return user


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(20), unique=True, nullable=False)
    Password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
            return f"User('{self.Name}', '{self.Password}')"

@app.route("/")
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@app.route("/<string:title>")
def postind(title):
    posts = db.engine.execute("SELECT * FROM POST where title = '%s'" %title)
    return render_template('home1.html', posts=posts, title=title)

@app.route("/post" ,methods = ['POST', 'GET'])
@login_required
def post():
    if request.method == 'POST':
      result = request.form
      post = Post(title=escape(result['Title']), post=escape(result['Content']))
      db.session.add(post)
      db.session.commit()
      return redirect(url_for('home'))
    return render_template('post.html')

@app.route("/posts")
def posts():
    data = []
    posts = db.engine.execute("SELECT * FROM Post")
    for post in posts:
        data2 = {
        'title': post.title,
        'content': post.post}
        data.append(data2)
    return jsonify(data)

@app.route("/posts/<string:title>")
def individual(title):
    data = []
    posts = db.engine.execute("SELECT * FROM Post where title = '%s'" %title)
    print("SELECT * FROM POST where title = '%s'" %title)
    for post in posts:
        data2 = {
        'title': post.title,
        'content': post.post}
        data.append(data2)
    return jsonify(data)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        result = request.form
        #users = db.engine.execute("SELECT * FROM User where (Name = '%s') AND (Password = '%s')"% (result['Name'], result['Password']))
        users = db.engine.execute("SELECT * FROM User where (Name = ?) AND (Password = ?)", (result['Name'], result['Password']))
        for user in users:
            if user:
                tologin = User.query.filter_by(Name=user[1]).first()
                login_user(tologin)
                return redirect(url_for('post'))

        return redirect(url_for('home'))
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/refresh")
def refresh():
    db.drop_all()
    db.create_all()
    user = User(Name="user", Password='password')
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('home'))
if __name__ == '__main__':
    app.run(debug=True)
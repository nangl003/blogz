from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:b10gz!@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] =  True
db = SQLAlchemy(app)
app.secret_key = '!m+h3b35t3v3r0890'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(600))
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content,owner):
        self.title = title
        self.content = content
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owned_blogs')

    def __init__(self, username, password):
        self.username = username
        self.password = password

list_of_blogs = []

users = []

@app.before_request
def require_login():
    allowed_routes = ['login', 'sign_up', 'main_Blog', 'index', 'main_Blog2', 'blog_Entry']
    if(request.endpoint not in allowed_routes and "username" not in session):
        return redirect('/login')

@app.route('/addblog')
def add_Blog():
    return render_template('addblog.html',webpage_title="Add a Blog Entry")

@app.route('/addblog', methods=['POST', 'GET'])
def create_Blog():
    title_error = ""
    content_error = ""
    blog_title = request.form['title']
    blog_content = request.form['content']
    blog_owner = User.query.filter_by(username=session['username']).first()

    if len(blog_title) == 0:
        title_error = "Please enter a blog title!"

    if len(blog_content) == 0:
        content_error = "Please enter blog content!"

    if not title_error and not content_error:
        new_blog = Blog(blog_title, blog_content, blog_owner.id)
        db.session.add(new_blog)
        db.session.commit()
        newly_added_blog = Blog.query.filter_by(title=blog_title).first()
        blog_id = str(newly_added_blog.id)
        return redirect('/blogentry?id=' + blog_id)

    else:
        return render_template('addblog.html', title_error=title_error, content_error=content_error, title=blog_title, content=blog_content)

@app.route('/mainblog', methods=['GET'])
def main_Blog():
    user_id = request.args.get('user')
    if user_id:
        user = User.query.filter_by(id=user_id).first()
        users_blogs = Blog.query.filter_by(owner=user_id).all()
        title = user.username + "'s Blogs"
        return render_template('mainblog.html',list_of_blogs=users_blogs,webpage_title=title)
    else:
        list_of_blogs = Blog.query.all()
        return render_template('mainblog.html',webpage_title="Build a Blog",list_of_blogs=list_of_blogs)

@app.route('/', methods=['POST', 'GET'])
def index():
        users = User.query.all()
        return render_template('index.html',webpage_title="Build a Blog",users=users)

@app.route('/blogentry', methods=['GET'])
def blog_Entry():
    blog_id = int(request.args.get('id'))
    blog = Blog.query.filter_by(id=blog_id).first()
    blog_title = blog.title
    blog_content = blog.content
    return render_template('blogentry.html',blog=blog,title=blog_title,content=blog_content,webpage_title=blog_title)

def valid_username(username):
    if(len(username) < 3 or len(username) > 20):
        return False
    elif(" " in username == True):
        return False
    else:
        return True

def valid_password(password):
    if(len(password) < 3 or len(password) > 30):
        return False
    elif(" " in password == True):
        return False
    else:
        return True 

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not username and not password:
            flash("Please enter a username and password!", "error")
            return render_template('login.html',webpage_title="Log In!")
        elif not valid_username(username) and not valid_password(password):
            flash("Please enter a valid username and password. Valid usernames are greater than 3 characters long and less than 20 characters long, containing no spaces. Valid passwords are greater than 3 characters long and less than 30 characters long, containing no spaces.", "error")
            return render_template('login.html',webpage_title="Log In!")
        elif valid_username(username) and not valid_password(password):
            flash("Please enter a valid password. Valid passwords are greater than 3 characters long and less than 30 characters long, containing no spaces.", "error")
            return render_template('login.html',webpage_title="Log In!")
        elif not valid_username(username) and valid_password(password):
            flash("Please enter a valid username. Valid usernames are greater than 3 characters long and less than 20 characters long, containing no spaces.","error")
            return render_template('login.html',webpage_title="Log In!")
        elif user and user.password == password:
            session['username'] = username
            flash("Logged in as ",username)
            return redirect('/addblog')
        elif user and user.password != password:
            flash('The password is incorrect!', 'error')
            return render_template('login.html',webpage_title="Log In!")
        else:
            flash('That account does not exist!', 'error')
            return render_template('login.html',webpage_title="Log In!")

    return render_template('login.html',webpage_title="Log In!")

@app.route('/signup', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if not username and not password:
            flash("Please enter a username and password!", "error")
            return render_template('signup.html')
        elif not valid_username(username) and not valid_password(password):
            flash("Please enter a valid username and password. Valid usernames are greater than 3 characters long and less than 20 characters long, containing no spaces. Valid passwords are greater than 3 characters long and less than 30 characters long, containing no spaces.", "error")
            return render_template('signup.html')
        elif valid_username(username) and not valid_password(password):
            flash("Please enter a valid password. Valid passwords are greater than 3 characters long and less than 30 characters long, containing no spaces.", "error")
            return render_template('signup.html')
        elif not valid_username(username) and valid_password(password):
            flash("Please enter a valid username. Valid usernames are greater than 3 characters long and less than 20 characters long, containing no spaces.","error")
            return render_template('signup.html')
        elif verify != password:
            flash("The passwords do not match. Please try again.", "error")
            return render_template('signup.html')
        elif existing_user == username:
            flash("This username is already taken. Please enter a new username.", "error")
            return render_template('signup.html')
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/addblog')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

if __name__ == '__main__':
    app.run()
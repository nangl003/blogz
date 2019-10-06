from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Bu!ld@bl0g@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] =  True

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(600))

    def __init__(self, title, content):
        self.title = title
        self.content = content

blogs = []

@app.route('/', methods=['POST','GET'])
def index():
    blogs = Blog.query.all()
    return render_template('mainBlog.html',webpage_title="Build a Blog",blogs=blogs)

@app.route('/addblog')
def add_Blog():
    return render_template('addBlog.html',webpage_title="Add a Blog Entry")


@app.route('/addblog', methods=['POST', 'GET'])
def create_Blog():
    title_error = ""
    content_error = ""
    blog_title = request.form['title']
    blog_content = request.form['content']

    if len(blog_title) == 0:
        title_error = "Please enter a blog title!"

    if len(blog_content) == 0:
        content_error = "Please enter blog content!"

    if not title_error and not content_error:

        new_blog = Blog(blog_title, blog_content)
        db.session.add(new_blog)
        db.session.commit()

        newly_added_blog = Blog.query.filter_by(title=blog_title).first()
        print("newly added blog", newly_added_blog)
        blog_id = str(newly_added_blog.id)

        return redirect('/blogentry?id=' + blog_id)

    else:

        return render_template('addBlog.html', title_error=title_error, content_error=content_error, title=blog_title, content=blog_content)

@app.route('/mainblog')
def main_Blog():
    blogs = Blog.query.all()
    return render_template('mainBlog.html',webpage_title="Build a Blog",blogs=blogs)

@app.route('/blogentry', methods=['GET'])
def blog_Entry():

    blog_id = int(request.args.get('id'))
    blog = Blog.query.filter_by(id=blog_id).first()
    print("blog", blog)
    blog_title = blog.title
    blog_content = blog.content
    return render_template('blogEntry.html',blog=blog,title=blog_title,content=blog_content,webpage_title=blog_title)

if __name__ == '__main__':
    app.run()
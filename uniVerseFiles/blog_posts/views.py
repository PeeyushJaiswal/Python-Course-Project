from flask import render_template, url_for, flash, redirect, request, Blueprint, make_response
from flask_login import current_user, login_required
import pandas as pd
from io import BytesIO
from uniVerseFiles import db
from uniVerseFiles.models import BlogPost, User
from uniVerseFiles.blog_posts.forms import BlogPostForm

blog_posts = Blueprint('blog_posts', __name__)

@blog_posts.route('/create',methods=['GET','POST'])
@login_required
def create_post():
    form = BlogPostForm()

    if form.validate_on_submit():

        blog_post = BlogPost(title=form.title.data,
                             text=form.text.data,
                             user_id=current_user.id
                             )
        db.session.add(blog_post)
        db.session.commit()
        flash("Blog Post Created")
        return redirect(url_for('core.index'))

    return render_template('create_post.html',form=form)

@blog_posts.route('/<int:blog_post_id>')
def blog_post(blog_post_id):
    blog_post = BlogPost.query.get_or_404(blog_post_id)
    return render_template('blog_post.html',title=blog_post.title,
                            date=blog_post.date,post=blog_post
    )

@blog_posts.route("/<int:blog_post_id>/update", methods=['GET', 'POST'])
@login_required
def update(blog_post_id):
    blog_post = BlogPost.query.get_or_404(blog_post_id)
    if blog_post.author != current_user:
        abort(403)

    form = BlogPostForm()
    if form.validate_on_submit():
        blog_post.title = form.title.data
        blog_post.text = form.text.data
        db.session.commit()
        flash('Post Updated')
        return redirect(url_for('blog_posts.blog_post', blog_post_id=blog_post.id))
    elif request.method == 'GET':
        form.title.data = blog_post.title
        form.text.data = blog_post.text
    return render_template('create_post.html', title='Update',
                           form=form)


@blog_posts.route("/<int:blog_post_id>/delete", methods=['POST'])
@login_required
def delete_post(blog_post_id):
    blog_post = BlogPost.query.get_or_404(blog_post_id)
    if blog_post.author != current_user:
        abort(403)
    db.session.delete(blog_post)
    db.session.commit()
    flash('Post has been deleted')
    return redirect(url_for('core.index'))


@blog_posts.route('/download')
def download_posts():
    posts = BlogPost.query.all()

    posts_list = [{
        'Title': post.title, 
        'Content': post.text,
        'Author': post.author.username,
        'Date': post.date.strftime("%Y-%m-%d %H:%M:%S")
    } for post in posts]

    df = pd.DataFrame(posts_list)

    csv_data = df.to_csv(index=False).encode('utf-8')

    output = BytesIO(csv_data)

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=blog_posts.csv"
    response.headers["Content-type"] = "text/csv"

    return response

import os
import random

import requests
from flask import Flask, render_template, request, make_response, abort, url_for
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import redirect

from data import db_session
from data.users import User
from data.articles import Articles
from data.new_articles import NewArticles
from forms.user import *
from forms.articles import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/blogs.db")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.about = form.about.data
        user.status = 'user'
        user.icon = 'static/img/user.png'
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/personage")
def personage():
    db_sess = db_session.create_session()
    news = db_sess.query(Articles).filter(Articles.type == 'personage')
    return render_template("index.html", news=news, title='Персонажи')


@app.route("/planets")
def planets():
    db_sess = db_session.create_session()
    news = db_sess.query(Articles).filter(Articles.type == 'planets')
    return render_template("index.html", news=news, title='Планеты')


@app.route("/chapter")
def chapter():
    db_sess = db_session.create_session()
    news = db_sess.query(Articles).filter(Articles.type == 'chapter')
    return render_template("index.html", news=news, title='Сюжет')


@app.route("/story")
def story():
    db_sess = db_session.create_session()
    news = db_sess.query(Articles).filter(Articles.type == 'story')
    return render_template("index.html", news=news, title='Истории')


@login_required
@app.route("/sort-articles")
def sort_articles():
    if current_user.status == 'admin' or current_user.status == 'main-admin':
        db_sess = db_session.create_session()
        art = db_sess.query(NewArticles).all()
        return render_template("cheakarticles.html", art=art)
    else:
        return 'НЕДОСТАТОЧНО ПРАВ'


@login_required
@app.route("/add-admin")
def add_admin():
    if current_user.status == 'main-admin':
        db_sess = db_session.create_session()
        art = db_sess.query(User).all()
        return render_template("add-admin.html", art=art)
    else:
        return 'НЕДОСТАТОЧНО ПРАВ'


@app.route('/del-admin/<int:id>', methods=['GET', 'POST'])
@login_required
def del_admin(id):
    if current_user.status == 'main-admin':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        user.status = 'user'
        db_sess.merge(user)
        db_sess.commit()
        return redirect('/add-admin')
    else:
        return "НЕДОСТАТОЧНО ПРАВ"


@app.route('/add-admin/<int:id>', methods=['GET', 'POST'])
@login_required
def add_admin3(id):
    if current_user.status == 'main-admin':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        user.status = 'admin'
        db_sess.merge(user)
        db_sess.commit()
        return redirect('/add-admin')
    else:
        return "НЕДОСТАТОЧНО ПРАВ"


@app.route('/del-articles/<int:id>', methods=['GET', 'POST'])
@login_required
def new_art_delete(id):
    if current_user.status == 'admin' or current_user.status == 'main-admin':
        db_sess = db_session.create_session()
        new_articles = db_sess.query(NewArticles).filter(NewArticles.id == id).first()
        if new_articles:
            icon = new_articles.icon
            if icon != 'static/img/Articles.png':
                os.remove(f'static/img/db/articles/{icon.split("/")[-1]}')
            db_sess.delete(new_articles)
            db_sess.commit()
        return redirect('/sort-articles')
    else:
        return "НЕДОСТАТОЧНО ПРАВ"


@app.route('/del-a/<int:id>', methods=['GET', 'POST'])
@login_required
def a_delete(id):
    if current_user.status == 'main-admin':
        db_sess = db_session.create_session()
        new_articles = db_sess.query(Articles).filter(Articles.id == id).first()
        if new_articles:
            icon = new_articles.icon
            if icon != 'static/img/Articles.png':
                os.remove(f'static/img/db/articles/{icon.split("/")[-1]}')
            db_sess.delete(new_articles)
            db_sess.commit()
        return redirect('/')
    else:
        return "НЕДОСТАТОЧНО ПРАВ"


@app.route('/add-new-art/<int:id>', methods=['GET', 'POST'])
@login_required
def new_art_add(id):
    if current_user.status == 'admin' or current_user.status == 'main-admin':
        db_sess = db_session.create_session()
        new_articles = db_sess.query(NewArticles).filter(NewArticles.id == id).first()
        if new_articles:
            art = Articles()
            art.type = new_articles.type
            icon = new_articles.icon.split('/')
            if len(icon) != 3:
                fn = icon[-1][3:]
                i = random.randint(1, 1000)
                while fn in os.listdir('static/img/db/articles/'):
                    fn = str(i) + fn
                os.rename(f'static/img/db/articles/{icon[-1]}', f'static/img/db/articles/{fn}')
                icon[-1] = fn
                icon = '../' + '/'.join(icon)
                art.icon = icon
            else:
                art.icon = f'static/img/Articles.png'
            art.title = new_articles.title
            art.content = new_articles.content
            art.user = new_articles.user
            art.created_date = new_articles.created_date
            new_articles.user.articles.append(art)
            db_sess.merge(new_articles.user)
            db_sess.delete(new_articles)
            db_sess.commit()
        return redirect('/sort-articles')
    else:
        return "НЕДОСТАТОЧНО ПРАВ"


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/profile')
def profile():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        user = db_sess.query(User).filter(User.id == current_user.id).first()
    else:
        return 'Вы не вошли в систему!'
    return render_template('profile.html', user=user)


@app.route('/articles',  methods=['GET', 'POST'])
@login_required
def articles():
    if request.method == 'GET':
        return render_template('addarticles.html')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        new_art = NewArticles()
        new_art.title = request.form['title']
        new_art.content = request.form['content']
        new_art.type = request.form['type']
        new_art.user = current_user
        current_user.new_articles.append(new_art)
        db_sess.merge(current_user)
        db_sess.commit()

        db_sess = db_session.create_session()
        new_art = db_sess.query(NewArticles).all()[-1]
        f = request.files['file']
        if not f:
            new_art.icon = f'static/img/Articles.png'
        else:
            filename = f'new{new_art.id}.jpg'
            f.save(os.path.join('static/img/db/articles', filename))
            new_art.icon = f'static/img/db/articles/{filename}'
        db_sess.commit()
        return redirect('/profile')


@app.route('/articles/<int:id>')
def show_articles(id):
    db_sess = db_session.create_session()
    news = db_sess.query(Articles).filter(Articles.id == id).first()
    request = f"http://numbersapi.com/{id}/trivia"
    response = requests.get(request)
    res = response.text
    return render_template(
        'articles.html', news=news, title=f'{news.title.capitalize()}', t='2',
        fact=f'this is article number {id}, an interesting fact: {res}')


@app.route('/new-articles/<int:id>')
def show_new_articles(id):
    db_sess = db_session.create_session()
    news = db_sess.query(NewArticles).filter(NewArticles.id == id).first()
    return render_template('articles.html', news=news, title=f'{news.title.capitalize()}', t='1')


@app.route('/add-icon', methods=['POST', 'GET'])
def sample_file_upload():
    if request.method == 'GET':
        return render_template('add_image.html')
    elif request.method == 'POST':
        f = request.files['file']
        filename = f'{current_user.id}.jpg'
        f.save(os.path.join('static/img/db/profile', filename))
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.icon = f'static/img/db/profile/{filename}'
        db_sess.commit()
        return redirect('/profile')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

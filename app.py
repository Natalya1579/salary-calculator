from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import config
from db import db
from models import User, Profession, SalaryReport

# Создаем приложение
app = Flask(__name__)

# Настройки
app.config.from_object('config')

# Привязываем db к приложению
db.init_app(app)        # теперь db знает про app

# Настраиваем вход пользователей
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # если не залогинен, отправлять на логин

# Найти пользователя по номеру
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Страницы сайта
@app.route('/')
def index():
    return render_template('index.html', title='Salary Calculator')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Проверяем, не занят ли пароль
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Пользователь с таким именем или email уже существует', 'danger')
            return redirect(url_for('register'))

        # Создаем нового пользователя
        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash('Регистрация успешна! Теперь войдите в систему', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'С возвращением, {username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    return render_template('login.html', title='Вход')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('index'))


# Запуск
if __name__ == '__main__':
    with app.app_context():
        db.create_all()     # создаем таблицы в базе данных
    app.run(debug=True)     # запускаем сервер

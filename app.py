from flask import Flask, render_template
from flask_login import LoginManager
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


# Запуск
if __name__ == '__main__':
    with app.app_context():
        db.create_all()     # создаем таюблицы в базе данных
    app.run(debug=True)     # запускаем сервер

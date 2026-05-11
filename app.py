from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import config
from db import db
from models import User, Profession, SalaryReport
import statistics

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
        existing_user = User.query.filter(User.username == username).first()
        if existing_user:
            flash('Такой логин уже занят', 'danger')
            return redirect(url_for('register'))

        # Проверяем, не занят ли email
        existing_email = User.query.filter(User.email == email).first()
        if existing_email:
            flash('Такой email уже зарегистрирован', 'danger')
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

        # Ищем пользователя
        user = User.query.filter_by(username=username).first()

        # Проверяем пароль
        if user and check_password_hash(user.password_hash, password):
            # session['user_id'] = user.id
            # session['username'] = user.username
            login_user(user)
            flash(f'Добро пожаловать, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль', 'danger')
    return render_template('login.html', title='Вход')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('index'))


@app.route('/add-salary', methods=['GET', 'POST'])
@login_required
def add_salary():
    if request.method == 'POST':
        profession_title = request.form['profession_title']
        city = request.form['city']
        salary = int(request.form['salary'])
        work_format = request.form.get('work_format', 'office')
        grade = request.form.get('grade', 'middle')
        is_anonymous = 'is_anonymous' in request.form

        # Находим или создаем профессию
        profession = Profession.query.filter_by(title=profession_title).first()
        if not profession:
            profession = Profession(title=profession_title)
            db.session.add(profession)
            db.session.commit()

        # Создаем запись о зарплате
        report = SalaryReport(
            profession_id=profession.id,
            city=city,
            salary=salary,
            work_format=work_format,
            grade=grade,
            is_anonymous=is_anonymous,
            user_id=None if is_anonymous else current_user.id
        )
        db.session.add(report)
        db.session.commit()

        flash('Зарплата добавлена анонимно' if is_anonymous else 'Зарплата добавлена', 'success')
        return redirect(url_for('profession_page', id=profession.id))
    return render_template('add_salary.html', title='Добавить зарплату')


@app.route('/professions')
def professions_list():
    professions = Profession.query.all()
    return render_template('professions.html', professions=professions, title='Профессии')


@app.route('/profession/<int:id>')
def profession_page(id):
    # Находим профессию в БД
    profession = Profession.query.get(id)

    if not profession:
        flash('Профессия не найдена', 'danger')
        return redirect(url_for('professions_list'))

    # Находим все зарплаты для этой профессии
    reports = SalaryReport.query.filter_by(profession_id=id).all()

    # Количество зарплат для этой профессии
    count = len(reports)

    if count > 0:
        total = 0
        for report in reports:
            total += report.salary
        average = total // count

        min_salary = reports[0].salary
        max_salary = reports[0].salary

        for report in reports:
            if report.salary < min_salary:
                min_salary = report.salary
            if report.salary > max_salary:
                max_salary = report.salary
    else:
        average = 0
        min_salary = 0
        max_salary = 0

    # Считаем статистику по городам
    cities = {}
    for report in reports:
        if report.city not in cities:
            cities[report.city] = [report.salary]
        else:
            cities[report.city].append(report.salary)

    # Для каждого города считаем среднюю зарплату
    city_stats = {}
    for city, salaries in cities.items():
        city_stats[city] = sum(salaries) // len(salaries)

    # Сортировка по городам
    sorted_cities = sorted(city_stats.items(), key=lambda x: x[1], reverse=True)

    # Считаем статистику по формату работы
    work_formats = {}
    for report in reports:
        if report.work_format not in work_formats:
            work_formats[report.work_format] = [report.salary]
        else:
            work_formats[report.work_format].append(report.salary)

    # Для каждого формата работы считаем среднюю зарплату
    work_format_stats = {}
    for work_format, salaries in work_formats.items():
        work_format_stats[work_format] = sum(salaries) // len(salaries)

    # Сортировка по формату работы
    sorted_work_formats = sorted(work_format_stats.items(), key=lambda x: x[1], reverse=True)

    # Считаем статистику по грейдам
    grades = {}
    for report in reports:
        if report.grade not in grades:
            grades[report.grade] = [report.salary]
        else:
            grades[report.grade].append(report.salary)

    # Для каждого грейда считаем среднюю зарплату
    grade_stats = {}
    for grade, salaries in grades.items():
        grade_stats[grade] = sum(salaries) // len(salaries)

    # Сортировка по грейду
    sorted_grades = sorted(grade_stats.items(), key=lambda x: x[1], reverse=True)

    # Передаем в шаблон
    return render_template('profession.html',
                           profession=profession,
                           count=count,
                           average=average,
                           min_salary=min_salary,
                           max_salary=max_salary,
                           reports=reports,
                           city_stats=sorted_cities,
                           work_format_stats=sorted_work_formats,
                           grade_stats=sorted_grades)


# Запуск
if __name__ == '__main__':
    with app.app_context():
        db.create_all()     # создаем таблицы в базе данных
    app.run(debug=True)     # запускаем сервер

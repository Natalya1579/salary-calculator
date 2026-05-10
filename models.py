from db import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime


# Таблица пользователей
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    salary_reports = db.relationship(
        'SalaryReport',    # указывает с какой моделью устанавливается связь
        backref='author',  # автоматически добавляет 'author' в SalaryReport
        lazy=True          # объекты загружаются из БД только когда нужны
    )
    favorites = db.relationship('Favorite', foreign_keys='Favorite.user_id', backref='user', lazy=True)
    following = db.relationship('Follow', foreign_keys='Follow.follower_id', backref='follower', lazy=True)
    followers = db.relationship('Follow', foreign_keys='Follow.followed_id', backref='followed', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


# Таблица профессий
class Profession(db.Model):
    __tablename__ = 'professions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50))     # IT, Marketing, Строительство итд

    # Отношения
    salary_reports = db.relationship(
        'SalaryReport', backref='profession', lazy=True
    )

    def __repr__(self):
        return f'<Profession {self.title}>'


# Таблица зарплат
class SalaryReport(db.Model):
    __tablename__ = 'salary_reports'

    id = db.Column(db.Integer, primary_key=True)
    profession_id = db.Column(db.Integer, db.ForeignKey('professions.id'), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Integer, nullable=False)  # зарплата в рублях
    work_format = db.Column(db.String(20))          # office, remote, hybrid
    grade = db.Column(db.String(20))                # junior, middle, senior, lead
    is_anonymous = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SalaryReport {self.profession.title}: {self.salary}>'


class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    profession_id = db.Column(db.Integer, db.ForeignKey('professions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Favorite {self.user_id} {self.profession_id}>'


class Follow(db.Model):
    __tablename__ = 'follows'

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)   # кто подписался
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)   # на кого подписались
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

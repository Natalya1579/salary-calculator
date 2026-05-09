from flask import Flask, render_template

# Создаем приложение
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title='Salary Calculator')

# Запуск
if __name__ == '__main__':
    app.run(debug=True)

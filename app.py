import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


import os
import sqlite3

# Получаем точный абсолютный путь к папке, где лежит этот файл app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'math_ege.db')

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    conn = sqlite3.connect('math_ege.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Таблица заданий (поддержка чертежей: опционально для №1, №3, №9, №17; обязательно для №12)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_number INTEGER NOT NULL,
            topic TEXT NOT NULL,
            text TEXT NOT NULL,
            answer TEXT NOT NULL,
            explanation TEXT,
            part INTEGER NOT NULL,
            image_url TEXT
        )
    ''')

    # 2. Таблица общей истории тестирований
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            mode_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            percent INTEGER NOT NULL
        )
    ''')

    # 3. Таблица истории ответов по темам для аналитики
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            date TEXT NOT NULL
        )
    ''')

    # Первоначальное наполнение базы данных
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        sample_tasks = [
            # === ЧАСТЬ 1 (№1 — №12) ===
            (1, 'Планиметрия',
             'В равнобедренной трапеции основания равны 8 и 14, а углы при большем основании равны 60°. Найдите периметр трапеции.',
             '34',
             'Высоты отсекают отрезки по (14 - 8)/2 = 3. Боковая сторона равна 3 / cos(60°) = 6. Периметр = 8 + 14 + 6 + 6 = 34.',
             1, '/static/images/task_1.png'),

            (2, 'Векторы на плоскости',
             'Даны векторы a(4; y) и b(3; -6). Найдите значение y, при котором векторы a и b перпендикулярны.',
             '2',
             'Условие перпендикулярности: a · b = 0 => 4*3 + y*(-6) = 0 => 12 - 6y = 0 => y = 2.',
             1, None),

            (3, 'Стереометрия',
             'В прямую призму, в основании которой лежит прямоугольный треугольник с катетами 6 и 8, описан цилиндр. Найдите объем цилиндра, если высота призмы равна 5/π.',
             '125',
             'Гипотенуза основания = √(6² + 8²) = 10. Радиус R = 10 / 2 = 5. Объем V = π * R² * h = π * 25 * (5/π) = 125.',
             1, '/static/images/task_3.png'),

            (4, 'Теория вероятностей (простые)',
             'Вероятность того, что новый электрический чайник прослужит больше года, равна 0,93. Вероятность того, что он прослужит больше двух лет, равна 0,87. Найдите вероятность того, что он прослужит меньше двух лет, но больше года.',
             '0,06',
             'P = 0,93 - 0,87 = 0,06.',
             1, None),

            (5, 'Теория вероятностей (сложные)',
             'Биатлонист 5 раз стреляет по мишеням. Вероятность попадания при одном выстреле равна 0,8. Найдите вероятность того, что биатлонист первые 3 раза попал, а последние 2 раза промахнулся.',
             '0,02048',
             'P = 0,8 * 0,8 * 0,8 * 0,2 * 0,2 = 0,512 * 0,04 = 0,02048.',
             1, None),

            (6, 'Простейшие уравнения',
             'Найдите корень уравнения log₄(5x - 1) = 2.',
             '3,4',
             '5x - 1 = 4² => 5x - 1 = 16 => 5x = 17 => x = 3,4.',
             1, None),

            (7, 'Вычисления и преобразования',
             'Найдите значение выражения (√28 - √7) * √7.',
             '7',
             '√28 * √7 - √7 * √7 = √196 - 7 = 14 - 7 = 7.',
             1, None),

            (8, 'Производная и геометрический смысл',
             'На рисунке изображен график функции y = f(x) и касательная к нему в точке с абсциссой x₀. Касательная проходит через точки (0; 1) и (2; 5). Найдите значение производной f\'(x₀).',
             '2',
             'Значение производной равно угловому коэффициенту касательной: k = (5 - 1) / (2 - 0) = 2.',
             1, '/static/images/task_8.png'),

            (9, 'Задачи с прикладным содержанием',
             'Зависимость температуры (в K) от времени задана формулой T(t) = T₀ + a*t + b*t², где T₀ = 1000 K, a = 85 K/мин, b = -0,5 K/мин². При температуре выше 1350 K прибор может испортиться. Найдите наименьшее время в минутах, через которое прибор нужно отключить.',
             '20',
             '1000 + 85t - 0,5t² = 1350 => t² - 170t + 700 = 0. Корни t = 20 и t = 150. Наименьшее время: 20 мин.',
             1, None),

            (10, 'Текстовые задачи',
             'Теплоход проходит по течению реки до пункта назначения 140 км и после стоянки возвращается в пункт отправления. Найдите скорость теплохода в неподвижной воде, если скорость течения равна 4 км/ч, стоянка длится 3 часа, а возвращается он через 15 часов.',
             '24',
             'Время в пути = 15 - 3 = 12 ч. 140/(v + 4) + 140/(v - 4) = 12 => 3v² - 70v - 48 = 0 => v = 24 км/ч.',
             1, None),

            (11, 'Графики функций',
             'На рисунке изображен график функции f(x) = a cos x + b. Найдите значение b, если наименьшее значение функции равно -1, а наибольшее равно 5.',
             '2',
             'Амплитуда a = (5 - (-1)) / 2 = 3. Сдвиг по вертикали b = (5 + (-1)) / 2 = 2.',
             1, '/static/images/task_11.png'),

            (12, 'Наибольшее и наименьшее значение функций',
             'Найдите наименьшее значение функции y = x³ - 3x + 5 на отрезке [0; 2].',
             '3',
             'y\' = 3x² - 3 = 0 => x = 1. y(0) = 5, y(1) = 3, y(2) = 7. Наименьшее значение равно 3.',
             1, None),

            # === ЧАСТЬ 2 (№13 — №19) ===
            (13, 'Уравнения (Часть 2)',
             'а) Решите уравнение (2sin²x - sin x) / (tan x - √3) = 0.\nб) Укажите корни этого уравнения, принадлежащие отрезку [2π; 7π/2].',
             'a) x = πk, x = 5π/6 + 2πk; б) 2π, 17π/6, 3π',
             'ОДЗ: x ≠ π/3 + πk. Из числителя sin x (2sin x - 1) = 0. С учетом ОДЗ остаются x = πk и x = 5π/6 + 2πk.',
             2, None),

            (14, 'Стереометрия (Часть 2)',
             'В тетраэдре ABCD ребро AD перпендикулярно плоскости ABC, AB = BC = AC = 6, AD = 4.\nа) Докажите, что скрещивающиеся рёбра AD и BC перпендикулярны.\nб) Найдите угол между плоскостями ABC и BDC.',
             'a) Доказано; б) arctg(2√3 / 3)',
             'а) Так как AD ⊥ (ABC), прямая AD перпендикулярна любой прямой в плоскости (ABC), включая BC.\nб) AH = 3√3, tg ∠AHD = AD / AH = 4 / (3√3) = 2√3/3.',
             2, None),

            (15, 'Неравенства (Часть 2)',
             'Решите неравенство: 9^(x + 0.5) - 28 * 3^(x - 1) + 1 ≥ 0.',
             '(-∞; -2] ∪ [1; +∞)',
             'Пусть t = 3^x > 0. Получаем 9t² - 28t + 3 ≥ 0. Корни t = 1/9 и t = 3 => x ≤ -2 или x ≥ 1.',
             2, None),

            (16, 'Экономическая задача (Часть 2)',
             'В июле 2026 года планируется взять кредит на некоторую сумму под 20% годовых. Кредит будет полностью погашен тремя равными платежами за три года, и общая сумма выплат на 77 200 рублей больше суммы кредита. Сколько рублей планируется взять в банке?',
             '182000',
             '3X - S = 77200 и 1.728S - 3.64X = 0 => X = (216/455)S => (193/455)S = 77200 => S = 182000.',
             2, None),

            (17, 'Планиметрия (Часть 2)',
             'В трапеции ABCD биссектрисы углов A и B пересекаются в точке M, лежащей на стороне CD.\nа) Докажите, что AB = AD + BC.\nб) Найдите площадь трапеции, если AB = 10, а высота h = 6.',
             'a) Доказано; б) 30',
             'а) Средняя линия через M равна AB/2 = (AD + BC)/2 => AB = AD + BC.\nб) S = ((AD + BC)/2) * h = (10/2) * 6 = 30.',
             2, '/static/images/task_17.png'),

            (18, 'Задачи с параметром (Часть 2)',
             'Найдите все значения параметра a, при каждом из которых система имеет ровно 2 решения:\n{ x² + y² = 1\n{ y = ax + 2',
             'a ∈ (-∞; -√3) ∪ (√3; +∞)',
             'Расстояние от (0,0) до прямой меньше радиуса 1: 2 / √(a² + 1) < 1 => a² > 3.',
             2, None),

            (19, 'Числа и их свойства (Часть 2)',
             'Дано множество из 10 различных натуральных чисел.\nа) Может ли сумма всех чисел быть равна 56?\nб) Какое максимальное значение S может принимать сумма всех чисел, если их среднее арифметическое — целое число, не превосходящее 12?',
             'a) Да; б) 120',
             'а) Пример: 1+2+3+4+5+6+7+8+9+11 = 56.\nб) S = 10 * M ≤ 120; достигается, например, при 3,4,5,6,7,8,9,10,11,57.',
             2, None)
        ]

        cursor.executemany('''
            INSERT INTO tasks (task_number, topic, text, answer, explanation, part, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_tasks)
        conn.commit()

    conn.close()


import os
from werkzeug.utils import secure_filename

# Указываем папку для загрузки файлов
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        task_number = int(request.form['task_number'])
        topic = request.form['topic']
        text = request.form['text']
        answer = request.form['answer']
        explanation = request.form['explanation']
        part = 1 if task_number <= 13 else 2

        # Обработка загружаемого изображения
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Сохраняем файл в static/images
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                image_url = f'/{app.config["UPLOAD_FOLDER"]}/{filename}'

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (task_number, topic, text, answer, explanation, part, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (task_number, topic, text, answer, explanation, part, image_url))
        conn.commit()
        conn.close()
        return redirect(url_for('add_task'))

    return render_template('add_task.html')


@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Загрузка истории решений
    cursor.execute('SELECT * FROM history ORDER BY id DESC LIMIT 10')
    history_list = [dict(row) for row in cursor.fetchall()]

    # 2. Общая статистика
    cursor.execute('SELECT COUNT(*), AVG(percent) FROM history')
    stats = cursor.fetchone()
    total_tests = stats[0] or 0
    avg_percent = round(stats[1]) if stats[1] else 0

    # 3. АНАЛИЗАТОР СЛАБЫХ МЕСТ и ДАННЫЕ ДЛЯ ГРАФА ZNANIY
    cursor.execute('''
        SELECT topic, 
               COUNT(*) as total_attempts,
               SUM(is_correct) as correct_attempts,
               ROUND(CAST(SUM(is_correct) AS FLOAT) / COUNT(*) * 100) as accuracy
        FROM task_history 
        GROUP BY topic
    ''')
    topic_stats = [dict(row) for row in cursor.fetchall()]

    # Ищем худшие темы (точность < 60%)
    weak_topics = [t for t in topic_stats if t['accuracy'] < 60]

    conn.close()
    return render_template(
        'index.html',
        history=history_list,
        total_tests=total_tests,
        avg_percent=avg_percent,
        topic_stats=topic_stats,
        weak_topics=weak_topics
    )


import os


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    mode = request.form.get('mode', 'full') if request.method == 'POST' else request.args.get('mode', 'full')
    conn = get_db()
    cursor = conn.cursor()
    variant_tasks = []

    if mode == 'part1':
        for num in range(1, 13):  # Задания 1–12
            cursor.execute('''
                SELECT * FROM tasks 
                WHERE task_number = ? AND part = 1 
                ORDER BY RANDOM() LIMIT 1
            ''', (num,))
            row = cursor.fetchone()
            if row:
                variant_tasks.append(dict(row))

    elif mode == 'full':
        for num in range(1, 20):  # Задания 1–19
            part = 1 if num <= 12 else 2
            cursor.execute('''
                SELECT * FROM tasks 
                WHERE task_number = ? AND part = ? 
                ORDER BY RANDOM() LIMIT 1
            ''', (num, part))
            row = cursor.fetchone()
            if row:
                variant_tasks.append(dict(row))

    elif mode == 'weak_spots':
        cursor.execute('''
            SELECT topic FROM task_history 
            WHERE is_correct = 0 
            GROUP BY topic 
            ORDER BY COUNT(*) DESC LIMIT 5
        ''')
        weak_topics = [r[0] for r in cursor.fetchall()]

        if weak_topics:
            for topic in weak_topics:
                cursor.execute('SELECT * FROM tasks WHERE topic = ? ORDER BY RANDOM() LIMIT 1', (topic,))
                row = cursor.fetchone()
                if row:
                    variant_tasks.append(dict(row))
        else:
            cursor.execute('SELECT * FROM tasks ORDER BY RANDOM() LIMIT 5')
            variant_tasks = [dict(r) for r in cursor.fetchall()]

    for task in variant_tasks:
        if task.get('image_url'):
            abs_img = os.path.join(BASE_DIR, task['image_url'].lstrip('/'))
            if not os.path.exists(abs_img):
                task['image_url'] = None

    conn.close()
    return render_template('exam.html', tasks=variant_tasks, mode=mode)

import os
import random
@app.route('/exam')
def exam():
    mode = request.args.get('mode', 'part1')  # part1, full, weak_spots
    conn = get_db()
    cursor = conn.cursor()

    variant_tasks = []

    if mode == 'part1':
        # Выбираем случайную задачу для каждого номера Части 1 (с №1 по №13)
        for num in range(1, 14):
            cursor.execute('''
                SELECT * FROM tasks 
                WHERE task_number = ? AND part = 1 
                ORDER BY RANDOM() LIMIT 1
            ''', (num,))
            row = cursor.fetchone()
            if row:
                variant_tasks.append(dict(row))

    elif mode == 'full':
        # Выбираем случайную задачу для ВСЕХ номеров (с №1 по №20)
        for num in range(1, 21):
            part = 1 if num <= 13 else 2
            cursor.execute('''
                SELECT * FROM tasks 
                WHERE task_number = ? AND part = ? 
                ORDER BY RANDOM() LIMIT 1
            ''', (num, part))
            row = cursor.fetchone()
            if row:
                variant_tasks.append(dict(row))

    elif mode == 'weak_spots':
        # Пример: 5 случайных задач из тех тем, где больше всего ошибок
        cursor.execute('''
            SELECT topic FROM task_history 
            WHERE is_correct = 0 
            GROUP BY topic 
            ORDER BY COUNT(*) DESC LIMIT 5
        ''')
        weak_topics = [r[0] for r in cursor.fetchall()]

        if weak_topics:
            for topic in weak_topics:
                cursor.execute('SELECT * FROM tasks WHERE topic = ? ORDER BY RANDOM() LIMIT 1', (topic,))
                row = cursor.fetchone()
                if row:
                    variant_tasks.append(dict(row))
        else:
            # Если истории еще нет — просто берем 5 случайных задач
            cursor.execute('SELECT * FROM tasks ORDER BY RANDOM() LIMIT 5')
            variant_tasks = [dict(r) for r in cursor.fetchall()]

    # Проверка на физическое существование картинок (чтобы не было битых иконок)
    for task in variant_tasks:
        if task.get('image_url'):
            rel_path = task['image_url'].lstrip('/')
            if not os.path.exists(rel_path):
                task['image_url'] = None

    conn.close()
    return render_template('exam.html', tasks=variant_tasks, mode=mode)


@app.route('/bank')
def bank():
    selected_num = request.args.get('task_number', type=int)
    conn = get_db()
    cursor = conn.cursor()

    if selected_num:
        cursor.execute('SELECT * FROM tasks WHERE task_number = ? ORDER BY id DESC', (selected_num,))
    else:
        cursor.execute('SELECT * FROM tasks ORDER BY task_number ASC, id DESC')

    tasks = [dict(r) for r in cursor.fetchall()]

    # Статистика: сколько всего задач в банке
    cursor.execute('SELECT COUNT(*) FROM tasks')
    total_count = cursor.fetchone()[0]

    conn.close()
    return render_template('bank.html', tasks=tasks, selected_num=selected_num, total_count=total_count)


@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('bank'))


@app.route('/check', methods=['POST'])
def check():
    mode = request.form.get('mode', 'part1')

    conn = get_db()
    cursor = conn.cursor()

    score = 0
    total = 0
    results = []

    # Проходим по всем переданным ответам из формы
    for key, user_ans in request.form.items():
        if key.startswith('answer_'):
            task_id = int(key.split('_')[1])
            cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            task = dict(cursor.fetchone())

            total += 1
            user_clean = user_ans.strip().replace(' ', '').replace(',', '.').lower()
            correct_clean = task['answer'].strip().replace(' ', '').replace(',', '.').lower()

            is_correct = (user_clean == correct_clean) if user_clean else False
            if is_correct:
                score += 1

            # Сохраняем результат для таблицы
            results.append({
                'task_number': len(results) + 1,
                'orig_number': task['task_number'],
                'topic': task['topic'],
                'text': task['text'],
                'user_answer': user_ans if user_ans.strip() else "—",
                'correct_answer': task['answer'],
                'is_correct': is_correct,
                'explanation': task['explanation'],
                'image_url': task['image_url']
            })

            # Фиксируем попытку в аналитике по темам
            cursor.execute(
                'INSERT INTO task_history (topic, is_correct, date) VALUES (?, ?, DATE("now"))',
                (task['topic'], 1 if is_correct else 0)
            )

    percent = int((score / total) * 100) if total > 0 else 0

    # Записываем общую историю в БД
    cursor.execute(
        'INSERT INTO history (date, mode_name, score, total, percent) VALUES (DATETIME("now"), ?, ?, ?, ?)',
        (mode, score, total, percent)
    )
    conn.commit()
    conn.close()

    return render_template('result.html', score=score, total=total, percent=percent, results=results)


init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)


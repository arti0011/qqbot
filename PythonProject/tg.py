import telebot
from telebot import types
import sqlite3

API_TOKEN = '7474038419:AAG5ev6CG133HVGWA-ebpsB42YSunM1Dxs0'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_PASSWORD = '11111111'


# Функция для подключения к базе данных
def db_connect():
    return sqlite3.connect('employees.db')


# Создание базы данных и таблиц
def create_db():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            contact_info TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hr_contacts (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee_efficiency (
            employee_id INTEGER,
            tasks_completed INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    ''')
    conn.commit()
    conn.close()


create_db()


# Главное меню
def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Получить список сотрудников")
    item2 = types.KeyboardButton("Информация о компании")
    item3 = types.KeyboardButton("Контакты HR")
    item4 = types.KeyboardButton("Панель администратора")
    item5 = types.KeyboardButton("Эффективность сотрудников")

    markup.add(item1, item2, item3, item4, item5)

    bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)


# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    username = message.from_user.first_name  # Получаем имя пользователя
    bot.send_message(message.chat.id, f"Привет, {username}!Это бот Цаги для помощи)")
    main_menu(message)


# Команда для получения списка сотрудников
def get_employees(message):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    conn.close()

    if employees:
        response = "\n".join([f"{emp[0]}: {emp[1]}, {emp[2]}, {emp[3]}" for emp in employees])
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Нет сотрудников в базе данных.")

    main_menu(message)


# Информация о компании
def company_info(message):
    info = ("Информация о компании:\n\n"
            "Акционерное общество «ЦАГИ-системы моделирования» осуществляет свою деятельность в рамках стратегии развития информационного общества Российской Федерации "
            "Мы стремимся к инновациям и качеству в каждой из наших проектов.")

    bot.send_message(message.chat.id, info)
    main_menu(message)


# Контакты HR
def hr_contacts(message):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hr_contacts")
    hr_contacts_list = cursor.fetchall()
    conn.close()

    if hr_contacts_list:
        response = "\n".join([f"{hr[0]}: {hr[1]}, Телефон: {hr[2]}, Email: {hr[3]}" for hr in hr_contacts_list])
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Нет информации о HR.")

    main_menu(message)


# Проверка пароля для доступа к админ-панели
def admin_password_check(message):
    msg = bot.send_message(message.chat.id, "Введите пароль для доступа к панели администратора:")
    bot.register_next_step_handler(msg, verify_admin_password)


def verify_admin_password(message):
    if message.text == ADMIN_PASSWORD:
        admin_panel(message)
    else:
        bot.send_message(message.chat.id, "Неверный пароль. Попробуйте еще раз.")
        main_menu(message)

# Панель администратора
def admin_panel(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Добавить сотрудника")
    item2 = types.KeyboardButton("Добавить контакт HR")
    item3 = types.KeyboardButton("Добавить эффективность сотрудника")
    item4 = types.KeyboardButton("Назад")  # Кнопка "Назад"

    markup.add(item1, item2, item3, item4)

    bot.send_message(message.chat.id, "Панель администратора:", reply_markup=markup)


# Команда для добавления сотрудника
def add_employee(message):
    msg = bot.send_message(message.chat.id, "Введите имя сотрудника:")
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    name = message.text
    msg = bot.send_message(message.chat.id, "Введите должность:")
    bot.register_next_step_handler(msg, process_position_step, name)


def process_position_step(message, name):
    position = message.text
    msg = bot.send_message(message.chat.id, "Введите контактную информацию:")
    bot.register_next_step_handler(msg, process_contact_step, name, position)


def process_contact_step(message, name, position):
    contact_info = message.text
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO employees (name, position, contact_info) VALUES (?, ?, ?)",
                   (name, position, contact_info))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"Сотрудник {name} успешно добавлен!")
    main_menu(message)


# Команда для добавления контакта HR
def add_hr_contact(message):
    msg = bot.send_message(message.chat.id, "Введите имя HR:")
    bot.register_next_step_handler(msg, process_hr_name_step)


def process_hr_name_step(message):
    name = message.text
    msg = bot.send_message(message.chat.id, "Введите телефон:")
    bot.register_next_step_handler(msg, process_hr_phone_step, name)


def process_hr_phone_step(message, name):
    phone = message.text
    msg = bot.send_message(message.chat.id, "Введите email:")
    bot.register_next_step_handler(msg, process_hr_email_step, name, phone)


def process_hr_email_step(message, name, phone):
    email = message.text
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO hr_contacts (name, phone, email) VALUES (?, ?, ?)",
                   (name, phone, email))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"Контакт HR {name} успешно добавлен!")
    main_menu(message)


# Команда для добавления эффективности сотрудника
def add_employee_efficiency(message):
    conn = db_connect()
    cursor = conn.cursor()

    # Получаем список сотрудников для отображения
    cursor.execute("SELECT id, name FROM employees")
    employees = cursor.fetchall()

    if employees:
        response = "\n".join([f"{emp[0]}: {emp[1]}" for emp in employees])
        msg = bot.send_message(
            message.chat.id,
            f"Выберите сотрудника по ID:\n{response}"
        )
        bot.register_next_step_handler(msg, process_efficiency_id)

    else:
        bot.send_message(message.chat.id, "Нет сотрудников для обновления эффективности.")

    conn.close()


def process_efficiency_id(message):
    employee_id = message.text
    msg = bot.send_message(message.chat.id, "Введите количество выполненных заданий:")
    bot.register_next_step_handler(msg, process_efficiency_tasks_completed, employee_id)


def process_efficiency_tasks_completed(message, employee_id):
    tasks_completed = message.text
    conn = db_connect()
    cursor = conn.cursor()

    # Удаляем старую запись об эффективности сотрудника (если существует)
    cursor.execute("DELETE FROM employee_efficiency WHERE employee_id=?", (employee_id,))

    # Проверка существования сотрудника перед добавлением эффективности
    cursor.execute("SELECT * FROM employees WHERE id=?", (employee_id,))

    if cursor.fetchone():
        cursor.execute("INSERT INTO employee_efficiency (employee_id, tasks_completed) VALUES (?, ?)",
                       (employee_id, tasks_completed))
        conn.commit()
        bot.send_message(message.chat.id, f"Эффективность сотрудника с ID {employee_id} успешно обновлена!")
    else:
        bot.send_message(message.chat.id, f"Сотрудник с ID {employee_id} не найден.")

    conn.close()
    main_menu(message)


# Команда для отображения эффективности сотрудников
def show_employee_efficiency(message):
    conn = db_connect()
    cursor = conn.cursor()

    cursor.execute('''
                SELECT e.name, e.position, ee.tasks_completed 
                FROM employees e 
                JOIN employee_efficiency ee ON e.id = ee.employee_id
            ''')

    efficiencies = cursor.fetchall()

    if efficiencies:
        response = "\n".join([f"{eff[0]} ({eff[1]}): Выполнено заданий - {eff[2]}" for eff in efficiencies])
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Нет информации об эффективности сотрудников.")

    conn.close()
    main_menu(message)


# Обработка действий в админ-меню и главном меню
@bot.message_handler(func=lambda message: True)
def handle_actions(message):
    if message.text == "Получить список сотрудников":
        get_employees(message)

    elif message.text == "Информация о компании":
        company_info(message)

    elif message.text == "Контакты HR":
        hr_contacts(message)

    elif message.text == "Панель администратора":
        admin_password_check(message)  # Запрос пароля для доступа к админ-панели

    elif message.text == "Добавить сотрудника":
        add_employee(message)

    elif message.text == "Добавить контакт HR":
        add_hr_contact(message)

    elif message.text == "Добавить эффективность сотрудника":
        add_employee_efficiency(message)

    elif message.text == "Эффективность сотрудников":
        show_employee_efficiency(message)

        # Обработка нажатия кнопки "Назад"
    elif message.text == "Назад":
        main_menu(message)


# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)

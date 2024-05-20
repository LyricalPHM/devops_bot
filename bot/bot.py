import paramiko
import os
import re
import logging
import psycopg2
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from psycopg2 import Error
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

# Настройка логирования
logging.basicConfig(filename='bot.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Обработчик команды /start
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(f'Добро пожаловать {user.full_name}! Этот бот, может помочь Вам с выполнением различных задач. '
                              'Введите /help, чтобы увидеть доступные команды и их описание.')

# Обработчик команды /help
def help(update: Update, context: CallbackContext):
    update.message.reply_text('/find_email - поиск email-адресов в тексте\n'
                              '/findPhoneNumbers - поиск номеров телефонов в тексте\n'
                              '/verify_password - проверка сложности пароля\n'
                              '/get_release - получение информации о релизе системы\n'
                              '/get_uname - получение информации об архитектуре процессора, имени хоста и версии ядра\n'
                              '/get_uptime - получение информации о времени работы\n'
                              '/get_df - получение информации о состоянии файловой системы\n'
                              '/get_free - получение информации о состоянии оперативной памяти\n'
                              '/get_mpstat - получение информации о производительности системы\n'
                              '/get_w - получение информации о пользователях\n'
                              '/get_auths - получение данных о последних входах в систему\n'
                              '/get_critical - получение данных о последних критических событиях\n'
                              '/get_ps - получение информации о запущенных процессах\n'
                              '/get_ss - получение информации об используемых портах\n'
                              '/get_apt_list - получение информации об установленных пакетах\n'
                              '/get_apt_input - получение информации об определенном пакете\n'
                              '/get_services - получение информации о запущенных сервисах\n'
                              '/get_repl_logs_DOCKER - вывод логов о репликации базы данных в контейнере\n'
                              '/get_repl_logs_ANSIBLE - вывод логов о репликации базы данных развернутой через Ansible\n'
                              '/get_emails - вывод email адресов из базы данных\n'
                              '/get_phone_numbers - вывод телефонных номеров из базы данных\n')

# Функции для поиска email-адресов в тексте
def findEmailAddressesCommand(update: Update, context: CallbackContext):
    update.message.reply_text('Введите текст для поиска email адресов: ')
    return 'find_email'

def find_email(update: Update, context: CallbackContext):
    user_input = update.message.text  
    emailRegex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    emailAddressList = emailRegex.findall(user_input)  
    if not emailAddressList:  
        update.message.reply_text('Email адреса не найдены.')
        return ConversationHandler.END  
    emailAddresses = []  
    for email in emailAddressList:
        emailAddresses.append(email)  
    update.message.reply_text('\n'.join(emailAddresses))  
    context.user_data['email_addresses'] = emailAddresses  

    # Предлагаем записать email адреса в базу данных
    keyboard = [['Да', 'Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('Хотите записать найденные email адреса в базу данных?', reply_markup=reply_markup)
    return 'confirm_email'


def confirm_email(update: Update, context: CallbackContext):
    user_choice = update.message.text
    if user_choice == 'Да':
        try:
            email_addresses = context.user_data.get('email_addresses')
            if email_addresses is not None:
                connection = None
                try:
                    connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                                  password=os.getenv('DB_PASSWORD'),
                                                  host=os.getenv('DB_HOST'),
                                                  port=os.getenv('DB_PORT'),
                                                  database=os.getenv('DB_DATABASE'))
                    cursor = connection.cursor()
                    for email_address in email_addresses:
                        cursor.execute("INSERT INTO email (email) VALUES (%s);", (email_address,))
                    connection.commit()
                    update.message.reply_text('Email адреса успешно записаны в базу данных.')
                    logging.info("Команда успешно выполнена.")
                except (Exception, Error) as error:
                    logging.error("Ошибка при работе с PostgreSQL: %s", error)
                    update.message.reply_text("Произошла ошибка при выполнении команды.")
                finally:
                    if connection is not None:
                        cursor.close()
                        connection.close()
                        logging.info("Соединение с PostgreSQL закрыто.")
            else:
                update.message.reply_text('Отсутствуют email адреса для записи.')
        except Exception as e:
            update.message.reply_text(f'Произошла ошибка при записи в базу данных: {str(e)}')
    elif user_choice == 'Нет':
        update.message.reply_text(' Email адреса не будут записаны в базу данных.')
    else:
        update.message.reply_text('Выберите один из вариантов: Да или Нет.')
    return ConversationHandler.END


def send_repl_log(update, context):
    log_file_path = '/var/log/repl.log'
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as file:
            lines = file.readlines()
        filtered_lines = [line.strip() for line in lines if "repl" in line]
        last_15_lines = filtered_lines[-15:]
        log_content = '\n'.join(last_15_lines)
        if log_content:
            update.message.reply_text(log_content)
        else:
            update.message.reply_text("Логи репликации не найдены")
    else:
        update.message.reply_text("Файл журнала не найден.")


# Функции для поиска номеров телефонов в тексте
def findPhoneNumbersCommand(update: Update, context: CallbackContext):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'findPhoneNumbers'


def findPhoneNumbers(update: Update, context: CallbackContext):
    user_input = update.message.text  
    phoneNumRegex = re.compile(r'(?:\+7|8)(?: \(\d{3}\) \d{3}-\d{2}-\d{2}|\d{10}|\(\d{3}\)\d{7}| \d{3} \d{3} \d{2} \d{2}| \(\d{3}\) \d{3} \d{2} \d{2}|-\d{3}-\d{3}-\d{2}-\d{2})')
    phoneNumberList = phoneNumRegex.findall(user_input)  
    if not phoneNumberList: 
        update.message.reply_text('Телефонные номера не найдены.')
        return ConversationHandler.END  
    phoneNumbers = []  
    for phone in phoneNumberList:
        formatted_phone = ''.join([part for part in phone if part and part.strip()])  
        phoneNumbers.append(formatted_phone)  
    update.message.reply_text('\n'.join(phoneNumbers))  
    context.user_data['phone_numbers'] = phoneNumbers  
    keyboard = [['Да', 'Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('Хотите записать найденные номера телефонов в базу данных?', reply_markup=reply_markup)
    return 'confirm_phone'


#Функция записи найденного номера в базу данных
def normalize_phone(phone_number):
    cleaned_number = re.sub(r'[-\s]', '', phone_number)
    cleaned_number = re.sub(r'\D', '', cleaned_number)
    if cleaned_number.startswith('8'):
        cleaned_number = '+7' + cleaned_number[1:]
    elif cleaned_number.startswith('7'):
        cleaned_number = '+' + cleaned_number
    return cleaned_number

def confirm_phone(update: Update, context: CallbackContext):
    user_choice = update.message.text
    if user_choice == 'Да':
        try:
            phone_numbers = context.user_data.get('phone_numbers')
            if phone_numbers is not None:
                connection = None
                try:
                    connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                                  password=os.getenv('DB_PASSWORD'),
                                                  host=os.getenv('DB_HOST'),
                                                  port=os.getenv('DB_PORT'),
                                                  database=os.getenv('DB_DATABASE'))
                    cursor = connection.cursor()
                    for phone_number in phone_numbers:
                        normalized_number = normalize_phone(phone_number)
                        cursor.execute("INSERT INTO phone (phone_number) VALUES (%s);", (normalized_number,))
                    connection.commit()
                    update.message.reply_text('Номера телефонов успешно записаны в базу данных.')
                    logging.info("Команда успешно выполнена.")
                except (Exception, Error) as error:
                    logging.error("Ошибка при работе с PostgreSQL: %s", error)
                    update.message.reply_text("Произошла ошибка при выполнении команды.")
                finally:
                    if connection is not None:
                        cursor.close()
                        connection.close()
                        logging.info("Соединение с PostgreSQL закрыто")
            else:
                update.message.reply_text('Нет номеров телефонов для записи.')
        except Exception as e:
            update.message.reply_text(f'Произошла ошибка при записи в базу данных: {str(e)}')
    elif user_choice == 'Нет':
        update.message.reply_text('Номера телефонов не будут записаны в базу данных.')
    else:
        update.message.reply_text('Пожалуйста, выберите один из вариантов: Да или Нет.')
    return ConversationHandler.END






# Функции для проверки сложности пароля
def verifyPasswordCommand(update: Update, context: CallbackContext):
    update.message.reply_text('Введите пароль для проверки сложности: ')
    return 'verify_password'

def verify_password(update: Update, context: CallbackContext):
    user_input = update.message.text  
    passwordRegex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()])[A-Za-z\d!@#$%^&*()]{8,}$')
    if passwordRegex.match(user_input):  
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')
    return ConversationHandler.END  

# Функции для получения информации о системе
def run_command_on_server(command):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    return str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

def execute_command(update: Update, context: CallbackContext):
    command = update.message.text.split()[0].split('/')[-1]  
    commands_map = {
        'get_release': 'lsb_release -d',
        'get_uname': 'uname -a',
        'get_uptime': 'uptime',
        'get_df': 'df -h',
        'get_free': 'free -m',
        'get_mpstat': 'mpstat',
        'get_w': 'w',
        'get_auths': 'last -10',
        'get_critical': 'tail -n 15 /var/log/syslog | grep "CRITICAL"',
        'get_ps': 'ps aux | head -n 15',
        'get_ss': 'ss -tuln',
        'get_apt_list': 'apt list --installed| head -n 15',
        'get_services': 'systemctl list-units --type=service | grep running | head -n 15',
        'get_repl_logs_ANSIBLE': 'tail -n 15 /var/log/postgresql/postgresql-15-main.log'
    }

    if command in commands_map:
        data = run_command_on_server(commands_map[command])
        update.message.reply_text(f'Результат выполнения команды {command}:\n{data}')
        return ConversationHandler.END
    else:
        update.message.reply_text('Неверная команда')
        return ConversationHandler.END

def getAptPackageCommand(update: Update, context: CallbackContext):
    update.message.reply_text("Введите название пакета:")
    return 'get_apt_input'

def get_apt_input(update: Update, context: CallbackContext):
    package_name = update.message.text.strip()
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    command = f'apt show {package_name}'
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(f'Информация о пакете {package_name}:\n{data}')
    return ConversationHandler.END



#Функция для работы с выводом информации из базы данных
def get_from_db(update: Update, context: CallbackContext):
    try:
        command = update.message.text.split('/')[-1]

        commands_map = {
            'get_emails': ('SELECT * FROM email', 'почтовых адресов'),
            'get_phone_numbers': ('SELECT * FROM phone', 'номеров телефонов')
        }
        if command in commands_map:
            connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                          password=os.getenv('DB_PASSWORD'),
                                          host=os.getenv('DB_HOST'),
                                          port=os.getenv('DB_PORT'),
                                          database=os.getenv('DB_DATABASE'))
            cursor = connection.cursor()
            cursor.execute(commands_map[command][0])
            data = cursor.fetchall()
            items = ""
            for row in data:
                items += str(row) + "\n"
            if items:
                update.message.reply_text(f'Список {commands_map[command][1]} из базы данных:\n{items}')
            else:
                update.message.reply_text(f'База данных не содержит {commands_map[command][1]}.')
            logging.info("Команда успешно выполнена")
        else:
            update.message.reply_text("Неверная команда.")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        update.message.reply_text("Произошла ошибка при выполнении команды.")
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Обработчик диалога номеров телефонов
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('findPhoneNumbers', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'confirm_phone': [MessageHandler(Filters.text & ~Filters.command, confirm_phone)],
        },
        fallbacks=[]
    )

    # Обработчик диалога email адресов
    convHandlerFindEmailAddresses = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailAddressesCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'confirm_email': [MessageHandler(Filters.text & ~Filters.command, confirm_email)],
        },
        fallbacks=[]
    )

    # Обработчик диалога для проверки сложности пароля
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

    convHandlerGetAptInput = ConversationHandler(
        entry_points=[CommandHandler('get_apt_input', getAptPackageCommand)],
        states={
            'get_apt_input': [MessageHandler(Filters.text & ~Filters.command, get_apt_input)],
        },
        fallbacks=[]
    )

    dispatcher.add_handler(CommandHandler("get_repl_logs_DOCKER", send_repl_log))
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(convHandlerFindEmailAddresses)
    dispatcher.add_handler(convHandlerGetAptInput)
    dispatcher.add_handler(convHandlerFindPhoneNumbers)
    dispatcher.add_handler(convHandlerVerifyPassword)
    dispatcher.add_handler(CommandHandler(['get_release', 'get_uname', 'get_uptime', 'get_df', 'get_free',
                                           'get_mpstat', 'get_w', 'get_auths', 'get_critical', 'get_ps',
                                           'get_ss', 'get_apt_list', 'get_services', 'get_repl_logs_ANSIBLE'], execute_command))
    dispatcher.add_handler(CommandHandler(['get_emails', 'get_phone_numbers'], get_from_db))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()


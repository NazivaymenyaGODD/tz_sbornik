import telebot
import psycopg2


key = '6135998307:AAEgWvCTm3gmu5VgGdHKRidfQhOTLthmqRQ'
bot = telebot.TeleBot(key)
conn = psycopg2.connect(dbname="postgres", 
                        user="postgres", 
                        password="123", 
                        host="127.0.0.1", 
                        port = "5432")
cursor = conn.cursor()
conn.autocommit = True
# # #Создал БД

cursor.execute(
            """CREATE TABLE member(
                    id varchar(30),
                   complex varchar(50),
                    subject varchar(80),
                    step1 int
                  )"""
               )

@bot.message_handler(commands=['start'])
def start_message(message):
    print(message.chat.username)
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Выбрать сложность задач','Выбрать тематику задач', 'Получить задания')
    bot.send_message(message.chat.id, "Привет, я сборник задач. Первым делом выбирайте сложность и тематику задачи, потом вы можете получить задачи.", reply_markup=keyboard)
    
@bot.message_handler(content_types=['text'])
def send_text(message):
    if message:
        cursor.execute("SELECT id FROM member")
        data = cursor.fetchall()
        check = 0
        for i in range(len(data)):
            if data[i][0] == str(message.chat.id):
                check = 1
        if  check == 0: cursor.execute("INSERT INTO member (id, step1) VALUES(%s, 0);", [message.chat.id])

    if message.text == 'Выбрать сложность задач':
        cursor.execute("""SELECT DISTINCT complexity FROM task""")
        data = cursor.fetchall()
        text = 'Cложности: \n'
        for i in range(len(data)):
            text = text + str(data[i][0] + '\n')
        text = text + 'Введите сложность:'
        bot.send_message(message.chat.id, text)
        cursor.execute("UPDATE member SET step1 = 1 WHERE id = %s;", [str(message.chat.id)])

    
    if message.text == 'Выбрать тематику задач':
        cursor.execute("""SELECT s1 FROM subject
                            UNION
                            SELECT s2 FROM subject
                            UNION
                            SELECT s3 FROM subject
                            UNION
                            SELECT s4 FROM subject """)
        data = cursor.fetchall()
        text = 'Тематики: \n'
        for i in range(len(data)):
            text = text + str(data[i][0] + '\n')
        text = text + 'Введите тематику:'
        bot.send_message(message.chat.id, text)
        cursor.execute("UPDATE member SET step1 = 2 WHERE id = %s;", [str(message.chat.id)])
        
    if message.text != 'Выбрать тематику задач' and message.text != 'Выбрать сложность задач':
        cursor.execute("SELECT step1 FROM member WHERE id = %s;", [str(message.chat.id)])
        data = cursor.fetchall()
        if data[0][0] == 1:
            cursor.execute("""SELECT DISTINCT complexity FROM task""")
            data = cursor.fetchall()
            check = 0
            for i in range(len(data)):
                if data[i][0] == message.text:
                    check = 1
            if check == 1:
                cursor.execute("UPDATE member SET step1 = 0 WHERE id = %s;", [str(message.chat.id)])
                cursor.execute("UPDATE member SET complex = %s WHERE id = %s;", [message.text, str(message.chat.id)])
            if check == 0:
                bot.send_message(message.chat.id, "Такой сложности нету. Попробуйте снова")
        
        if data[0][0] == 2:
            cursor.execute("""SELECT s1 FROM subject
                            UNION
                            SELECT s2 FROM subject
                            UNION
                            SELECT s3 FROM subject
                            UNION
                            SELECT s4 FROM subject """)
            data = cursor.fetchall()
            check = 0
            for i in range(len(data)):
                if data[i][0] == message.text:
                    check = 1
            if check == 1:
                cursor.execute("UPDATE member SET step1 = 0 WHERE id = %s;", [str(message.chat.id)])
                cursor.execute("UPDATE member SET subject = %s WHERE id = %s;", [message.text, str(message.chat.id)])
            if check == 0:
                bot.send_message(message.chat.id, "Такой тематики нету. Попробуйте снова")        
        if message.text == 'Получить задания':
            cursor.execute("SELECT complex FROM member WHERE id = %s;", [str(message.chat.id)])
            data = cursor.fetchall()
            cursor.execute("SELECT subject FROM member WHERE id = %s;", [str(message.chat.id)])
            data2 = cursor.fetchall()
            if data[0][0] and data2[0][0]:
                cursor.execute("""
                SELECT DISTINCT id, name, href FROM task WHERE 
                    id in (SELECT id FROM subject WHERE
                    s1 = %s or s2 = %s
                    or s3 = %s or s4 = %s)
                    and complexity = %s LIMIT 10;""", [data2[0][0], data2[0][0],data2[0][0],data2[0][0],data[0][0]])
                data = cursor.fetchall()
                text = ''
                for i in range(len(data)):
                    text = text +  data[i][0] + "/" + data[i][1] + ". https://codeforces.com/" + data[i][2] + '\n'
                if text != '':
                    bot.send_message(message.chat.id, text)
                else:
                    bot.send_message(message.chat.id, 'такой подборки не нашлось')
            else:
                bot.send_message(message.chat.id, "Не выбрано сложность или тематика задачи.")


bot.polling()

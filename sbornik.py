import requests
import psycopg2
from bs4 import BeautifulSoup as BS
import time



conn = psycopg2.connect(dbname="postgres", 
                        user="postgres", 
                        password="123", 
                        host="127.0.0.1", 
                        port = "5432")
conn.autocommit = True
cursor = conn.cursor()

# #  #  # #Создал БД
# cursor.execute(
#                 """CREATE TABLE task(
#                        id varchar(10),
#                        name varchar(100),
#                        quantity varchar(30),
#                        complexity varchar(30),
#                        href varchar(100)
#                 )"""
#           )
# cursor.execute(
#          """CREATE TABLE subject(
#                          id varchar(10),
#                          s1 varchar(50),
#                          s2 varchar(50),
#                          s3 varchar(50),
#                        s4 varchar(50)
#                 )"""
#    )

while True:
    if time.localtime(time.time()).tm_min == 56 and time.localtime(time.time()).tm_sec == 30:
        my_list = []
        rating = None
        subject = []
        cursor.execute("""SELECT id FROM task""")
        data = cursor.fetchall()
        for k in range(10): # только 10 страиниц взял
            r = requests.post('https://codeforces.com/problemset/page/' + str(k + 1) + '?order=BY_SOLVED_DESC&locale=ru')
            html = BS(r.content, 'html.parser')
            for el in html.select(".problems"):
                for el in html.select("tr"):
                    subject = []
                    my_list = []
                    my_href = []
                    for elik in el.select('a'):
                        info = elik.text
                        info = info.strip()
                        my_list.append(info)
                        in_href = elik.get('href')
                        my_href.append(in_href)
                    for elik in el.select('.ProblemRating'):
                        rating = elik.text
                    j = 0
                    for i in range(len(my_list) - 1):
                        if i > 1 and my_list[i]: 
                            subject.append(my_list[i])
                    subject.append('')
                    subject.append('')
                    subject.append('')
                    
                    if my_list and my_list[0]:
                        check = 0
                        for i in range(len(data)):
                            if my_list[0] == data[i][0]:
                                check = 1
                        if check == 0:
                            cursor.execute("INSERT INTO task (id, name,  quantity, complexity, href) VALUES(%s, %s, %s, %s, %s);", [my_list[0], my_list[1], my_list[-1], rating, my_href[0]])
                            cursor.execute("INSERT INTO subject(id, s1, s2, s3, s4) VALUES(%s, %s, %s, %s, %s);", [my_list[0], subject[0], subject[1], subject[2], subject[3]])
            print('Страница - ', k + 1)
                    
                
"""
Модуль для работы с локальной базой данных по памятным и инвестиционным монетам
"""
import requests
import sqlite3
import os
from datetime import datetime
import coins_web as cw


class Coin_db:
    """
    Класс для работы с локальной базой данных
    """
    quality_inf = {0: 'пруф', 1:'АЦ', 2:'БА', 3:'пруф-лайк'}
    
    def __init__(self, db_path='coin.db'):
        self.__db_path = db_path
        self.names = {
            'autors': 'авторы', 
            'avers': 'аверс', 
            'revers': 'реверс', 
            'begindate': 'дата выпуска', 
            'cat_num': 'каталожный номер', 
            'comment': 'справка', 
            'prefix': 'префикс', 
            'sname': 'название серии', 
            'nc_mintage': 'тираж может меняться', 
            'mintage': 'тираж, шт.', 
            'quality': 'качество', 
            'weigth': 'масса общая, г.', 
            'sq_lenght': 'длина', 
            'sq_width': 'ширина', 
            'thickness': 'толщина, мм', 
            'diametr': 'диаметр, мм', 
            'finemetall': 'содержание химически чистого металла не менее, г', 
            'history_note': 'историко-тематическая справка', 
            'cname': 'название рус.', 
            'nominal': 'код номинала', 
            'nname': 'номинал (рус)', 
            'mname': 'металл (рус)', 
            'tname': 'тип металла (рус)'
            }
        try:
            self.connection = sqlite3.connect(f'file:{self.__db_path}?mode=rw', uri=True)
            self.cursor = self.connection.cursor()
            self.err = f'{self.__db_path} connection successful'
        except sqlite3.Error as error:
            self.err = f'{error} (default {self.__db_path})'
                        
    def check_kn(self, g=str(datetime.now().year)):
        """
        Метод проверяет локальную БД с БД crb.ru по году 
        и добавляет недостающие записи
        """
        cat_num_new = [i['CatNumber'] for i in cw.searchcoin(g)]
        if g in self.__get_kn().keys():
            cat_num_old = self.__get_kn()[g]
        else: 
            cat_num_old = []
        if (set(cat_num_new)-set(cat_num_old)):
            for i in set(cat_num_new)-set(cat_num_old):
                self.__add_line(cw.getmonetdetailinfo(i))
                self.__upload_img()
                self.__upload_img(g)
            return f'new-> {set(cat_num_new)-set(cat_num_old)} add to Db'
        else:
            return 'no changes' 

    def get_coin_info(self, kn):
        """
        Метод обновляет атрубуты класса(или добавляет новые из self.names) 
        по конкретной монете(по каталожному номеру монеты kn)
        """
        if self.__confirm_kn(kn):
            for i in self.names:
                self.cursor.execute(f'''SELECT {i} FROM Coins WHERE cat_num = ?''', (kn,))
                self.__dict__[i] = self.cursor.fetchall()[0][0]
            if os.path.exists(os.path.join('img', str(self.begindate[:4]), f'{kn}.jpg')):
                self.img_a = os.path.join('img', str(self.begindate[:4]), f'{kn}.jpg')
            else:
                self.img_a = ''
            if os.path.exists(os.path.join('img', str(self.begindate[:4]), f'{kn}r.jpg')):
                self.img_r = os.path.join('img', str(self.begindate[:4]), f'{kn}r.jpg')
            else:
                self.img_r = ''
            return f'successfully updating methods'
        else:
            return f'incorrect cat_num - {kn} or not in the Db'       
            
    def __upload_img(self, g=None):
        """
        Метод скачивает и сохраняет локально(/img) изображения монет
        """
        cat_num_list = self.__get_kn()
        if not g:
            for i in set(cat_num_list):
                if not os.path.exists(os.path.join('img', str(i))):
                    os.makedirs(os.path.join('img', str(i)))
        else:
            for i in cat_num_list[g]:
                link_img = {'avers': f'https://cbr.ru/legacy/PhotoStore/img/{i}.jpg', 'revers': f'https://cbr.ru/legacy/PhotoStore/img/{i}r.jpg'}
                if not os.path.exists(os.path.join('img', str(g), f'{i}.jpg')):
                    p = requests.get(link_img['avers'])
                    img_a = open(os.path.join('img', str(g), f'{i}.jpg'), 'wb')
                    img_a.write(p.content)
                    img_a.close()
                if not os.path.exists(os.path.join('img', str(g), f'{i}r.jpg')):
                    p = requests.get(link_img['revers'])
                    img_r = open(os.path.join('img', str(g), f'{i}r.jpg'), 'wb')
                    img_r.write(p.content)
                    img_r.close()
                
            
    def __add_line(self, x):
        """
        Метод сохраняет строку в локальной БД
        """
        self.cursor.execute('''
        INSERT INTO Coins (
        autors,
        avers,
        revers,
        begindate,
        cat_num,
        comment,
        prefix,
        sname,
        nc_mintage,
        mintage,
        quality,
        weigth,
        sq_lenght,
        sq_width,
        thickness,
        diametr,
        finemetall,
        history_note,
        cname,
        nominal,
        nname,
        mname,
        tname
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
        x['autors'],
        x['avers'],
        x['revers'],
        x['begindate'],
        x['cat_num'],
        x['comment'],
        x['prefix'],
        x['sname'],
        x['nc_mintage'],
        x['mintage'],
        x['quality'],
        x['weigth'],
        x['sq_lenght'],
        x['sq_width'],
        x['thickness'],
        x['diametr'],
        x['finemetall'],
        x['history_note'],
        x['cname'],
        x['nominal'],
        x['nname'],
        x['mname'],
        x['tname'],
        ))
        self.connection.commit()
            
    def __confirm_kn(self, kn):
        """
        Метод проверяет наличие монеты(по kn) в локальной БД
        """
        res = []
        for i in self.__get_kn().values():
            res += i
        if kn in res:
            return True
        else:
            return False

    def __get_kn(self):
        """
        Метод возвращет словарь {'год':['kn',...], ...}
        из локальной БД
        """
        self.cursor.execute(f'''SELECT cat_num, begindate FROM Coins''')
        res = {}
        g = ''
        l = []
        for i in self.cursor.fetchall():            
            if g == i[1][:4]:
                l.append(i[0])
            else:
                if l:
                    res[g] = l
                    l = []
                    g = i[1][:4]
                    l.append(i[0])
                else:
                    g = i[1][:4]
                    l.append(i[0])
        res[g] = l
        return res
      
    def __del__(self):
        if hasattr(self, 'connection'):
            self.connection.close()
            return f'Db connection closed'
        
    def __repr__(self):
        return f'{self.err}'
        
        
def start(year_begin, db_path='coin.db'):
    """
    Стартовая функция, создает пустую локальную БД,
    начинает заполнять ее с года year_begin(1992 - начальный год в БД crb.ru),
    скачивает и сохраняет локально(/img) изображения монет,
    выводит в консоль информацию по заполнению БД.
    Запускать один раз, долее обновлять через метод класса check_kn
    """
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()       
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Coins (
    id INTEGER PRIMARY KEY,
    autors TEXT,
    avers TEXT,
    revers TEXT,
    begindate TEXT,
    cat_num TEXT,
    comment TEXT,
    prefix TEXT,
    sname TEXT,
    nc_mintage TEXT,
    mintage TEXT,
    quality TEXT,
    weigth TEXT,
    sq_lenght TEXT,
    sq_width TEXT,
    thickness TEXT,
    diametr TEXT,
    finemetall TEXT,
    history_note TEXT,
    cname TEXT,
    nominal TEXT,
    nname TEXT,
    mname TEXT,
    tname TEXT
    )
    ''')
    connection.commit()
    connection.close()
    print(f'база данных {db_path} создана, заполняем...')
    new = Coin_db()
    for i in range(year_begin, datetime.now().year + 1):
        print(f'{i} год')
        new.check_kn(str(i))
        print(f'OK')
    print(f'Done')


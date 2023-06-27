import kivy
import sqlite3
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.config import Config

Config.set("graphics", "width", "340")
Config.set("graphics", "height", "540")


def connect_to_database(path):
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        create_table_products(cursor)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)


def create_table_products(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS LuxBarbershop(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Ime TEXT NOT NULL,
            Prezime TEXT NOT NULL,
            Cijena FLOAT NOT NULL,
            Usluga FLOAT NOT NULL           
        )
        """
    )


class MainWid(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # self.theme_cls.theme_style = "Light"
        # self.theme_cls.primary_palette = "Orange"

        self.APP_PATH = os.getcwd()
        self.DB_PATH = self.APP_PATH + '/my_database.db'

        self.StartWid = StartWid(self)
        wid = Screen(name='start')
        wid.add_widget(self.StartWid)
        self.add_widget(wid)

        self.DatabaseWid = DatabaseWid(self)
        wid = Screen(name='database')
        wid.add_widget(self.DatabaseWid)
        self.add_widget(wid)

        self.InsertDataWid = InsertDataWid(self)
        wid = Screen(name='insertdata')
        wid.add_widget(self.InsertDataWid)
        self.add_widget(wid)

        self.UpdateDataWid = UpdateDataWid(self, data_id="0")
        wid = Screen(name='updatedata')
        wid.add_widget(self.UpdateDataWid)
        self.add_widget(wid)

        self.goto_start()

    def goto_start(self):
        self.current = 'start'

    def goto_database(self):
        self.DatabaseWid.check_memory()
        self.current = 'database'

    def goto_insert_data(self):
        self.InsertDataWid.clear_widgets()
        wid = InsertDataWid(self)
        self.InsertDataWid.add_widget(wid)
        self.current = 'insertdata'

    def goto_update_data(self, data_id):
        self.UpdateDataWid.clear_widgets()
        wid = UpdateDataWid(self, data_id)
        self.UpdateDataWid.add_widget(wid)
        self.current = 'updatedata'


class StartWid(BoxLayout):
    def __init__(self, mainwid, **kwargs):
        super().__init__(**kwargs)
        self.mainwid = mainwid

    def create_database(self):
        connect_to_database(self.mainwid.DB_PATH)
        self.mainwid.goto_database()


class DatabaseWid(BoxLayout):
    def __init__(self, mainwid, **kwargs):
        super().__init__(**kwargs)
        self.mainwid = mainwid

    def check_memory(self):
        self.ids.container.clear_widgets()

        conn = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT ID, Ime, Prezime, Cijena, Usluga FROM LuxBarbershop")

        for element in cursor:
            wid = DataWid(self.mainwid)
            id = 'ID: ' + str(element[0]) + '\n'
            barber = str(element[1]) + ' ' + str(element[2]) + '\n'
            cijena = "Cijena: " + str(element[3]) + '\n'
            usluga = "Usluga: " + str(element[4]) + '\n'

            wid.data_id = str(element[0])
            wid.data = id + barber + cijena + usluga
            self.ids.container.add_widget(wid)

        wid = NewDataButton(self.mainwid)
        self.ids.container.add_widget(wid)

        conn.close()


class NewDataButton(Button):
    def __init__(self, mainwid, **kwargs):
        super().__init__(**kwargs)
        self.mainwid = mainwid

    def create_new_product(self):
        print("Created new barber")
        self.mainwid.goto_insert_data()


class InsertDataWid(BoxLayout):
    def __init__(self, mainwid, **kwargs):
        super().__init__(**kwargs)
        self.mainwid = mainwid

    def insert_data(self):
        conn = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = conn.cursor()

        d1 = self.ids.ti_ime.text
        d2 = self.ids.ti_prezime.text
        d3 = self.ids.ti_cijena.text
        d4 = self.ids.ti_usluga.text

        a1 = (d1, d2, d3, d4)

        s1 = 'INSERT INTO LuxBarbershop (Ime, Prezime, Cijena, Usluga)'
        s2 = 'VALUES ("%s", "%s", %s, "%s")' % a1

        try:
            cursor.execute(s1 + " " + s2)
            conn.commit()
            conn.close()
            self.mainwid.goto_database()
        except Exception as e:
            if "" in a1:
                print("Niste unijeli sve podatke")
            else:
                print(e)

    def back_to_database(self):
        self.mainwid.goto_database()


class DataWid(BoxLayout):
    def __init__(self, mainwid, **kwargs):
        super().__init__(**kwargs)
        self.mainwid = mainwid

    def update_data(self, data_id):
        self.mainwid.goto_update_data(data_id)


class UpdateDataWid(BoxLayout):
    def __init__(self, mainwid, data_id, **kwargs):
        super().__init__(**kwargs)
        self.mainwid = mainwid
        self.data_id = data_id
        self.check_memory()

    def check_memory(self):
        conn = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = conn.cursor()
        s = 'SELECT Ime, Prezime, Cijena, Usluga from LuxBarbershop where ID ='
        cursor.execute(s + self.data_id)

        for element in cursor:
            self.ids.ti_ime.text = str(element[0])
            self.ids.ti_prezime.text = str(element[1])
            self.ids.ti_cijena.text = str(element[2])
            self.ids.ti_usluga.text = str(element[3])
        conn.close()

    def update_data(self):
        conn = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = conn.cursor()

        d1 = self.ids.ti_ime.text
        d2 = self.ids.ti_prezime.text
        d3 = self.ids.ti_cijena.text
        d4 = self.ids.ti_usluga.text

        a1 = (d1, d2, d3, d4)
        s1 = 'UPDATE LuxBarbershop SET'
        s2 = 'Ime = "%s", Prezime = "%s", Cijena = %s, Usluga = "%s"' % a1
        s3 = 'WHERE ID = %s' % self.data_id

        try:
            cursor.execute(s1 + " " + s2 + " " + s3)
            conn.commit()
            conn.close()
            self.mainwid.goto_database()
        except Exception as e:
            print("Greška u bazi")

    def delete_data(self):
        conn = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = conn.cursor()
        s = 'DELETE from LuxBarbershop WHERE ID =' + self.data_id

        cursor.execute(s)
        conn.commit()
        conn.close()
        self.mainwid.goto_database()

    def back_to_database(self):
        self.mainwid.goto_database()


class MainApp(App):
    title = "Lux Barbershop App"

    def build(self):
        # self.APP_PATH = os.getcwd()
        # self.DB_PATH = self.APP_PATH + '/my_database.db'
        # connect_to_database(self.DB_PATH)
        return MainWid()


if __name__ == '__main__':
    MainApp().run()

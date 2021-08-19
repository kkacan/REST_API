import os
from flask import Flask
import pymysql.cursors
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

class DbUtils:

    # Connect to the database
    @staticmethod
    def create_connection():
        return pymysql.connect(host='18.185.93.51',
                                user='user',
                                password='******',
                                db='baza',
                                charset='utf8',
                                cursorclass=pymysql.cursors.DictCursor)
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

    @staticmethod
    def check_credentials(email, password):

        valid = False
        connection = DbUtils.create_connection()

        try:
            with connection.cursor() as cursor:

                sql = 'SELECT lozinka FROM korisnik where email=%s;'
                cursor.execute(sql, email)
                result = cursor.fetchall()
                if len(result) > 0:
                    hash1 = result[0].get('lozinka')
                    valid = check_password_hash(hash1, password)
                    

        finally:
            cursor.close()
            connection.close()

        return valid

    @staticmethod
    def check_api_key(key):

        valid = False
        connection = DbUtils.create_connection()

        try:
            with connection.cursor() as cursor:

                sql = 'SELECT * FROM korisnik where email=%s;'
                cursor.execute(sql, key)
                result = cursor.fetchall()
                if len(result) > 0:
                    valid = True

        finally:
            cursor.close()
            connection.close()

        return valid    


class Queries:

    PONUDA =        'SELECT proizvod.id, proizvod.naziv, proizvod.cijena, proizvod.opis, tip_proizvoda.id as tipProizvoda, korisnik.ime, korisnik.prezime,'\
                        'korisnik.email, korisnik.grad, korisnik.tel, slika.slika FROM ponuda LEFT JOIN proizvod ON proizvod.id = ponuda.proizvod_id LEFT JOIN slika '\
                        'ON slika.proizvod_id = proizvod.id LEFT JOIN korisnik ON korisnik.id = ponuda.korisnik_id LEFT JOIN tip_proizvoda ON '\
                        'tip_proizvoda.id = proizvod.tip_proizvoda_id WHERE proizvod.naziv LIKE %s GROUP BY proizvod.id, tip_proizvoda.id, korisnik.id, slika.id;'
    
    PONUDA_TIP =    'SELECT proizvod.id, proizvod.naziv, proizvod.cijena, proizvod.opis, tip_proizvoda.id as tipProizvoda, korisnik.ime, korisnik.prezime,'\
                        'korisnik.email, korisnik.grad, korisnik.tel, slika.slika FROM ponuda LEFT JOIN proizvod ON proizvod.id = ponuda.proizvod_id LEFT JOIN slika '\
                        'ON slika.proizvod_id = proizvod.id LEFT JOIN korisnik ON korisnik.id = ponuda.korisnik_id LEFT JOIN tip_proizvoda ON '\
                        'tip_proizvoda.id = proizvod.tip_proizvoda_id WHERE tip_proizvoda.id=%s GROUP BY proizvod.id, tip_proizvoda.id, korisnik.id, slika.id;'
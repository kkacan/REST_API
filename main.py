import os
from flask import Flask, jsonify, request, abort, flash, request, redirect, url_for
import pymysql.cursors
import json
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import *
from config import Config
from utils import DbUtils
from utils import Queries


app = Flask(__name__)



@app.route('/api/v1/tip_proizvoda', methods=['GET'])
def get_tip_proizvoda():
    
    result = []

    key = request.args.get('apikey')

    if key == None:
        result.append('Missing apikey parameter!')
        return jsonify(result)
        
    if(DbUtils.check_api_key(key)):
    
        connection = DbUtils.create_connection()

        try:
    
            with connection.cursor() as cursor:

                sql = 'SELECT * from tip_proizvoda;'
                cursor.execute(sql)
                result = cursor.fetchall()

        finally:
            cursor.close()
            connection.close()
    
        return jsonify(result)
    else:
        result.append('Invalid apikey!')
        return jsonify(result)        

@app.route('/api/v1/ponuda', methods=['GET', 'POST', 'DELETE'])
def ponuda():
    
    result = []

    if request.method == 'GET':

        key = request.args.get('apikey')

        if key == None:
            result.append('Missing apikey parameter!')
            return jsonify(result)
        
        if(DbUtils.check_api_key(key)):    

            tip_id = request.args.get('id')
            search = request.args.get('search')

            if search == None: 
                search = ''

            if tip_id == None:
                tip_id = 0

            connection = DbUtils.create_connection()

            try:

                with connection.cursor() as cursor:

                    if int(tip_id) == 0:
                        sql = Queries.PONUDA
                        cursor.execute(sql, "%" + search + "%")
                        
                    else:
                        sql = Queries.PONUDA_TIP
                        cursor.execute(sql, tip_id)

                    result = cursor.fetchall()

            finally:
                cursor.close()
                connection.close()

            return jsonify(result)
        else:
            result.append('Invalid apikey!')
            return jsonify(result)    

    if request.method == 'POST':

        responsePonuda = ResponsePonuda()
        responsePonuda.responseImage = "Fail"
        result = responsePonuda.__dict__

        ponuda = json.loads(request.form['ponuda'])

        connection = DbUtils.create_connection()
        try:
            with connection.cursor() as cursor:

                sql = 'SELECT * FROM proizvod WHERE id=%s;'
                cursor.execute(sql, ponuda['id'])
                broj = cursor.rowcount

                if broj == 0:

                    cursor.execute("INSERT INTO proizvod (id, naziv, cijena, opis, tip_proizvoda_id, korisnik_id) VALUES ('%s','%s','%s','%s','%s','%s')"
                    %(ponuda['id'],ponuda['naziv'],ponuda['cijena'], ponuda['opis'], ponuda['tipProizvoda'], ponuda['korisnikId']))

                    cursor.execute("INSERT INTO slika (slika, proizvod_id) VALUES ('%s','%s')"
                    %(ponuda['slika'],ponuda['id']))

                    cursor.execute("INSERT INTO ponuda (korisnik_id, proizvod_id) VALUES ('%s','%s')"
                    %(ponuda['korisnikId'],ponuda['id']))

                    connection.commit()
                    responsePonuda.response = 'Success'
                else:
                    
                    sql = "UPDATE proizvod SET naziv=%s, cijena=%s, opis=%s, tip_proizvoda_id=%s, korisnik_id=%s WHERE id=%s"
                    val = (ponuda['naziv'], ponuda['cijena'], ponuda['opis'], ponuda['tipProizvoda'], ponuda['korisnikId'], ponuda['id'])
                    cursor.execute(sql, val)
                    
                    sql = "UPDATE slika SET slika=%s WHERE proizvod_id=%s"
                    val = (ponuda['slika'], ponuda['id'])
                    cursor.execute(sql, val)

                    sql = "UPDATE ponuda SET korisnik_id=%s WHERE proizvod_id=%s"
                    val = (ponuda['korisnikId'], ponuda['id'])
                    cursor.execute(sql, val)

                    connection.commit()
                    responsePonuda.response = 'Success'                   
        
        except:
            responsePonuda.response = 'Fail'
          

        finally:
            cursor.close()
            connection.close()

        if 'file' not in request.files:
            responsePonuda.responseImage = 'Fail'
            return jsonify(result)

        file = request.files['file']

        if file.filename == '':
            responsePonuda.responseImage = 'Fail'
            return jsonify(result)

        if file and DbUtils.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.root_path, Config.UPLOAD_FOLDER, filename))
            responsePonuda.responseImage = 'Success'
            return jsonify(result)


    if request.method == 'DELETE':

        responsePonuda = ResponsePonuda()
        responsePonuda.responseImage = "Fail"
        result = responsePonuda.__dict__
        ponuda = request.get_json()

        connection = DbUtils.create_connection()
        try:
            with connection.cursor() as cursor:
                sql = 'DELETE FROM proizvod WHERE id=%s'
                val = (ponuda['id'])
                cursor.execute(sql, val)

                sql = 'DELETE FROM slika WHERE proizvod_id=%s'
                val = (ponuda['id'])
                cursor.execute(sql, val)

                sql = 'DELETE FROM ponuda WHERE proizvod_id=%s'
                val = (ponuda['id'])
                cursor.execute(sql, val)

                connection.commit()
                responsePonuda.response = 'Success'
        
        except:
            responsePonuda.response = 'Fail'


        finally:
            cursor.close()
            connection.close()
        
        try:
            path = os.path.join(Config.UPLOAD_FOLDER, ponuda['slika'].replace(Config.IMAGE_PREFIX,''))
            if os.path.exists(path):
                os.remove(path)
        except:
            responsePonuda.responseImage = "Fail"

        return jsonify(result)
    

@app.route('/api/v1/korisnik', methods=['POST', 'PUT'])
def korisnik():
    
    result = []

    if request.method == 'POST':
        
        req_data = request.get_json()

        responseKorisnik = ResponseKorisnik()
        responseKorisnik.response = "Fail"
        result = responseKorisnik.__dict__

        connection = DbUtils.create_connection()

        try:
            with connection.cursor() as cursor:
                sql = 'SELECT count(email) as broj FROM korisnik WHERE email=%s;'
                cursor.execute(sql, req_data['email'])
                values = cursor.fetchall()
                broj = values[0].get('broj')

                if broj == 0:
                    hash1 = generate_password_hash(req_data['lozinka'])
                    cursor.execute("INSERT INTO korisnik (ime, prezime, grad, adresa, tel, email, lozinka) VALUES ('%s','%s','%s','%s','%s','%s','%s')"
                    %(req_data['ime'],req_data['prezime'], req_data['grad'], req_data['adresa'], req_data['tel'], req_data['email'], hash1))
                    connection.commit()

                    responseKorisnik.response = "Success"
                    responseKorisnik.korisnik = req_data
                    
                else:
                    responseKorisnik.response = "Exist"
                    responseKorisnik.korisnik = req_data
        except:
           responseKorisnik.response = "Fail"           
                      
            
        finally:
            cursor.close()
            connection.close()

    if request.method == 'PUT':
        
        req_data = request.get_json()

        responseKorisnik = ResponseKorisnik()
        responseKorisnik.response = "Fail"
        result = responseKorisnik.__dict__

        connection = DbUtils.create_connection()

        try:
            with connection.cursor() as cursor:

                sql = 'UPDATE korisnik SET ime=%s, prezime=%s, grad=%s, adresa=%s, tel=%s WHERE email=%s;'
                val = (req_data['ime'], req_data['prezime'], req_data['grad'], req_data['adresa'], req_data['tel'], req_data['email'])
                cursor.execute(sql, val)
                connection.commit()

                sql = 'SELECT * FROM korisnik WHERE email=%s;'
                cursor.execute(sql, req_data['email'])
                responseKorisnik.korisnik = cursor.fetchone()
                responseKorisnik.response = "Success"

        except:
            responseKorisnik.response = 'Fail'
   
        finally:
            cursor.close()
            connection.close()

    return jsonify(result)


@app.route('/api/v1/login', methods=['POST'])
def login():

    req_data = request.get_json()
    email = req_data['email']
    password = req_data['lozinka']
    broj = 0
    responseKorisnik = ResponseKorisnik()
    responseKorisnik.response = "Fail Password"
    result = responseKorisnik.__dict__

    connection = DbUtils.create_connection()
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT count(email) as broj FROM korisnik WHERE email=%s;'
            cursor.execute(sql, email)
            values = cursor.fetchall()
            broj = values[0].get('broj')

            if broj == 0:
                responseKorisnik.response = "Fail Username"
                
    except:
        responseKorisnik.response = "Fail"

    finally:
        cursor.close()
        connection.close()

    if broj > 0 and DbUtils.check_credentials(email, password):
        connection = DbUtils.create_connection()
        
        try:
            with connection.cursor() as cursor:

                sql = 'SELECT * FROM korisnik WHERE email=%s;'
                cursor.execute(sql, email)
                responseKorisnik.korisnik = cursor.fetchone()
                responseKorisnik.response = "Success"
 
        except:
           responseKorisnik.response = "Fail"

        finally:
            cursor.close()
            connection.close()
    
    return jsonify(result), 200


if __name__ == '__main__':
    app.run(host='192.168.1.199',debug=True)
    #app.run(debug=True)
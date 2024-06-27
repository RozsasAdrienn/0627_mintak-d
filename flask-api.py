from flask import Flask, request, json, Response
from flask_cors import CORS
import sqlite3
from hashlib import md5
from auth import letezik

api=Flask(__name__)
#cors hibák kezelése
"""
CORS(api)
api.config['CORS_HEADERS'] = 'Content-Type'
api.config['CORS_METHODS'] = ['GET, POST, PATCH, DELETE']
api.config['CORS_ORIGINS'] = ['localhost', 'localhost:5000', '127.0.0.1', '127.0.0.1:5000']
"""
# elegánsabb megoldás
CORS(api, origins=['localhost', 'localhost:5000', '127.0.0.1', '127.0.0.1:5000'], methods=['GET', 'POST'])


#bejelentkezés
@api.route('/users/login', methods=['POST'])
def get_token():
    data = request.json
    con = sqlite3.connect('data.db')
    con.row_factory = sqlite3.Row # mezőnevek használat a válaszban
    cursor = con.cursor()
    cursor.execute("SELECT id, token FROM users WHERE email=? AND password=?", (data['email'], md5(data['password'].encode('UTF-8')).hexdigest()))
    sor = cursor.fetchone()
    user = dict(zip(sor.keys(), sor))
    return json.dumps(user)
   
#regisztráció
@api.route('/users')
def get_users():
    if not letezik():
        return Response('Nem található', 401,{"WWW-Authenticate": "Basic realm=\"Login required\""})
    con = sqlite3.connect('data.db')
    con.row_factory = sqlite3.Row # mezőnevek használat a válaszban
    cursor = con.cursor()
    cursor.execute("SELECT * FROM users")
    sorok  = cursor.fetchall()
    felhasznalok = []
    for sor in sorok:
        d = dict(zip(sor.keys(), sor))
        felhasznalok.append(d)
    return json.dumps(felhasznalok)


#termékek lekérdezése
@api.route('/products', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def get_products():
    if not letezik():
        return Response('Nem található', 401,{"WWW-Authenticate": "Basic realm=\"Login required\""})
    
    con = sqlite3.connect('data.db')
    con.row_factory = sqlite3.Row # mezőnevek használat a válaszban
    cursor = con.cursor()

    if request.method == 'GET':       
        cursor.execute("SELECT * FROM products")
        sorok  = cursor.fetchall()
        products = []
        for sor in sorok:
            d = dict(zip(sor.keys(), sor))
            products.append(d)
        return json.dumps(products)
    
    if request.method == 'POST':
        termek = request.json
        cursor.execute('INSERT INTO products (category, name, description, picture, price, stock) VALUES (?, ?, ?, ?, ?, ?)', (termek['category'], termek['name'], termek['description'], termek['picture'], termek['price'], termek['stock']))
        con.commit()
        termek['id'] = cursor.lastrowid
        return json.dumps(termek)

    if request.method == 'PATCH':       
        termek = request.json
         # Az elérhető frissítési mezők listája
        allowed_fields = ['category', 'name', 'description', 'picture', 'price', 'stock']
        
        # Dinamikus SQL lekérdezés építése
        set_clause = ", ".join([f"{field} = ?" for field in termek if field in allowed_fields])
        parameters = tuple(termek[field] for field in termek if field in allowed_fields)
        

        cursor.execute(f"UPDATE products SET {set_clause} WHERE id = ?", parameters + (termek['id'],))
        con.commit()
        return json.dumps({'success': True, 'updated': termek}), 200

    if request.method == 'DELETE':
        termek = request.json
        cursor.execute("DELETE FROM products WHERE id = ?", (termek['id'],))
        con.commit()
        return json.dumps({'success': True, 'deleted': termek}), 200

#con.close()

if __name__ == '__main__':
    api.run(debug=True) # fejlesztés befejezése után távolítsuk el
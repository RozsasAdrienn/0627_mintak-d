# token ellenőrzés
from flask import request
import sqlite3

def letezik():
    if request.method == 'OPTIONS':
        return True
    
    #nem kell azonsítás
    noAuthResources = {
        'GET': ('products'),
        'POST': ('users=login'),
        'PATCH': (),
        'DELETE': ()
        }
    
    # url szétdarabolása 
    if(request.url.rsplit('/', 1))[-1] in noAuthResources[request.method]:
        # nem kell autentikáció rész kezelése
        return True
    
    # tokenes azonosítás
    token = request.headers['Token'] if 'Token' in request.headers else None
    con = sqlite3.connect('data.db')
    cursor = con.cursor()
    cursor.execute("SELECT id FROM users WHERE token=?", (token,))
    sor  = cursor.fetchone()
    if sor:
        return True

    # egyik se teljesül ezt adjuk vissza
    return False
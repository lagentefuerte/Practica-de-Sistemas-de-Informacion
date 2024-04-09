import sqlite3
from flask import Flask, render_template, request
import json
import pandas as pd
from consultas import *
import json



app = Flask(__name__)
app.static_folder = 'static'

def conectar_base_datos():
    return sqlite3.connect('example2.db')

@app.route('/')
def indice():
    return render_template("resultados.html")


@app.route('/vulnerable', methods=['GET']) #peticion get /topusuarios?num=x
def ejercicio1():
    calcular_puntuaciones_usuarios_criticos(cur, request.args.get('num'))
    calcular_politicas_desactualizadas(cur, request.args.get('num'))


@app.route('/top50', methods=['GET']) #peticion get /top50?string=(true/false)
def ejercicio2():
    if (request.args.get('string') == "true"):
        top50percent(cur, "DESC")
    else:
            top50percent(cur, "ASC")

if __name__ == '__main__':
    app.run(debug=True, port=8080)

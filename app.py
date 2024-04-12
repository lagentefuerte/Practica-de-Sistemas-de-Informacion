import sqlite3
from flask import Flask, render_template, request,redirect,url_for
import json

from consultas import *
import json



app = Flask(__name__)
app.static_folder = 'static'

def conectar_base_datos():
    return sqlite3.connect('example2.db')

@app.route('/')
def indice():
    return render_template("resultados.html")

@app.route('/formulario')
def mostrar_formulario():
    return render_template('formulario.html')

# Ruta para procesar el número ingresado por el usuario
@app.route('/procesar_numero', methods=['POST'])
def procesar_numero():
    if request.method == 'POST':
        numero = request.form['numero']  # Obtener el número del formulario
        return redirect(url_for('resultados', num=numero))  # Redireccionar a la página de resultados con el número como parámetro

# Ruta para mostrar los resultados
@app.route('/vulnerable/<int:num>')
def resultados(num):
    con = conectar_base_datos()
    cur = con.cursor()

    usuarios, puntuaciones = calcular_puntuaciones_usuarios_criticosPrueba(cur, num)

    paginas_web, politicas = calcular_politicas_desactualizadasPrueba(cur, num)
    cur.close()
    return render_template('Ejercicio1.html', usuarios=usuarios, puntuaciones=puntuaciones,pag=paginas_web, politicas=politicas)

#@app.route('/vulnerable', methods=['GET']) #peticion get /topusuarios?num=x
#def ejercicio1():
 #   con = conectar_base_datos()
  #  cur = con.cursor()
   # calcular_puntuaciones_usuarios_criticos(cur, request.args.get('num'))
    #calcular_politicas_desactualizadas(cur, request.args.get('num'))



@app.route('/top50', methods=['GET']) #peticion get /top50?string=(true/false)
def ejercicio2():
    if (request.args.get('string') == "true"):
        top50percent(cur, "DESC")
    else:
            top50percent(cur, "ASC")

if __name__ == '__main__':
    app.run(debug=True, port=8080)

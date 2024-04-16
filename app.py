import sqlite3,requests

from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

from flask import Flask, render_template, request,redirect,url_for,abort

import json


from consultas import *
import json



app = Flask(__name__)
app.static_folder = 'static'
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_id, name):
        self.id = user_id
        self.name = name

def conectar_base_datos():
    return sqlite3.connect('example2.db')

@app.errorhandler(400)
def bad_request_error(error):
    return render_template('Errores/error.html'), 400


@app.errorhandler(404)
def not_found_error(error):
    return render_template('Errores/errorNotFound.html'), 404

@app.route('/')
def indice():
    return render_template("resultados.html")

@app.route('/formulario/<destino>')
def mostrar_formulario(destino):
    return render_template('formulario.html',destino=destino)


@app.route('/procesar_numero/<destino>', methods=['POST'])
def procesar_numero(destino):
    """
    if request.method == 'POST':
        numero = request.form['numero']  #nº del form
        if destino == 'critico':
            return redirect(url_for('usuarios', num=numero))
        elif destino == 'politicas':
            return redirect(url_for('politicas', num=numero))
    """
    if request.method == 'POST':
        numero = request.form['numero']
        try:

            if len(numero)>6:
                abort(400)
            numero = int(numero)
            if numero < 0:
                render_template("Errores/errorNumerico.html")


            if destino == 'critico':
                return redirect(url_for('usuarios', num=numero))
            elif destino == 'politicas':
                return redirect(url_for('politicas', num=numero))
            else:#Destino no válido
                abort(404)
        except ValueError:
            # Fallo al convertir tipo dato
            abort(400)


@app.route('/usuariosCriticos/<int:num>')
def usuarios(num):
    con = conectar_base_datos()
    cur = con.cursor()

    usuarios, puntuaciones = calcular_puntuaciones_usuarios_criticosPrueba(cur, num)
    usuariosMayor,puntMayor = calcular_puntuaciones_usuarios_Mayor50(cur)
    usuariosMenor,puntMenor = calcular_puntuaciones_usuarios_Menor50(cur)
    cur.close()
    return render_template('UsuariosCriticos.html', usuarios=usuarios, puntuaciones=puntuaciones,usuariosMayor=usuariosMayor,puntMayor=puntMayor,usuariosMenor=usuariosMenor,puntMenor=puntMenor)

@app.route('/politicasDesactualizadas/<int:num>')
def politicas(num):
    con = conectar_base_datos()
    cur = con.cursor()

    paginas_web, politicas = calcular_politicas_desactualizadasPrueba(cur, num)
    cur.close()
    return render_template('PoliticasDesactualizadas.html',pag=paginas_web, politicas=politicas)



@app.route('/last10vulnerabilities')
def vulnerabilidades():
    response = requests.get('https://cve.circl.lu/api/last')
    data = response.json()
    last_10_entries = data[:10]

    #PARA VER EL FORMATO DEL JSON QUE SE OBTIENE
    #with open('last_10_vulnerabilities.json', 'w') as json_file:
     #   json.dump(last_10_entries, json_file)

    return render_template('Ejercicio3.html',datos=last_10_entries)

@app.route('/top50', methods=['GET']) #peticion get /top50?string=(true/false)
def ejercicio2():
    if (request.args.get('string') == "true"):
        top50percent(cur, "DESC")
    else:
            top50percent(cur, "ASC")

if __name__ == '__main__':
    app.run(debug=True, port=8080)


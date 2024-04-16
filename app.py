import sqlite3,requests
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask import Flask, render_template, request, redirect, url_for, abort
import json


from consultas import *
import json

def conectar_base_datos():
    return sqlite3.connect('example2.db')

def inicializar ():
    con = conectar_base_datos()
    cur = con.cursor()
    crearTablaLogin(con, cur)

app = Flask(__name__)
app.static_folder = 'static'
inicializar()
app.secret_key = 'clave_muy_secreta'
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
def indice():
    return render_template("resultados.html")

@app.route('/formulario/<destino>')
def mostrar_formulario(destino):
    return render_template('formulario.html',destino=destino)

# Ruta para procesar el número ingresado por el usuario
@app.route('/procesar_numero/<destino>', methods=['POST'])
def procesar_numero(destino):
    if request.method == 'POST':
        numero = request.form['numero']  # Obtener el número del formulario
        if destino == 'critico':
            # Redireccionar a la página de resultados para usuarios críticos con el número como parámetro
            return redirect(url_for('usuarios', num=numero))
        elif destino == 'politicas':
            # Redireccionar a la página de resultados para políticas con el número como parámetro
            return redirect(url_for('politicas', num=numero))

# Ruta para mostrar los resultados
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

@login_required
@app.route('/top50', methods=['GET']) #peticion get /top50?string=(true/false)
def ejercicio2():
    if (request.args.get('string') == "true"):
        top50percent(cur, "DESC")
    else:
            top50percent(cur, "ASC")

@app.route('/login', methods=['GET', 'POST'])
def login():
    con = conectar_base_datos()
    cur = con.cursor()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if consultalogin(cur, username, password):
            user = User(username)
            login_user(user)
            return redirect(url_for('indice'))
        else:
            return 'Usuario o contraseña incorrectos'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('indice'))


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        con = conectar_base_datos()
        cur = con.cursor()
        username = request.form['username']
        password = request.form['password']
        if registrar_usuario(cur, con, username, password):
            return redirect(url_for('login'))
        else:
            abort(404)

    return render_template('registro.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)


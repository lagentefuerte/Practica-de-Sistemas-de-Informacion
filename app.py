import sqlite3,requests
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask import Flask, render_template, request, redirect, url_for, abort
from sklearn import tree
from xhtml2pdf import pisa
from flask import Flask, render_template, request,redirect,url_for,abort
import pandas as pd
import json
from sklearn import linear_model
from sklearn.model_selection import train_test_split
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


@app.route('/metodos')
def metodos():
    # Conectar a la base de datos (debes definir esta función)
    con = conectar_base_datos()
    cur = con.cursor()

    # Obtener los datos de los usuarios
    Datos = obtenerDatosUsuarios(cur)
    cur.close()

    # Convertir el diccionario en un DataFrame
    df_usuarios = pd.DataFrame(Datos)

    # Leer los datos desde el archivo CSV
    df_usuarios.to_csv('usuarios.csv', index=False)
    train = pd.read_csv('usuarios.csv')

    # Separar las características (X) y la etiqueta (y)
    X = train[['phishing', 'total', 'contrasenadebil', 'permisos', 'cliclados']]
    y = train['etiquetas']

    # Dividir los datos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Inicializar y entrenar el modelo de Regresión Logística
    modelo = tree.DecisionTreeClassifier()


    modelo.fit(X_train, y_train)
    text_representation = tree.export_text(modelo)
    print(text_representation)
    # Predecir para un nuevo usuario
    nuevoUsuario = {
        'phishing': [256],
        'total': [300],
        'contrasenadebil': [0],
        'permisos': [0],
        'cliclados': [100]
    }

    nuevo_usuario_df = pd.DataFrame(X_test)
    prediccion = modelo.predict(nuevo_usuario_df)

    if prediccion < 0.5:
        etiqueta_predicha = "No crítico"
    else:
        etiqueta_predicha = "Crítico"

    print("La etiqueta predicha para el nuevo usuario es:", etiqueta_predicha)
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


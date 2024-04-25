import sqlite3, requests
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask import Flask, render_template, request, redirect, url_for, abort
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import export_graphviz
import graphviz
from xhtml2pdf import pisa
from flask import Flask, render_template, request,redirect,url_for,abort
import pandas as pd
import json
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from consultas import *
import json
import os
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
from subprocess import call
def conectar_base_datos():
    return sqlite3.connect('example2.db')

def inicializar ():
    con = conectar_base_datos()
    cur = con.cursor()
    crearTablaLogin(con, cur)

app = Flask(__name__)
app.static_folder = 'static'
inicializar()
crearBaseDatos()
ejercicio3()
app.secret_key = 'clave_muy_secreta'
login_manager = LoginManager()
login_manager.init_app(app)



"""
RUTAS BÁSICAS
"""
@app.route('/')
def indice():
    return render_template("resultados.html")

@app.errorhandler(400)
def bad_request_error(error):
    return render_template('Errores/error.html'), 400


@app.errorhandler(404)
def not_found_error(error):
    return render_template('Errores/errorNotFound.html'), 404


"""
EJERCICIO 1: Formulario, tratamiento de datos y visualización
"""
@app.route('/ejercicio1')
def ejercicio1():
    return render_template('ejercicio1elegirApartado.html')

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

    cur.close()
    return render_template('Ej1/UsuariosCriticos.html', usuarios=usuarios, puntuaciones=puntuaciones)

@app.route('/politicasDesactualizadas/<int:num>')
def politicas(num):
    con = conectar_base_datos()
    cur = con.cursor()

    paginas_web, politicas = calcular_politicas_desactualizadasPrueba(cur, num)
    cur.close()
    return render_template('Ej1/PoliticasDesactualizadas.html',pag=paginas_web, politicas=politicas)

"""
EJERCICIO 2: Gráficos usuarios con mayor o menor; formualrio y tratamiento de datos
"""
@app.route('/form2')
def form2():
    return render_template('formularioMayorMenor.html')

@app.route('/procesarMayorMenor', methods=['POST'])
def procesarMayorMenor():
    if request.method == 'POST':
        try:
            num = int(request.form['numero'])
            mayorMenor = int(request.form['cincuenta'])
            return redirect(url_for('ejercicio2', num=num, num2=mayorMenor))
        except (ValueError, KeyError):
            abort(400)
    else:
        abort(404)
@app.route('/ejercicio2/<int:num>/<int:num2>')
def ejercicio2(num,num2):
    con = conectar_base_datos()
    cur = con.cursor()
    if num2==1:
        usuarios, punt = calcular_puntuaciones_usuarios_Mayor50(cur, num)
    elif num2==2:
        usuarios, punt = calcular_puntuaciones_usuarios_Menor50(cur, num)
    else:
        abort(404)
    con.close()
    return render_template('usuariosMasMenos50.html',usuarios=usuarios,punt=punt)

"""
EJERCICIO 3: Últimas 10 vulnerabilidades
"""

@app.route('/last10vulnerabilities')
def vulnerabilidades():
    response = requests.get('https://cve.circl.lu/api/last')
    data = response.json()
    last_10_entries = data[:10]

    #PARA VER EL FORMATO DEL JSON QUE SE OBTIENE
    #with open('last_10_vulnerabilities.json', 'w') as json_file:
     #   json.dump(last_10_entries, json_file)

    return render_template('Ejercicio3.html',datos=last_10_entries)


"""
EJERCICIO 4: Login (pdf dentro de ejercicio 3)
"""
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)
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


"""
EJERCICIO 5: Algorigtmo IA
"""

@app.route('/metodos', methods=['POST'])
def metodoss():
    # Conectar a la base de datos (debes definir esta función)
    con = conectar_base_datos()
    cur = con.cursor()
    # Agregar la ruta al directorio binario de Graphviz al entorno
    os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'
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

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


    #Modelo Decision TREE
    modelo = tree.DecisionTreeClassifier()
    modelo.fit(X_train, y_train)
    


    #Modelo de regresión lineal
    PruebaArray = []
    for i in range(0, len(X_train)):
        PruebaArray.append(X_train.iloc[i]['cliclados'] / X_train.iloc[i]['total'])
    PruebaArray = np.array(PruebaArray).reshape(-1, 1)
    modeloLineal = linear_model.LinearRegression()
    modeloLineal.fit(PruebaArray, y_train)
    print(modeloLineal.coef_)


    #Modelo Ramdom Forest
    modeloForest = RandomForestClassifier(max_depth=2, random_state=0,n_estimators=10)
    modeloForest.fit(X_train, y_train)

    #Graficos
    grafico(modeloLineal, X_test, y_test)
    graficoRamdomForest(modeloForest,X)
    graficoDecisionTree(modelo, X)
    # Predecir para un nuevo usuario
    username = request.form['username']
    phone = request.form['phone']
    passwordHash = request.form['password']
    permisos = request.form['permisos']
    total = request.form['total']
    phishing = request.form['phishing']
    clicados = request.form['clicados']
    contrasena_debil = esContrasenaDebil(passwordHash)
    metodoInteligencia = request.form['metodoInt']
    nuevoUsuario = {
        'phishing': phishing,
        'total': total,
        'contrasenadebil': contrasena_debil,
        'permisos': permisos,
        'cliclados': clicados
    }
    if metodoInteligencia == '2':
        nuevo_usuario_df = pd.DataFrame(nuevoUsuario)
        prediccion = modelo.predict(nuevo_usuario_df)
    elif metodoInteligencia == '1':
        nuevoUsuario['cliclados_total'] = int (nuevoUsuario['cliclados']) / int(nuevoUsuario['total'])
        nuevo_usuario_df = pd.DataFrame([nuevoUsuario['cliclados_total']],
                                        columns=['cliclados_total'])  # Asegúrate de pasar una lista de diccionarios
        prediccion = modeloLineal.predict(nuevo_usuario_df)
    else:
        nuevo_usuario_df = pd.DataFrame(nuevoUsuario)
        prediccion = modeloForest.predict(nuevo_usuario_df)

    if prediccion < 0.5:
        etiqueta_predicha = "No crítico"
    else:
        etiqueta_predicha = "Crítico"

    # Renderiza la plantilla 'metoditos.html' y pasa la ruta de la imagen
    return render_template('metoditos.html', etiqueta = etiqueta_predicha)

def grafico(modeloLineal, X_test, y_test):
    # Predecir los valores de y
    PruebaArrayModelo = []
    for i in range(0, len(X_test)):
        PruebaArrayModelo.append(X_test.iloc[i]['cliclados'] / X_test.iloc[i]['total'])
    PruebaArrayModelo = np.array(PruebaArrayModelo).reshape(-1, 1)
    y_pred = modeloLineal.predict(PruebaArrayModelo)
    # Crear un gráfico de dispersión con los datos de entrenamiento
    plt.scatter(PruebaArrayModelo,y_test, color='red')
    # Dibujar la línea de regresión
    plt.plot(PruebaArrayModelo,y_pred, color='blue')
    # Etiquetas de los ejes
    plt.xlabel('Clicados respecto del total')
    plt.ylabel('Critico o no critico')
    # Guardar el gráfico como una imagen PNG
    plt.savefig('regression_line.png')
    # Mostrar el gráfico
    plt.show()
def graficoDecisionTree(modelo,X):
    # Exportar el árbol de decisiones a un archivo .dot
    dot_data = export_graphviz(modelo, out_file=None,
                               feature_names=X.columns.tolist(),
                               class_names=['0', '1'],
                               filled=True, rounded=True,
                               special_characters=True)
    graph = graphviz.Source(dot_data)
    graph.render('test', format='png')

def graficoRamdomForest(modeloForest,X):
    for i in range(len(modeloForest.estimators_)):
        estimator = modeloForest.estimators_[i]
        # Exportar cada árbol a un archivo .dot diferente
        export_graphviz(estimator,
                        out_file='tree' + str(i) + '.dot',
                        feature_names=X.columns.tolist(),
                        class_names=['0', '1'],
                        rounded=True, proportion=False,
                        precision=2, filled=True)
        # Convertir cada archivo .dot a una imagen PNG diferente
        call(['dot', '-Tpng', 'tree' + str(i) + '.dot', '-o', 'tree' + str(i) + '.png', '-Gdpi=600'])
"""
EJERCICIO 5.2: Datos para decicisión sobre usuario
"""

@app.route('/recogidaDatos')
def mostrat_recogida_datos():
    return render_template('datosUsuario.html')


@app.route('/verificarUsuario', methods=['POST'])
def nuevoUsuario():
    username = request.form['username']
    phone = request.form['phone']
    passwordHash = request.form['password']
    permisos = request.form['permisos']
    total = request.form['total']
    phishing = request.form['phishing']
    clicados = request.form['clicados']
    contrasena_debil = esContrasenaDebil(passwordHash)
    metodoInteligencia=request.form['metodoInt']
    """"
    1->Regresión Lineal
    2->Árbol de Decisión
    3->Bosque Aleatorio
    """

    #TODO MEZCLARLO CON EL METODO DE JUANCARLOS
    #return redirect('/') #TODO: devolver la misma página de
    return redirect(url_for('metodo', username=username, phone=phone, password=passwordHash, permisos=permisos, total=total, phishing=phishing, clicados=clicados, metodoInteligencia=metodoInteligencia))


def esContrasenaDebil(passwordHash):
    bool = False
    f = open("rockyou-20.txt", 'r')
    linea = f.readline()
    while not bool and linea:
        hashContrasena = calcularMD5(linea[:-1])
        bool = hashContrasena == passwordHash
        linea = f.readline()
    return bool





if __name__ == '__main__':
    app.run(debug=True, port=8080)


import sqlite3
from flask import Flask, render_template
import json
import pandas as pd



app = Flask(__name__)
app.static_folder = 'static'


@app.route('/')
def resultados():  # put application's code here
    con = sqlite3.connect("example2.db")
    sql_query = "SELECT * FROM tabla_ejemplo;"
    result = pd.read_sql_query(sql_query,con)

    # Procesar los resultados con pandas
    columns = ['columna1', 'columna2', 'columna3']  # Reemplaza con los nombres reales de tus columnas
    df = pd.DataFrame(result, columns=columns)

    # Aquí puedes realizar operaciones con pandas para preparar los datos para tus gráficas e informes
    # Por ejemplo, podrías hacer df.plot() para obtener una gráfica rápida

    # Convertir el DataFrame a un diccionario para pasarlo a la plantilla
    data_dict = df.to_dict(orient='records')

    return render_template("templates/resultados.html", data=data_dict)

@app.route('/aux')
def aux():
    return render_template("resultados.html")

if __name__ == '__main__':
    app.run(debug=True, port=5050)

import db
from flask import Flask, render_template
import json
import pandas as pd



app = Flask(__name__)
app.static_folder = 'static'


@app.route('/')
def resultados():  # put application's code here
    sql_query = "SELECT * FROM tabla_ejemplo;"
    result = query_database(sql_query)

    # Procesar los resultados con pandas
    columns = ['columna1', 'columna2', 'columna3']  # Reemplaza con los nombres reales de tus columnas
    df = pd.DataFrame(result, columns=columns)

    # Aquí puedes realizar operaciones con pandas para preparar los datos para tus gráficas e informes
    # Por ejemplo, podrías hacer df.plot() para obtener una gráfica rápida

    # Convertir el DataFrame a un diccionario para pasarlo a la plantilla
    data_dict = df.to_dict(orient='records')

    return render_template("templates/resultados.html", data=data_dict)


if __name__ == '__main__':
    app.run()

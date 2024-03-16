import sqlite3
from flask import Flask, render_template
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
    return render_template("layout.html")
@app.route('/Ej1.html')
def resultadosEj1():
    con=conectar_base_datos()
    cur=con.cursor()

    num_usuarios = num_muestras(cur)
    media_fechas, desviacion_fechas = media_desviacion_fechas_cambio_contrasena(cur)
    media_ips, desviacion_ips = media_desv_ips_detectadas(cur)
    media_emails_phishing, desviacion_emails_phishing = media_desv_phising(cur)
    min_emails, max_emails = min_max_emails_recibidos(cur)
    min_emails_phishing_admin, max_emails_phishing_admin = min_max_phising_interactuado_admin(cur)



    con.close()
    return render_template("Ej1.html",
                           num_usuarios=num_usuarios,
                           media_fechas=media_fechas,
                           desviacion_fechas=desviacion_fechas,
                           media_ips=media_ips,
                           desviacion_ips=desviacion_ips,
                           media_emails_phishing=media_emails_phishing,
                           desviacion_emails_phishing=desviacion_emails_phishing,
                           min_emails=min_emails,
                           max_emails=max_emails,
                           min_emails_phishing_admin=min_emails_phishing_admin,
                           max_emails_phishing_admin=max_emails_phishing_admin
                           )
@app.route('/Ej3.html')
def resultadosEj3():
    con=conectar_base_datos()
    cur=con.cursor()

    #la primera consulta
    users, punt = calcular_puntuaciones_usuarios_criticos(cur)
    pag, politicas = calcular_politicas_desactualizadas(cur)
    anio, cumplen, no_cumplen = calcular_cumplimiento_politicas_por_anio(cur)

    users_json = json.dumps(users)
    punt_json = json.dumps(punt)
    pag_json = json.dumps(pag)
    politicas_json = json.dumps(politicas)
    an_json = json.dumps(an)
    cum_json = json.dumps(cum)
    no_cum_json = json.dumps(no_cum)


    con.close()
    return render_template("Ej3.html",
                           users=users_json, punt=punt_json,
                           pag=pag_json, politicas=politicas_json,
                           an=an_json, cum=cum_json, no_cum=no_cum_json)



if __name__ == '__main__':
    app.run(debug=True, port=5050)

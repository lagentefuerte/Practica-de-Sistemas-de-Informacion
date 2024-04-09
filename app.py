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
@app.route('/Ej1')
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

@app.route('/Ej2')
def resultadosEj2():
    con = conectar_base_datos()
    cur = con.cursor()
    
    observaciones_usuarios=num_observaciones_usuarios(cur)
    sumUs,mediaUs,maxUs,minUS=sum_media_max_min_phishing_usuario(cur)
    medianaUs,varianzaUs=mediana_varianza_phishing_usuarios(cur)


    observaciones_admin=num_observaciones_admin(cur)
    sumAd, mediaAd, maxAd, minAd = sum_media_max_min_phishing_admin(cur)
    medianaAd,varianzaAd=mediana_varianza_phishing_admin(cur)

    observaciones_pass_debil=num_observaciones_pass_debil(cur)
    sumDebil, mediaDebil, maxDebil, minDebil = sum_media_max_min_phising_pass_debil(cur)
    medianaDebil,varianzaDebil=mediana_varianza_phising_pass_debil(cur)

    observaciones_pass_fuerte = num_observaciones_pass_fuerte(cur)
    sumFuerte, mediaFuerte, maxFuerte, minFuerte = sum_media_max_min_phising_pass_fuerte(cur)
    medianaFuerte,varianzaFuerte=mediana_varianza_phishing_pass_fuerte(cur)


    con.close()

    data = {
        "usuarios": {
            "missing": json.dumps(observaciones_usuarios),
            "observaciones": json.dumps(sumUs),
            "media": json.dumps(mediaUs),
            "maximo": json.dumps(maxUs),
            "minimo": json.dumps(minUS),
            "mediana": json.dumps(medianaUs),
            "varianza": json.dumps(varianzaUs)
        },
        "admin": {
            "missing": json.dumps(observaciones_admin),
            "observaciones": json.dumps(sumAd),
            "media": json.dumps(mediaAd),
            "maximo": json.dumps(maxAd),
            "minimo": json.dumps(minAd),
            "mediana": json.dumps(medianaAd),
            "varianza": json.dumps(varianzaAd)
        },
        "debil": {
            "missing": json.dumps(observaciones_pass_debil),
            "observaciones": json.dumps(sumDebil),
            "media": json.dumps(mediaDebil),
            "maximo": json.dumps(maxDebil),
            "minimo": json.dumps(minDebil),
            "mediana": json.dumps(medianaDebil),
            "varianza": json.dumps(varianzaDebil)
        },
        "fuerte": {
            "missing": json.dumps(observaciones_pass_fuerte),
            "observaciones": json.dumps(sumFuerte),
            "media": json.dumps(mediaFuerte),
            "maximo": json.dumps(maxFuerte),
            "minimo": json.dumps(minFuerte),
            "mediana": json.dumps(medianaFuerte),
            "varianza": json.dumps(varianzaFuerte)
        }
    }

    return render_template("Ej2.html", data=data)








@app.route('/Ej3')
def resultadosEj3():
    con=conectar_base_datos()
    cur=con.cursor()

    media_cambio_pass_usuarios,media_cambio_pass_admin=calcular_media_tiempo_cambio_contrasena_por_usuario(cur)
    users, punt = calcular_puntuaciones_usuarios_criticos(cur)
    pag, politicas = calcular_politicas_desactualizadas(cur)
    anio, cumplen, no_cumplen = calcular_cumplimiento_politicas_por_anio(cur)


    media_cambio_pass_usuarios_json=json.dumps(media_cambio_pass_usuarios)
    media_cambio_pass_admin_json = json.dumps(media_cambio_pass_admin)
    users_json = json.dumps(users)
    punt_json = json.dumps(punt)
    pag_json = json.dumps(pag)
    politicas_json = json.dumps(politicas)
    an_json = json.dumps(anio)
    cum_json = json.dumps(cumplen)
    no_cum_json = json.dumps(no_cumplen)


    con.close()
    return render_template("Ej3.html",
                           mediaUsers=media_cambio_pass_usuarios_json,mediaAdmin=media_cambio_pass_admin_json,
                           users=users_json, punt=punt_json,
                           pag=pag_json, politicas=politicas_json,
                           an=an_json, cum=cum_json, no_cum=no_cum_json)


@app.route('/topusuarios', methods=['GET']) #peticion get /topusuarios?num=x
def ejercicio1():
    calcular_puntuaciones_usuarios_criticos(cur, request.args.get('num'))


@app.route('/webvulnerables', methods=['GET']) #peticion get /webvulnerables?num=x
def ejercicio11():
    calcular_politicas_desactualizadas(cur, request.args.get('num'))

@app.route('/top50', methods=['GET']) #peticion get /top50?string=(true/false)
def ejercicio2():
    if (request.args.get('string') == "true"):
        top50percent(cur, "DESC")
    else:
            top50percent(cur, "ASC")

if __name__ == '__main__':
    app.run(debug=True, port=8080)

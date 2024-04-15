import json
import sqlite3
import statistics
import hashlib
from datetime import datetime


import matplotlib.pyplot as plt

def calcularMD5 (cadena):
    md5 = hashlib.md5()
    md5.update(cadena.encode('utf-8'))
    return md5.hexdigest()

con = sqlite3.connect('example2.db')
cur = con.cursor()
f = open("legal_data_online.json", "r")
datos = json.load(f)
cur.execute("CREATE TABLE IF NOT EXISTS legalData(""url TEXT PRIMARY KEY,"
            "cookies INTEGER,"
            "aviso INTEGER,"
            "proteccionDatos INTEGER,"
            "creacion INTEGER"
            ");")
con.commit()
for elem in datos["legal"]:
    clave = list(elem.keys())[0]
    print(clave)
    cur.execute("INSERT OR IGNORE INTO legalData(url, cookies, aviso, proteccionDatos, creacion)"
                "VALUES ('%s', '%d', '%d', '%d', '%d')" %
                (clave, elem[clave]['cookies'], elem[clave]['aviso'], elem[clave]['proteccion_de_datos'],
                 elem[clave]['creacion']))
    con.commit()

f.close()
f = open("users_data_online.json", "r")
datos_usuarios = json.load(f)
cur.execute("CREATE TABLE IF NOT EXISTS usuarios(""username TEXT PRIMARY KEY,"
            "telefono INTEGER,"
            "passwordHash TEXT,"
            "provincia TEXT,"
            "permisos INTEGER,"
            "total INTEGER,"
            "phishing INTEGER,"
            "cliclados INTEGER"
            ");")
cur.execute("CREATE TABLE IF NOT EXISTS ipfecha (""id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "username TEXT,"
            "ip_address TEXT,"
            "fecha DATE,"
            "FOREIGN KEY (username) REFERENCES usuarios (username)"
            ");")
con.commit()

for elem in datos_usuarios["usuarios"]:
    clave = list(elem.keys())[0]
    cur.execute(
        "INSERT OR IGNORE INTO usuarios(username, telefono, passwordHash, provincia, permisos, total, phishing, cliclados)"
        "VALUES ('%s', '%s', '%s', '%s', '%s', '%d', '%d', '%d')" %
        (clave, elem[clave]['telefono'], elem[clave]['contrasena'], elem[clave]['provincia'],
         elem[clave]['permisos'], elem[clave]["emails"]['total'], elem[clave]["emails"]['phishing'],
        elem[clave]["emails"]['cliclados']))
    for i in range(len(elem[clave]["fechas"])):
        if (elem[clave]["ips"] == "None"):
            cur.execute("INSERT OR IGNORE INTO ipfecha (username, ip_address, fecha)" "VALUES ('%s', '%s', '%s')" %
                    (clave, "None", elem[clave]["fechas"][i]))
        else:
            cur.execute("INSERT OR IGNORE INTO ipfecha (username, ip_address, fecha)" "VALUES ('%s', '%s', '%s')" %
                        (clave, elem[clave]["ips"][i], elem[clave]["fechas"][i]))

con.commit()
f.close()


#######################                 EJERCICIO 2

def num_muestras(cur):
    cur.execute("SELECT COUNT(*) from usuarios")
    numUs= cur.fetchall()[0][0]
    #print("Numero de usuarios:",numUs)
    return numUs
#num_muestras(cur)

# Obtener el número de fechas distintas por usuario en las que se ha cambiado la contraseña
def media_desviacion_fechas_cambio_contrasena(cur):
    cur.execute("""
        SELECT username, COUNT(DISTINCT fecha) AS num_fechas_cambio_contraseña
        FROM ipfecha
        GROUP BY username
    """)
    resultados = cur.fetchall()

    num_fechas_cambio_contraseña_por_usuario = [row[1] for row in resultados]

    media_fechas_cambio_contraseña = statistics.mean(num_fechas_cambio_contraseña_por_usuario)
    desviacion_estandar_fechas_cambio_contraseña = statistics.stdev(num_fechas_cambio_contraseña_por_usuario)

    #print("Media de fechas de cambio de contraseña por usuario:", media_fechas_cambio_contraseña)
    #print("Desviación estándar de fechas de cambio de contraseña por usuario:",desviacion_estandar_fechas_cambio_contraseña)
    return round(media_fechas_cambio_contraseña,3),round(desviacion_estandar_fechas_cambio_contraseña,3)
#media_desviacion_fechas_cambio_contrasena(cur)

def media_desv_ips_detectadas(cur):
    cur.execute("""
        SELECT username, COUNT(DISTINCT ip_address) AS num_ips_cambio_contraseña
        FROM ipfecha
        WHERE ip_address IS NOT NULL AND ip_address <> 'None'
        GROUP BY username
    """)
    resultados_ips = cur.fetchall()

    # Almacenar el número total de IPs por usuario
    num_ips_cambio_contraseña_por_usuario = [row[1] for row in resultados_ips]

    # Calcular la media y desviación estándar en Python
    media_ips_cambio_contraseña = statistics.mean(num_ips_cambio_contraseña_por_usuario)
    desviacion_estandar_ips_cambio_contraseña = statistics.stdev(num_ips_cambio_contraseña_por_usuario)

    #print("Media de IPs de cambio de contraseña por usuario:", media_ips_cambio_contraseña)
    #print("Desviación estándar de IPs de cambio de contraseña por usuario:", desviacion_estandar_ips_cambio_contraseña)
    return round(media_ips_cambio_contraseña,3),round(desviacion_estandar_ips_cambio_contraseña,3)
#media_desv_ips_detectadas(cur)

def media_desv_phising(cur):
    # Obtener el número de emails de phishing para cada usuario
    cur.execute("""
        SELECT phishing
        FROM usuarios
    """)
    num_emails_phishing_por_usuario = [row[0] for row in cur.fetchall()]

    media_emails_phishing = statistics.mean(num_emails_phishing_por_usuario)
    desviacion_estandar_emails_phishing = statistics.stdev(num_emails_phishing_por_usuario)
    #print("Media de emails de phishing por usuario:", media_emails_phishing)
    #print("Desviación estándar de emails de phishing por usuario:", desviacion_estandar_emails_phishing)
    return round(media_emails_phishing,3),round(desviacion_estandar_emails_phishing,3)
#media_desv_phising(cur)

def min_max_emails_recibidos(cur):
    cur.execute("""
        SELECT MIN(num_emails) AS min_total_emails,
               MAX(num_emails) AS max_total_emails
        FROM (
            SELECT total AS num_emails
            FROM usuarios
        ) AS total_emails_por_usuario;
    """)
    result = cur.fetchone()
    #print("Valor mínimo de emails recibidos:", result[0])
    #print("Valor máximo de emails recibidos:", result[1])
    return result[0],result[1]
#min_max_emails_recibidos(cur)

def min_max_phising_interactuado_admin(cur):
    # Valor mínimo y valor máximo del número de emails de phishing en los que ha interactuado un administrador
    cur.execute("""
        SELECT MIN(num_emails) AS min_emails_phishing_admin,
               MAX(num_emails) AS max_emails_phishing_admin
        FROM (
            SELECT phishing AS num_emails
            FROM usuarios
            WHERE permisos = "1"
            GROUP BY username
        ) AS emails_phishing_admin;
    """)
    result = cur.fetchone()
    #print("Valor mínimo de emails de phishing de un administrador:", result[0])
    #print("Valor máximo de emails de phishing de un administrador:", result[1])
    return result[0],result[1]
#min_max_phising_interactuado_admin(cur)



#######################                 EJERCICIO 3

cur.execute(""" ALTER TABLE usuarios DROP COLUMN es_contrasena_debil
""")

# Agrupaciones

cur.execute( """ ALTER TABLE usuarios
ADD COLUMN es_contrasena_debil INTEGER;
""")
cur.execute(""" SELECT passwordHash from usuarios;
""")
lista_contrasenas = cur.fetchall()
for contrasena in lista_contrasenas:
    bool = False
    f = open("rockyou-20.txt", 'r')
    linea = f.readline()
    while not bool and linea:
        hashContrasena = calcularMD5(linea[:-1])
        hashComparar = contrasena[0]
        bool = hashContrasena == hashComparar
        linea = f.readline()
    cur.execute("UPDATE usuarios SET es_contrasena_debil = ? WHERE passwordHash = ?", (int(bool), contrasena[0]))
con.commit()
f.close()


#CONSULTAS
def num_observaciones_usuarios(cur):
    cur.execute("""
        SELECT Count(*)
        FROM usuarios
        WHERE permisos = 0 and phishing = 0
    """)
    phishing_usuario = cur.fetchone()[0]
    #print(phishing_usuario)
    return phishing_usuario
#num_observaciones_usuarios(cur)



def num_observaciones_admin(cur):
    cur.execute("""
        SELECT Count(*)
        FROM usuarios
        WHERE permisos = 1 and phishing = 0
    """)
    phishing_admin = cur.fetchone()[0]
    return phishing_admin

def num_observaciones_pass_debil(cur):
    cur.execute("""
        SELECT Count(*)
        FROM usuarios
        WHERE es_contrasena_debil = 1 and phishing = 0
    """)
    phishing_weakPWD = cur.fetchone()[0]
    return phishing_weakPWD

def num_observaciones_pass_fuerte(cur):
    cur.execute("""
        SELECT Count(*)
        FROM usuarios
        WHERE es_contrasena_debil = 0 and phishing = 0
    """)
    phishing_strongPWD = cur.fetchone()[0]
    return phishing_strongPWD

def sum_media_max_min_phishing_usuario(cur):
    cur.execute("""
        SELECT SUM(phishing), AVG(phishing), MAX(phishing), MIN(phishing)
        FROM usuarios
        WHERE permisos = 0
    """)
    result = cur.fetchone()
    emails_sum = result[0]
    emails_avg = result[1]
    emails_max = result[2]
    emails_min = result[3]
    #print(emails_sum,emails_avg,emails_max,emails_min)
    return emails_sum,emails_avg,emails_max,emails_min
#sum_media_max_min_phishing_usuario(cur)

def sum_media_max_min_phishing_admin(cur):
    cur.execute("""
        SELECT SUM(phishing), AVG(phishing), MAX(phishing), MIN(phishing)
        FROM usuarios
        WHERE permisos = 1
    """)
    result = cur.fetchone()
    emails_sum = result[0]
    emails_avg = result[1]
    emails_max = result[2]
    emails_min = result[3]
    return emails_sum,emails_avg,emails_max,emails_min

def sum_media_max_min_phising_pass_fuerte(cur):
    cur.execute("""
        SELECT SUM(phishing), AVG(phishing), MAX(phishing), MIN(phishing)
        FROM usuarios
        WHERE es_contrasena_debil = 0
    """)
    result = cur.fetchone()
    emails_sum = result[0]
    emails_avg = result[1]
    emails_max = result[2]
    emails_min = result[3]
    return emails_sum,emails_avg,emails_max,emails_min

def sum_media_max_min_phising_pass_debil(cur):
    cur.execute("""
        SELECT SUM(phishing), AVG(phishing), MAX(phishing), MIN(phishing)
        FROM usuarios
        WHERE es_contrasena_debil = 1
    """)
    result = cur.fetchone()
    emails_sum = result[0]
    emails_avg = result[1]
    emails_max = result[2]
    emails_min = result[3]
    return emails_sum, emails_avg, emails_max, emails_min

def mediana_varianza_phishing_usuarios(cur):
    cur.execute("""
        SELECT phishing
        FROM usuarios
        WHERE permisos = 0
        GROUP BY username
    """)
    result = cur.fetchall()
    emails = [row[0] for row in result]
    emails_median = statistics.median(emails)
    emails_variance = statistics.variance(emails)
    #print(emails_median,emails_variance)
    return emails_median,emails_variance
#mediana_varianza_phishing_usuarios(cur)
def mediana_varianza_phishing_admin(cur):
    cur.execute("""
        SELECT phishing
        FROM usuarios
        WHERE permisos = 1
        GROUP BY username
    """)
    result = cur.fetchall()
    emails = [row[0] for row in result]
    emails_median = statistics.median(emails)
    emails_variance = statistics.variance(emails)
    return emails_median,emails_variance

def mediana_varianza_phishing_pass_fuerte(cur):
    cur.execute("""
        SELECT phishing
        FROM usuarios
        WHERE es_contrasena_debil = 0
        GROUP BY username
    """)
    result = cur.fetchall()
    emails = [row[0] for row in result]
    emails_median = statistics.median(emails)
    emails_variance = statistics.variance(emails)
    return emails_median,emails_variance

def mediana_varianza_phising_pass_debil(cur):
    cur.execute("""
        SELECT phishing
        FROM usuarios
        WHERE es_contrasena_debil = 1
        GROUP BY username
    """)
    result = cur.fetchall()
    emails = [row[0] for row in result]
    emails_median = statistics.median(emails)
    emails_variance = statistics.variance(emails)
    return emails_median,emails_variance






#######################                 EJERCICIO 4

def calcular_media_tiempo_cambio_contrasena_por_usuario(cur):
    cur.execute('''SELECT DISTINCT usuarios.username, fecha, permisos 
                FROM usuarios 
                JOIN ipfecha 
                ON usuarios.username = ipfecha.username 
                ORDER BY usuarios.username, fecha''')
    rows = cur.fetchall()

    # Diccionario para almacenar las fechas ordenadas por usuario
    fechas_por_usuario = {}

    # Iterar sobre las filas y almacenar las fechas ordenadas por usuario
    for row in rows:
        user, fecha_str, permiso = row
        fecha = datetime.strptime(fecha_str, "%d/%m/%Y")

        if user not in fechas_por_usuario:
            fechas_por_usuario[user] = []

        fechas_por_usuario[user].append((fecha, permiso))

    # Diccionario para almacenar los tiempos de cambio de contraseña por permiso
    tiempos_por_permiso = {}

    # Iterar sobre las fechas por usuario y calcular los tiempos de cambio de contraseña
    for user, fechas_permisos in fechas_por_usuario.items():
        fechas_permisos.sort()  # Ordenar las fechas

        for i in range(1, len(fechas_permisos)):
            fecha_anterior, permiso_anterior = fechas_permisos[i - 1]
            fecha_actual, permiso_actual = fechas_permisos[i]

            # Verificar si es el mismo permiso
            if permiso_actual == permiso_anterior:
                # Calcular la diferencia de tiempo entre fechas consecutivas
                tiempo_cambio = fecha_actual - fecha_anterior

                # Agregar el tiempo de cambio a la lista correspondiente
                if permiso_actual not in tiempos_por_permiso:
                    tiempos_por_permiso[permiso_actual] = []

                tiempos_por_permiso[permiso_actual].append(tiempo_cambio.days)

    # Calcular la media de los tiempos de cambio de contraseña por permiso
    medias_por_permiso = {}
    for permiso, tiempos in tiempos_por_permiso.items():
        media_tiempo = sum(tiempos) / len(tiempos)
        medias_por_permiso[permiso] = media_tiempo

    medias=[]
    for permiso, media in medias_por_permiso.items():
        #print(f"Media de tiempo de cambio de contraseña para permiso {permiso}: {media:.2f} días")
        medias.append(round(media,2))
    return medias[0],medias[1]

#calcular_media_tiempo_cambio_contrasena_por_usuario(cur)

def calcular_puntuaciones_usuarios_criticosOriginal(cur, num): #la puntuación hay que multiplicar por 100 el nº de fishing para que no de 0, algo; da directamente la probabilidad
    cur.execute("""SELECT username, (phishing*100 / total) AS puntuacion
        FROM usuarios WHERE es_contrasena_debil==1
        ORDER BY puntuacion DESC
        LIMIT ?
    """, int(num))
    resultados = cur.fetchall()
    usuarios = [row[0] for row in resultados]
    puntuaciones = [row[1] for row in resultados]
    #print("usuarios",end="")
    #print(usuarios)
    #print("puntuaciones",end="")
    #print(puntuaciones)
    return usuarios, puntuaciones

def calcular_puntuaciones_usuarios_criticosPrueba(cur, num): #la puntuación hay que multiplicar por 100 el nº de fishing para que no de 0, algo; da directamente la probabilidad
    consulta_sql = """
            SELECT username, (phishing*100 / total) AS puntuacion
            FROM usuarios WHERE es_contrasena_debil==1
            ORDER BY puntuacion DESC
            LIMIT ?
        """
    cur.execute(consulta_sql, (num,))
    resultados=cur.fetchall()
    usuarios = [row[0] for row in resultados]
    puntuaciones = [row[1] for row in resultados]
    #print("usuarios",end="")
    #print(usuarios)
    #print("puntuaciones",end="")
    #print(puntuaciones)
    return usuarios, puntuaciones

def calcular_puntuaciones_usuarios_criticosMayor50(cur):


    consulta_sql = """
            SELECT username, (phishing * 100 / total) AS puntuacion
            FROM usuarios WHERE (((cliclados * 100 / phishing)) < 50)
            ORDER BY puntuacion DESC
        """
    cur.execute(consulta_sql)
    resultados = cur.fetchall()
    usuarios = [row[0] for row in resultados]
    puntuaciones = [row[1] for row in resultados]
    return usuarios, puntuaciones

def calcular_politicas_desactualizadasOriginal(cur, num): #que es desactualizada, menor a que año?
    cur.execute("""
        SELECT url, SUM(cookies + aviso + proteccionDatos) AS politicas_desactualizadas
        FROM legalData
        GROUP BY url
        ORDER BY politicas_desactualizadas DESC
        LIMIT ?
    """, int(num))
    resultados = cur.fetchall()
    paginas_web = [row[0] for row in resultados]
    politicas = [row[1] for row in resultados]
    #print("paginas web", end="")
    #print(paginas_web)
    #print("politicas", end="")
    #print(politicas) #en base al numero de politicas que tiene
    return paginas_web, politicas
#pag,politicas=calcular_politicas_desactualizadas(cur)

def calcular_politicas_desactualizadasPrueba(cur, num): #que es desactualizada, menor a que año?
    consulta="""
        SELECT url, SUM(cookies + aviso + proteccionDatos) AS politicas_desactualizadas
        FROM legalData
        GROUP BY url
        ORDER BY politicas_desactualizadas DESC
        LIMIT ?
    """
    cur.execute(consulta,(num,))
    resultados = cur.fetchall()
    paginas_web = [row[0] for row in resultados]
    politicas = [row[1] for row in resultados]
    #print("paginas web", end="")
    #print(paginas_web)
    #print("politicas", end="")
    #print(politicas) #en base al numero de politicas que tiene
    return paginas_web, politicas


def calcular_cumplimiento_politicas_por_anio(cur):
    cur.execute("""
        SELECT creacion AS anio, 
               SUM(CASE WHEN cookies = 1 AND aviso = 1 AND proteccionDatos = 1 THEN 1 ELSE 0 END) AS cumplen,
               SUM(CASE WHEN cookies <> 1 OR aviso <> 1 OR proteccionDatos <> 1 THEN 1 ELSE 0 END) AS no_cumplen
        FROM legalData
        GROUP BY anio
    """)
    resultados = cur.fetchall()
    anios = [row[0] for row in resultados]
    cumplen = [row[1] for row in resultados]
    no_cumplen = [row[2] for row in resultados]
    #print("años", end="")
    #print(anios)
    #print("cumplen politicas", end="")
    #print(cumplen)
    #print("no cumplen todas las politicas", end="")
    #print(no_cumplen)
    return anios, cumplen, no_cumplen

#an,cum,no_cum=calcular_cumplimiento_politicas_por_anio(cur)

def top50percent(cur, string): #la puntuación hay que multiplicar por 100 el nº de fishing para que no de 0, algo; da directamente la probabilidad
    cur.execute("""
        SELECT username, (cliclados / phishing) AS puntuacion
        FROM usuarios WHERE es_contrasena_debil==1
        ORDER BY puntuacion ?
        LIMIT 15
    """, string)
    resultados = cur.fetchall()
    usuarios = [row[0] for row in resultados]
    puntuaciones = [row[1] for row in resultados]
    #print("usuarios",end="")
    #print(usuarios)
    #print("puntuaciones",end="")
    #print(puntuaciones)
    return usuarios, puntuaciones

con.close()
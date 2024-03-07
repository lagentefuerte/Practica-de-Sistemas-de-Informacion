import json
import sqlite3
import statistics

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
cur.execute("SELECT COUNT(*) from usuarios")
print("Numero de usuarios:", cur.fetchall()[0][0])
# Obtener el número de fechas distintas por usuario en las que se ha cambiado la contraseña
cur.execute("""
    SELECT username, COUNT(DISTINCT fecha) AS num_fechas_cambio_contraseña
    FROM ipfecha
    GROUP BY username
""")
resultados = cur.fetchall()


num_fechas_cambio_contraseña_por_usuario = [row[1] for row in resultados]


media_fechas_cambio_contraseña = statistics.mean(num_fechas_cambio_contraseña_por_usuario)
desviacion_estandar_fechas_cambio_contraseña = statistics.stdev(num_fechas_cambio_contraseña_por_usuario)

print("Media de fechas de cambio de contraseña por usuario:", media_fechas_cambio_contraseña)
print("Desviación estándar de fechas de cambio de contraseña por usuario:", desviacion_estandar_fechas_cambio_contraseña)

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

print("Media de IPs de cambio de contraseña por usuario:", media_ips_cambio_contraseña)
print("Desviación estándar de IPs de cambio de contraseña por usuario:", desviacion_estandar_ips_cambio_contraseña)

# Obtener el número de emails de phishing para cada usuario
cur.execute("""
    SELECT phishing
    FROM usuarios
""")
num_emails_phishing_por_usuario = [row[0] for row in cur.fetchall()]


media_emails_phishing = statistics.mean(num_emails_phishing_por_usuario)
desviacion_estandar_emails_phishing = statistics.stdev(num_emails_phishing_por_usuario)
print("Media de emails de phishing por usuario:", media_emails_phishing)
print("Desviación estándar de emails de phishing por usuario:", desviacion_estandar_emails_phishing)


cur.execute("""
    SELECT MIN(num_emails) AS min_total_emails,
           MAX(num_emails) AS max_total_emails
    FROM (
        SELECT total AS num_emails
        FROM usuarios
    ) AS total_emails_por_usuario;
""")
result = cur.fetchone()
print("Valor mínimo de emails recibidos:", result[0])
print("Valor máximo de emails recibidos:", result[1])

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
print("Valor mínimo de emails de phishing de un administrador:", result[0])
print("Valor máximo de emails de phishing de un administrador:", result[1])

cur.execute( """ ALTER TABLE usuarios
ADD COLUMN es_contrasena_debil BOOLEAN;
""")
cur.execute(""" SELECT passwordHash from usuarios;
""")
lista_contrasenas = cur.fetchall()[0]
for contrasena in lista_contrasenas:
    bool = False
    #while not bool:
        #Comprobar si esta en rockyou
    if bool:
        cur.execute(""" UPDATE usuarios
                        SET es_contrasena_debil = 1 WHERE passwordHash = contrasena;
                        """)
    else:
        cur.execute(""" UPDATE usuarios
                                SET es_contrasena_debil = 0 WHERE passwordHash = ?;
                                """, (contrasena,))

con.close()
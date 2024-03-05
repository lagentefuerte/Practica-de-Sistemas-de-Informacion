import json
import sqlite3

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
            "fecha TEXT,"
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
cur.execute("SELECT count from usuarios")
print("Numero de usuarios: " + cur.fetchall())

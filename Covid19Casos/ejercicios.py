
import csv
import sqlite3

# Ruta al archivo CSV
RUTA_CSV = "C:/Users/Usuario/OneDrive/Escritorio/Covid19-Argentina-EDA/Covid19Casos/Covid19Casos.csv"

# Crear base de datos y tabla
def crear_tabla():
    conn = sqlite3.connect("covid.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS casos")
    cur.execute("""
        CREATE TABLE casos (
            sexo TEXT,
            edad INTEGER,
            edad_años_meses TEXT,
            residencia_pais_nombre TEXT,
            residencia_provincia_nombre TEXT,
            residencia_departamento_nombre TEXT,
            carga_provincia_nombre TEXT,
            fallecido TEXT,
            asistencia_respiratoria_mecanica TEXT,
            origen_financiamiento TEXT,
            clasificacion TEXT,
            fecha_diagnostico TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Tabla creada correctamente.")

# Cargar datos desde CSV
def cargar_datos():
    conn = sqlite3.connect("covid.db")
    cur = conn.cursor()
    with open(RUTA_CSV, encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        encabezado = next(lector)
        for fila in lector:
            if len(fila) == 12:
                cur.execute("INSERT INTO casos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", fila)
    conn.commit()
    conn.close()
    print("✅ Datos cargados correctamente.")


# Punto 1 - Descripción de variables
def punto1_describir_variables():
    conn = sqlite3.connect("covid.db")
    cur = conn.cursor()
    print("\n📊 Punto 1: Descripción de las variables\n")

    variables = [
        ("sexo", "Cualitativa", "Nominal"),
        ("edad", "Cuantitativa", "Discreta"),
        ("edad_años_meses", "Cualitativa", "Nominal"),
        ("residencia_pais_nombre", "Cualitativa", "Nominal"),
        ("residencia_provincia_nombre", "Cualitativa", "Nominal"),
        ("residencia_departamento_nombre", "Cualitativa", "Nominal"),
        ("carga_provincia_nombre", "Cualitativa", "Nominal"),
        ("fallecido", "Cualitativa", "Binaria"),
        ("asistencia_respiratoria_mecanica", "Cualitativa", "Binaria"),
        ("origen_financiamiento", "Cualitativa", "Nominal"),
        ("clasificacion", "Cualitativa", "Nominal"),
        ("fecha_diagnostico", "Cualitativa", "Ordinal")
    ]

    for var, tipo, clasificacion in variables:
        print(f"🔸 Variable: {var}")
        print(f"   Tipo: {tipo}")
        print(f"   Clasificación: {clasificacion}")
        
        if var == "edad":
            cur.execute("SELECT MIN(edad), MAX(edad) FROM casos WHERE edad IS NOT NULL AND edad != ''")
            minimo, maximo = cur.fetchone()
            print(f"   Rango: {minimo} a {maximo}")
        else:
            cur.execute(f"SELECT DISTINCT {var} FROM casos WHERE {var} IS NOT NULL AND {var} != ''")
            valores = [fila[0] for fila in cur.fetchall()]
            print(f"   Valores posibles (ejemplo): {', '.join(valores[:5])}...")
        print("")

    conn.close()

# Punto 2 - Valores faltantes en edad
def punto2_edad_faltante():
    conn = sqlite3.connect("covid.db")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM casos")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM casos WHERE edad IS NULL OR edad = ''")
    faltantes = cur.fetchone()[0]

    porcentaje = (faltantes / total) * 100

    print("\n Punto 2: Análisis de valores faltantes en 'edad'")
    print(f"Total de registros: {total}")
    print(f"Registros sin edad: {faltantes}")
    print(f"Porcentaje de faltantes: {porcentaje:.2f}%")

    if porcentaje < 5:
        print("✅ Recomendación: Se pueden eliminar los registros sin edad.")
    else:
        print("⚠️ Recomendación: Reemplazar los valores faltantes con un valor central (media o mediana).")

    conn.close()

def punto3_promedio_edad_fallecidos():
    conn = sqlite3.connect("covid.db")
    cur = conn.cursor()

    print("\n Punto 3: Edad promedio de fallecidos por provincia")

    # Calcular edad promedio de fallecidos por provincia
    cur.execute("""
        SELECT residencia_provincia_nombre, AVG(edad)
        FROM casos
        WHERE fallecido = 'SI' AND edad IS NOT NULL AND edad != ''
        GROUP BY residencia_provincia_nombre
        ORDER BY residencia_provincia_nombre
    """)
    resultados = cur.fetchall()

    for provincia, promedio in resultados:
        print(f"🧾 {provincia}: {promedio:.2f} años")

    # Parte 2: detectar outliers en edad de fallecidos
    print("\n Detección de outliers en edades de fallecidos (criterio IQR)")

    # Obtener todas las edades de fallecidos válidas
    cur.execute("""
        SELECT edad FROM casos
        WHERE fallecido = 'SI' AND edad IS NOT NULL AND edad != ''
        ORDER BY edad
    """)
    edades = [int(f[0]) for f in cur.fetchall()]

    if len(edades) < 4:
        print("⚠️ No hay suficientes datos para detectar outliers.")
        conn.close()
        return

    # Calcular Q1, Q3 y IQR
    def calcular_cuartiles(lista):
        n = len(lista)
        Q1 = lista[n // 4]
        Q3 = lista[3 * n // 4]
        IQR = Q3 - Q1
        return Q1, Q3, IQR

    Q1, Q3, IQR = calcular_cuartiles(edades)
    lim_inf = Q1 - 1.5 * IQR
    lim_sup = Q3 + 1.5 * IQR

    print(f"Q1: {Q1} | Q3: {Q3} | IQR: {IQR}")
    print(f"Límite inferior: {lim_inf}")
    print(f"Límite superior: {lim_sup}")

    outliers = [e for e in edades if e < lim_inf or e > lim_sup]
    print(f"🔍 Se encontraron {len(outliers)} outliers en las edades de fallecidos.")
    if outliers:
        print(f"Ejemplos: {outliers[:10]}...")

    conn.close()

import math

def punto4_sturges_intervalos():
    conn = sqlite3.connect("covid.db")
    cur = conn.cursor()

    print("\n Punto 4: Tabla de intervalos de edad (método de Sturges)")

    # Obtener edades válidas y confirmadas entre 0 y 120
    cur.execute("""
        SELECT CAST(edad AS INTEGER) FROM casos
        WHERE edad IS NOT NULL AND edad != ''
        AND CAST(edad AS INTEGER) BETWEEN 0 AND 120
        AND LOWER(clasificacion) LIKE '%confirmado%'
    """)

    edades = [fila[0] for fila in cur.fetchall()]
    n = len(edades)

    if n == 0:
        print("❌ No hay datos suficientes.")
        return

    edad_min = min(edades)
    edad_max = max(edades)
    rango = edad_max - edad_min

    # Método de Sturges
    k = round(1 + 3.322 * math.log10(n))
    ancho_clase = math.ceil(rango / k)

    print(f"\n✅ Total de datos: {n}")
    print(f"✅ Número de clases (k): {k}")
    print(f"✅ Intervalo de clase: {ancho_clase}")
    print(f"✅ Rango: {edad_min} a {edad_max}")

    # Crear intervalos
    intervalos = []
    inferior = edad_min
    for i in range(k):
        superior = inferior + ancho_clase - 1
        intervalos.append((inferior, superior))
        inferior = superior + 1

    # Contar frecuencias
    frecuencias = []
    for inf, sup in intervalos:
        conteo = sum(1 for edad in edades if inf <= edad <= sup)
        frecuencias.append((f"{inf} - {sup}", conteo))

    # Mostrar tabla
    print("\n📊 Intervalos de edad (casos confirmados):\n")
    print(f"{'Intervalo':<15} {'Frecuencia':>10}")
    print("-" * 28)
    for intervalo, frec in frecuencias:
        print(f"{intervalo:<15} {frec:>10}")

    conn.close()


def punto5_mujeres_hombres_fallecidos_por_intervalo():
    conn = sqlite3.connect("covid.db")
    cur = conn.cursor()

    print("\n Punto 5: Intervalo con más mujeres fallecidas y mayor % de hombres fallecidos")

    # Crear intervalos fijos de 5 años (de 0 a 104)
    intervalos = [(i, i + 4) for i in range(0, 105, 5)]
    k = len(intervalos)

    # Inicializar contadores
    mujeres_fallecidas = [0] * k
    hombres_fallecidos = [0] * k
    hombres_totales = [0] * k

    # Mujeres fallecidas por edad
    cur.execute("""
        SELECT CAST(edad AS INTEGER) FROM casos
        WHERE sexo = 'F' AND fallecido = 'SI'
        AND edad IS NOT NULL AND edad != ''
        AND CAST(edad AS INTEGER) BETWEEN 0 AND 120
    """)
    for edad in cur.fetchall():
        edad = edad[0]
        for i, (inicio, fin) in enumerate(intervalos):
            if inicio <= edad <= fin:
                mujeres_fallecidas[i] += 1
                break

    # Hombres fallecidos y totales por edad
    cur.execute("""
        SELECT CAST(edad AS INTEGER), fallecido FROM casos
        WHERE sexo = 'M'
        AND edad IS NOT NULL AND edad != ''
        AND CAST(edad AS INTEGER) BETWEEN 0 AND 120
    """)
    for edad, fallecido in cur.fetchall():
        for i, (inicio, fin) in enumerate(intervalos):
            if inicio <= edad <= fin:
                hombres_totales[i] += 1
                if fallecido.strip().upper() == 'SI':
                    hombres_fallecidos[i] += 1
                break

    # Calcular porcentajes
    porcentaje_hombres = []
    for fallecidos, total in zip(hombres_fallecidos, hombres_totales):
        if total == 0:
            porcentaje_hombres.append(0)
        else:
            porcentaje_hombres.append((fallecidos / total) * 100)

    # Mostrar tabla
    print(f"\n{'Intervalo':<15} {'Mujeres fallecidas':<20} {'% Hombres fallecidos'}")
    print("-" * 60)
    for i, (inicio, fin) in enumerate(intervalos):
        print(f"{inicio:>3} - {fin:<10} {mujeres_fallecidas[i]:<20} {porcentaje_hombres[i]:.2f}%")

    # Buscar máximos
    max_mujeres_idx = mujeres_fallecidas.index(max(mujeres_fallecidas))
    max_porcentaje_idx = porcentaje_hombres.index(max(porcentaje_hombres))

    print(f"\n✅ Intervalo con más mujeres fallecidas: {intervalos[max_mujeres_idx]}")
    print(f"✅ Intervalo con mayor % de hombres fallecidos: {intervalos[max_porcentaje_idx]}")

    conn.close()


def punto6_confirmados_por_provincia_y_sexo():
    conn = sqlite3.connect("covid.db")
    cur = conn.cursor()

    print("\n Punto 6: Provincia con más casos confirmados por sexo")

    # Mujeres
    cur.execute("""
        SELECT residencia_provincia_nombre, COUNT(*) AS cantidad
        FROM casos
        WHERE TRIM(sexo) = 'F'
        AND LOWER(clasificacion) LIKE '%confirmado%'
        GROUP BY residencia_provincia_nombre
        ORDER BY cantidad DESC
        LIMIT 1
    """)
    mujer = cur.fetchone()
    if mujer:
        print(f"👩 Provincia con más casos confirmados en mujeres: {mujer[0]} ({mujer[1]} casos)")
    else:
        print("❌ No se encontraron casos confirmados en mujeres.")

    # Hombres
    cur.execute("""
        SELECT residencia_provincia_nombre, COUNT(*) AS cantidad
        FROM casos
        WHERE TRIM(sexo) = 'M'
        AND LOWER(clasificacion) LIKE '%confirmado%'
        GROUP BY residencia_provincia_nombre
        ORDER BY cantidad DESC
        LIMIT 1
    """)
    hombre = cur.fetchone()
    if hombre:
        print(f"🧔 Provincia con más casos confirmados en hombres: {hombre[0]} ({hombre[1]} casos)")
    else:
        print("❌ No se encontraron casos confirmados en hombres.")

    conn.close()


def punto7_menor_proporcion_confirmados_sobre_poblacion():
    import csv

    conn = sqlite3.connect("covid.db")
    cur = conn.cursor()

    print("\n Punto 7: Menor proporción de casos confirmados respecto al Censo 2022")

    # Leer archivo del censo
    poblacion = {}
    try:
        with open("censo2022.csv", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                provincia = fila["provincia"].strip()
                poblacion[provincia] = int(fila["poblacion"])
    except FileNotFoundError:
        print("❌ Archivo censo2022.csv no encontrado.")
        return

    # Obtener casos confirmados por provincia
    cur.execute("""
        SELECT residencia_provincia_nombre, COUNT(*) AS cantidad
        FROM casos
        WHERE LOWER(clasificacion) LIKE '%confirmado%'
        GROUP BY residencia_provincia_nombre
    """)

    datos = []
    for prov, casos in cur.fetchall():
        prov_normalizado = prov.strip()
        if prov_normalizado in poblacion:
            pob = poblacion[prov_normalizado]
            proporcion = (casos / pob) * 100
            datos.append((prov_normalizado, casos, pob, proporcion))
        else:
            print(f"⚠️ Provincia no encontrada en censo: {prov_normalizado}")

    # Ordenar por menor proporción
    datos.sort(key=lambda x: x[3])  # por porcentaje

    # Mostrar resultados
    print(f"\n{'Provincia':<25} {'Casos':>10} {'Población':>12} {'% Confirmados':>15}")
    print("-" * 65)
    for prov, casos, pob, prop in datos:
        print(f"{prov:<25} {casos:>10} {pob:>12} {prop:>14.2f} %")

    print(f"\n✔️ Provincia con menor proporción: {datos[0][0]} ({datos[0][3]:.2f} %)")
    conn.close()


def punto8_proporcion_fallecidos_sobre_poblacion():
    import csv

    conn = sqlite3.connect("covid.db")
    cur = conn.cursor()

    print("\n Punto 8: Provincia con mayor proporción de fallecidos sobre la población (Censo 2022)")

    # Leer archivo censo
    poblacion = {}
    try:
        with open("censo2022.csv", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                provincia = fila["provincia"].strip()
                poblacion[provincia] = int(fila["poblacion"])
    except FileNotFoundError:
        print("❌ Archivo censo2022.csv no encontrado.")
        return

    # Obtener cantidad de fallecidos confirmados por provincia
    cur.execute("""
        SELECT residencia_provincia_nombre, COUNT(*) AS fallecidos
        FROM casos
        WHERE TRIM(UPPER(fallecido)) = 'SI'
        AND LOWER(clasificacion) LIKE '%confirmado%'
        GROUP BY residencia_provincia_nombre
    """)

    datos = []
    for prov, fallecidos in cur.fetchall():
        prov_normalizado = prov.strip()
        if prov_normalizado in poblacion:
            pob = poblacion[prov_normalizado]
            porcentaje = (fallecidos / pob) * 100
            datos.append((prov_normalizado, fallecidos, pob, porcentaje))
        else:
            print(f"⚠️ Provincia no encontrada en censo: {prov_normalizado}")

    # Ordenar de mayor a menor proporción
    datos.sort(key=lambda x: x[3], reverse=True)

    # Mostrar resultados
    print(f"\n{'Provincia':<30} {'Fallecidos':>10} {'Población':>12} {'% Fallecidos':>15}")
    print("-" * 70)
    for prov, f, p, porc in datos:
        print(f"{prov:<30} {f:>10} {p:>12} {porc:>14.2f} %")

    print(f"\n✔️ Provincia con mayor proporción: {datos[0][0]} ({datos[0][3]:.2f} %)")
    conn.close()


def punto9_indice_confirmados_por_sexo():
    import csv

    conn = sqlite3.connect("covid.db")
    cur = conn.cursor()

    print("\n Punto 9: Índice de casos confirmados por sexo (según Censo 2022)")

    # Leer el censo con datos por provincia y sexo
    poblacion = {}  # clave: (provincia, sexo) → valor: población
    try:
        with open("censo2022.csv", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                prov = fila["provincia"].strip()
                sexo = fila["sexo"].strip().upper()
                pob = int(fila["poblacion"])
                poblacion[(prov, sexo)] = pob
    except FileNotFoundError:
        print("❌ Archivo censo2022.csv no encontrado.")
        return

    # Contar confirmados por provincia y sexo desde la base de datos
    cur.execute("""
        SELECT residencia_provincia_nombre, TRIM(UPPER(sexo)) AS sexo, COUNT(*) AS cantidad
        FROM casos
        WHERE LOWER(clasificacion) LIKE '%confirmado%'
        AND sexo IN ('F', 'M')
        GROUP BY residencia_provincia_nombre, sexo
    """)

    # Agrupar los datos
    datos = {}
    total_confirmados = {"F": 0, "M": 0}
    total_poblacion = {"F": 0, "M": 0}

    for prov, sexo, cant in cur.fetchall():
        clave = (prov.strip(), sexo)
        pob = poblacion.get(clave)
        if pob:
            indice = (cant / pob) * 100
            if prov not in datos:
                datos[prov] = {}
            datos[prov][sexo] = (cant, pob, indice)

            total_confirmados[sexo] += cant
            total_poblacion[sexo] += pob
        else:
            print(f"⚠️ Faltan datos del censo para: {clave}")

    # Mostrar tabla por provincia
    print(f"\n{'Provincia':<20} {'Conf. F':>8} {'Pob. F':>9} {'% F':>8} | {'Conf. M':>8} {'Pob. M':>9} {'% M':>8}")
    print("-" * 75)
    for prov in sorted(datos):
        f_data = datos[prov].get("F", (0, 0, 0))
        m_data = datos[prov].get("M", (0, 0, 0))
        print(f"{prov:<20} {f_data[0]:>8} {f_data[1]:>9} {f_data[2]:>7.2f} | {m_data[0]:>8} {m_data[1]:>9} {m_data[2]:>7.2f}")

    # Totales nacionales
    print("\n📊 Índice total nacional por sexo:")
    for sexo in ["F", "M"]:
        if total_poblacion[sexo] > 0:
            indice_total = (total_confirmados[sexo] / total_poblacion[sexo]) * 100
            nombre = "Mujeres" if sexo == "F" else "Varones"
            print(f"- {nombre}: {indice_total:.2f} % (Confirmados: {total_confirmados[sexo]}, Población: {total_poblacion[sexo]})")

    # Conclusión
    f_index = (total_confirmados["F"] / total_poblacion["F"]) * 100
    m_index = (total_confirmados["M"] / total_poblacion["M"]) * 100
    if f_index > m_index:
        print("\n✔️ Mayor índice de casos confirmados en: MUJERES")
    elif m_index > f_index:
        print("\n✔️ Mayor índice de casos confirmados en: VARONES")
    else:
        print("\n✔️ Índice igual en ambos sexos.")

    conn.close()



def ver_valores_clasificacion():
    conn = sqlite3.connect("covid.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT clasificacion FROM casos
        WHERE clasificacion IS NOT NULL AND clasificacion != ''
    """)
    valores = cur.fetchall()

    print("\n🔍 Valores únicos en la columna 'clasificacion':")
    for v in valores:
        print(f"- '{v[0]}'")
    conn.close()


def diagnostico_confirmados_por_sexo():
    conn = sqlite3.connect("covid.db")
    cur = conn.cursor()

    print("\n🔎 Diagnóstico de la tabla 'casos'")

    # Ver sexo
    print("\n📌 Valores únicos en 'sexo':")
    cur.execute("SELECT sexo, COUNT(*) FROM casos GROUP BY sexo")
    for fila in cur.fetchall():
        print(f"- {repr(fila[0])}: {fila[1]} registros")

    # Ver clasificaciones que contienen 'confirmado'
    print("\n📌 Clasificaciones que contienen 'confirmado':")
    cur.execute("SELECT clasificacion, COUNT(*) FROM casos WHERE LOWER(clasificacion) LIKE '%confirmado%' GROUP BY clasificacion")
    for fila in cur.fetchall():
        print(f"- {repr(fila[0])}: {fila[1]} registros")

    # Ver cantidad de casos confirmados por sexo
    print("\n📌 Casos confirmados por sexo:")
    cur.execute("""
        SELECT sexo, COUNT(*) FROM casos
        WHERE LOWER(clasificacion) LIKE '%confirmado%'
        GROUP BY sexo
    """)
    for fila in cur.fetchall():
        print(f"- {repr(fila[0])}: {fila[1]} casos confirmados")

    conn.close()




# Menú principal
def menu():
    while True:
        print("\n====== MENÚ COVID ======")
        print("1. Crear tabla SQL")
        print("2. Cargar datos desde CSV")
        print("3. Punto 1 - Describir variables")
        print("4. Punto 2 - Valores faltantes en edad")
        print("5. Punto 3 - Edad promedio de fallecidos y outliers")
        print("6. Punto 4 - Intervalos de edad (Sturges)")
        print("7. Punto 5 - Intervalos de fallecidos por sexo")
        print("8. Punto 6 - Provincia con más confirmados por sexo")
        print("9. Punto 7 - Menor proporción de confirmados vs población")
        print("10. Punto 8 - Proporción fallecidos vs población (Censo)")
        print("11. Punto 9 - Índice de confirmados por sexo")
        print("89. Diagnóstico de sexo y confirmación (debug)")
        print("99. Ver valores únicos de 'clasificacion'")
        print("0. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            crear_tabla()
        elif opcion == "2":
            cargar_datos()
        elif opcion == "3":
            punto1_describir_variables()
        elif opcion == "4":
            punto2_edad_faltante()
        elif opcion == "5":
            punto3_promedio_edad_fallecidos()
        elif opcion == "6":
            punto4_sturges_intervalos()
        elif opcion == "7":
            punto5_mujeres_hombres_fallecidos_por_intervalo()
        elif opcion == "8":
            punto6_confirmados_por_provincia_y_sexo()
        elif opcion == "9":
            punto7_menor_proporcion_confirmados_sobre_poblacion()
        elif opcion == "10":
            punto8_proporcion_fallecidos_sobre_poblacion()
        elif opcion == "11":
            punto9_indice_confirmados_por_sexo()
        elif opcion == "89":
            diagnostico_confirmados_por_sexo()
        elif opcion == "99":
            ver_valores_clasificacion()
        elif opcion == "0":
            print("👋 Saliendo...")
            break
        else:
            print("❌ Opción no válida.")

# Ejecutar menú
if __name__ == "__main__":
    menu()

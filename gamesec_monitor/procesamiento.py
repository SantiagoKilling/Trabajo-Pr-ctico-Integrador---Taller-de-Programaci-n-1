def calcular_estadisticas_globales(sesiones: list[dict]) -> dict:
    total = len(sesiones)

    if total == 0:
        return {
            "total_sesiones" : 0,
            "ping_promedio" : 0.0,
            "duracion_promedio" : 0.0,
            "porcentaje_competitivas" : 0.0,
        }

    acumulador_ping = 0 #Arranca en 0 para ir sumando los milisegundos de latencia
    acumulador_duracion = 0.0 #Arranca en 0.0 para sumar la duración en minutos de cada partida 
    sesiones_competitivas = 0 # Arranca en 0 para contar cuántas partidas caen en los formatos de alta competencia

    for sesion in sesiones: #Itera una por una cada sesion presente en la lista de sesiones
        acumulador_ping += sesion["ping_promedio"] #Extrae el ping promedio y lo suma a la variable de acumulador de ping
        acumulador_duracion += sesion["duracion_minutos"] #Extrae la duracion en minutos y lo suma al acumulador de duración de cada partida

        if sesion["tipo_partida"] in ("Competitiva", "Torneo"): #En esta clasificación ignoro las partidas casuales para que no interfieran con las que van a ser clasificadas como competitivas
            sesiones_competitivas += 1

    ping_promedio = round(acumulador_ping / total, 2) #Saco el promedio del ping
    duracion_promedio = round(acumulador_duracion / total, 2) #La duración en promedio de las partidas
    porcentaje_competitivas = round((sesiones_competitivas / total) * 100, 2) #Saco el promedio de las partidas competitivas
    #Todos lo valores flotantes quedan redondeados a cifras de 2 decimales

    return {
        "total_sesiones": total,
        "ping_promedio" : ping_promedio,
        "duracion_promedio" : duracion_promedio,
        "porcentaje_competitivas" : porcentaje_competitivas,
    }
    # Toma toda la lista de diccionarios y devuelve 4 únicos que se almacenan en una variable unica en main.py

def analizar_por_servidor(sesiones: list[dict]) -> dict:
    acumuladores = {}

    for sesion in sesiones:
        srv = sesion["servidor"]

        if srv not in acumuladores:
            acumuladores[srv] = {
                "cantidad": 0,
                "suma_ping": 0,
                "suma_fps": 0
            }

        acumuladores[srv]["cantidad"] += 1
        acumuladores[srv]["suma_ping"] += sesion["ping_promedio"]
        acumuladores[srv]["suma_fps"] += sesion["fps_promedio"]

    resultado = {}
    for srv, datos in acumuladores.items():
        cant = datos["cantidad"]
        resultado[srv] = {
            "cantidad": cant,
            "ping_promedio": round(datos["suma_ping"] / cant, 2),
            "fps_promedio": round(datos["suma_fps"] / cant, 2)
        }

    return resultado

def clasificar_incidentes(sesiones: list[dict]) -> tuple[dict, list[dict]]:
    resumen = {
        "Normal": 0,
        "Sospechoso": 0,
        "Critico": 0
    }

    eventos_criticos = []

    for sesion in sesiones:
        reportes = sesion["reportes_trampa"]
        intentos = sesion["intentos_fallidos"]
        ping = sesion["ping_promedio"]

    # 1 regla. Punto crítico
        if reportes > 3 or intentos >= 4:
            resumen["Critico"] += 1

            #Construcción de la dinámica para el motivo del reporte
            motivos_del_reporte = []
            if reportes > 3:
                motivos_del_reporte.append(f"Exceso de reportes por trampa ({reportes})")
            if intentos >= 4:
                motivos_del_reporte.append(f"intentos fallidos ({intentos})")

            texto_motivo = " e ".join(motivos_del_reporte)

            eventos_criticos.append({
                "id_sesion" : sesion["id_sesion"],
                "jugador_id" : sesion["jugador_id"],
                "servidor" : sesion["servidor"],
                "motivo" : texto_motivo
            })

        # Segunda regla : En caso de ser sospechoso (solo si no fue crítico)
        elif (ping > 200 and intentos >= 2) or (reportes == 2):
            resumen["Sospechoso"] += 1


        # Tercera regla : Está todo normal, cualquier sesión que no encaje en las categorías anteriores (siga viaje tranquilo)
        else:
            resumen["Normal"] += 1

    return resumen, eventos_criticos
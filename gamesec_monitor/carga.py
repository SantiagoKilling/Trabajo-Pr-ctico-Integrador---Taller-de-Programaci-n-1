import csv
import os

def cargar_telemetria(ruta_archivo: str) -> list [dict]:
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"El archivo de la ruta '{ruta_archivo}' no existe.")

    sesiones = []

    with open(ruta_archivo, mode="r", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo) #Leo el archivo línea por línea y devuelvo cada fila como una lista

        for fila in lector:
            sesion = {
                "id_sesion": int(fila["id_sesion"]),
                "servidor": fila["servidor"],
                "jugador_id": fila["jugador_id"],
                "tipo_partida": fila["tipo_partida"],
                "ping_promedio": int(fila["ping_promedio"]),
                "fps_promedio": int(fila["fps_promedio"]),
                "duracion_minutos": float(fila["duracion_minutos"]),
                "intentos_fallidos": int(fila["intentos_fallidos"]),
                "reportes_trampa": int(fila["reportes_trampa"]),
            }
            sesiones.append(sesion)

    if not sesiones:
        raise ValueError("El archivo CSV no contiene registros")

    return sesiones

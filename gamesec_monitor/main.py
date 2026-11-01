# Menú interactivo, orquestación y exportación de reporte
from datetime import datetime
import os

from carga import cargar_telemetria
from procesamiento import (
    analizar_por_servidor,
    calcular_estadisticas_globales,
    clasificar_incidentes,
)

def exportar_reporte(sesiones: list[dict], ruta_salida: str = "reporte_gamesec.txt") -> None:
    """
    Genera un informe consolidado en archivo de texto respetando
    la estructura oficial requerida por la cátedra.
    """
    if not sesiones:
        print("No hay sesiones para generar el reporte.")
        return

    globales = calcular_estadisticas_globales(sesiones)
    regionales = analizar_por_servidor(sesiones)
    resumen_seg, criticos = clasificar_incidentes(sesiones)

    total = globales["total_sesiones"]
    pct_normal = round((resumen_seg["Normal"] / total) * 100, 2)
    pct_sospechoso = round((resumen_seg["Sospechoso"] / total) * 100, 2)
    pct_critico = round((resumen_seg["Critico"] / total) * 100, 2)

    fecha_actual = datetime.now().strftime("%d/%m/%Y")

    lineas = []
    lineas.append("=====================================================================")
    lineas.append("        REPORTE DE AUDITORIA Y TELEMETRIA - GAMESEC MONITOR          ")
    lineas.append("=====================================================================")
    lineas.append(f"Fecha de generacion: {fecha_actual}\n")

    # [1] RESUMEN GLOBAL OPERATIVO
    lineas.append("[1] RESUMEN GLOBAL OPERATIVO")
    lineas.append("=====================================================================")
    lineas.append(f"Total de sesiones procesadas: {globales['total_sesiones']}")
    lineas.append(f"Ping promedio global: {globales['ping_promedio']:.2f} ms")
    lineas.append(f"Duracion media de partida: {globales['duracion_promedio']:.2f} min")
    lineas.append(f"Partidas de alta competencia (Ranked/Torneo): {globales['porcentaje_competitivas']:.2f}%\n")

    # [2] RENDIMIENTO REGIONAL POR SERVIDOR
    lineas.append("[2] RENDIMIENTO REGIONAL POR SERVIDOR")
    lineas.append("=====================================================================")
    lineas.append(f"{'Servidor':<18} | {'Sesiones':<8} | {'Ping Promedio':<13} | {'FPS Promedio':<12}")
    lineas.append("-" * 62)
    for servidor, datos in regionales.items():
        lineas.append(
            f"{servidor:<18} | {datos['cantidad']:<8} | {datos['ping_promedio']:>8.2f} ms | {datos['fps_promedio']:>8.2f} fps"
        )
    lineas.append("")

    # [3] AUDITORIA DE SEGURIDAD E INCIDENTES
    lineas.append("[3] AUDITORIA DE SEGURIDAD E INCIDENTES")
    lineas.append("=====================================================================")
    lineas.append("Distribucion de estados de seguridad:")
    lineas.append(f"  Normales:     {resumen_seg['Normal']:>3} sesiones ({pct_normal:.2f}%)")
    lineas.append(f"  Sospechosos:  {resumen_seg['Sospechoso']:>3} sesiones ({pct_sospechoso:.2f}%)")
    lineas.append(f"  Criticos:     {resumen_seg['Critico']:>3} sesiones ({pct_critico:.2f}%)\n")
    lineas.append("Detalle de Sesiones Criticas Detectadas:")
    for ev in criticos:
        lineas.append(f"[!] Sesion #{ev['id_sesion']} - Jugador: {ev['jugador_id']} | Servidor: {ev['servidor']}")
        lineas.append(f"    Motivo: {ev['motivo']}")
    lineas.append("")

    # [4] CONCLUSIONES TECNICAS DEL EQUIPO
    lineas.append("[4] CONCLUSIONES TECNICAS DEL EQUIPO")
    lineas.append("=====================================================================")
    lineas.append("1. La infraestructura regional presenta variaciones notables de latencia, requiriendo optimizacion en nodos con ping medio elevado.")
    lineas.append("2. El motor heuristico identifico un volumen acotado pero critico de ataques de fuerza bruta y reportes reiterados por uso de software no autorizado.")
    lineas.append("3. Las sesiones en modalidades competitivas y torneo concentran la mayor estabilidad operativa, recomendando priorizar su ancho de banda en picos de trafico.")
    lineas.append("")
    lineas.append("=====================================================================")
    lineas.append("                       FIN DEL REPORTE GAMESEC                       ")
    lineas.append("=====================================================================")

    with open(ruta_salida, mode="w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print(f"\n[OK] Reporte exportado exitosamente en: '{ruta_salida}'")


def mostrar_menu():
    print("\n" + "=" * 32)
    print("        GAMESEC MONITOR         ")
    print("       PANEL DE CONTROL         ")
    print("=" * 32)
    print("1. Cargar y validar dataset")
    print("2. Ver estadisticas globales de servidores")
    print("3. Ver rendimiento por region de servidor")
    print("4. Auditar incidentes de seguridad (Criticos y Sospechosos)")
    print("5. Exportar reporte consolidado (reporte_gamesec.txt)")
    print("6. Salir")
    print("=" * 32)


def main():
    sesiones = []
    ruta_dataset = 'gamesec_monitor\gamesec_logs.csv'

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "1":
            try:
                sesiones = cargar_telemetria(ruta_dataset)
                print(f"\n[OK] Se cargaron y validaron {len(sesiones)} sesiones correctamente.")
            except (FileNotFoundError, ValueError) as err:
                print(f"\n[ERROR] Fallo al cargar el dataset: {err}")

        elif opcion == "2":
            if not sesiones:
                print("\n[ALERTA] Primero debe cargar el dataset (Opcion 1).")
            else:
                glob = calcular_estadisticas_globales(sesiones)
                print("\n--- RESUMEN GLOBAL OPERATIVO ---")
                print(f"Total de sesiones: {glob['total_sesiones']}")
                print(f"Ping promedio: {glob['ping_promedio']:.2f} ms")
                print(f"Duracion promedio: {glob['duracion_promedio']:.2f} min")
                print(f"Partidas de alta competencia: {glob['porcentaje_competitivas']:.2f}%")

        elif opcion == "3":
            if not sesiones:
                print("\n[ALERTA] Primero debe cargar el dataset (Opcion 1).")
            else:
                reg = analizar_por_servidor(sesiones)
                print("\n--- RENDIMIENTO POR REGION ---")
                print(f"{'Servidor':<18} | {'Cantidad':<8} | {'Ping Prom (ms)':<14} | {'FPS Prom'}")
                print("-" * 55)
                for srv, val in reg.items():
                    print(f"{srv:<18} | {val['cantidad']:<8} | {val['ping_promedio']:>14.2f} | {val['fps_promedio']:>8.2f}")

        elif opcion == "4":
            if not sesiones:
                print("\n[ALERTA] Primero debe cargar el dataset (Opcion 1).")
            else:
                resumen_seg, criticos = clasificar_incidentes(sesiones)
                print("\n--- AUDITORIA DE SEGURIDAD ---")
                print(f"Normales: {resumen_seg['Normal']}")
                print(f"Sospechosos: {resumen_seg['Sospechoso']}")
                print(f"Criticos: {resumen_seg['Critico']}")
                print(f"\nDetalle de sesiones criticas ({len(criticos)} incidentes):")
                for c in criticos:
                    print(f" [!] Sesion #{c['id_sesion']} | Jugador: {c['jugador_id']} | Servidor: {c['servidor']}")
                    print(f"     Motivo: {c['motivo']}")

        elif opcion == "5":
            if not sesiones:
                print("\n[ALERTA] Primero debe cargar el dataset (Opcion 1).")
            else:
                exportar_reporte(sesiones)

        elif opcion == "6":
            print("\nFinalizando ejecucion de GameSec Monitor. Hasta luego.")
            break

        else:
            print("\n[ALERTA] Opcion no valida. Seleccione un numero del 1 al 6.")


if __name__ == "__main__":
    main()
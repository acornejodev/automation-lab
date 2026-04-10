#!/usr/bin/env python3
"""
Script:      aci_ping_check.py
Descripción: Verifica conectividad a dispositivos ACI leyendo
             la lista desde un archivo YAML externo.
             Versión 2.0 — datos separados de la lógica.
Autor:       Alfonso Cornejo
Fecha:       Abril 2026
"""

# ── IMPORTACIONES ──────────────────────────────────────────────────────────────
import subprocess
import sys

# 'yaml' es un módulo externo — necesita instalarse con pip.
# Permite leer y escribir archivos en formato YAML desde Python.
# YAML (Yet Another Markup Language) es el formato estándar para
# archivos de configuración en Ansible, Kubernetes y herramientas DevOps.
import yaml

# 'pathlib' proporciona la clase Path para manejar rutas de archivos
# de forma elegante y compatible con cualquier sistema operativo.
from pathlib import Path


# ── FUNCIÓN 1: cargar_dispositivos ────────────────────────────────────────────
def cargar_dispositivos(ruta_yaml: str) -> list:
    """
    Lee el archivo YAML y retorna una lista plana de dispositivos.

    Parámetros:
        ruta_yaml (str): Ruta al archivo YAML de configuración.

    Retorna:
        list: Lista de dicts, cada uno con 'nombre' e 'ip'.

    Lanza:
        FileNotFoundError: Si el archivo no existe.
        yaml.YAMLError: Si el archivo tiene sintaxis YAML inválida.
    """

    # Path() convierte el string en un objeto de ruta manejable
    archivo = Path(ruta_yaml)

    # Verificamos que el archivo exista antes de intentar abrirlo.
    # Es mejor dar un error claro que dejar que Python falle con un
    # mensaje críptico de FileNotFoundError más adelante.
    if not archivo.exists():
        print(f"Error: No se encontró el archivo '{ruta_yaml}'")
        print("Verifica que el archivo exista en la misma carpeta que el script.")
        sys.exit(1)

    # 'with open()' abre el archivo y lo cierra automáticamente al terminar.
    # Es la forma correcta de abrir archivos en Python — evita que queden
    # abiertos si ocurre un error dentro del bloque.
    # encoding="utf-8" especifica la codificación de caracteres.
    with open(archivo, encoding="utf-8") as f:
        # yaml.safe_load() lee el YAML y lo convierte en estructuras Python:
        # - Mappings YAML (clave: valor) → diccionarios Python {}
        # - Sequences YAML (- item)      → listas Python []
        # - Strings, números, booleanos  → tipos Python equivalentes
        # 'safe_load' (vs 'load') es más seguro porque no ejecuta código Python
        # embebido en el YAML — siempre usa safe_load.
        datos = yaml.safe_load(f)

    # Construimos una lista plana juntando todas las categorías.
    # 'datos' ahora es un dict Python que refleja la estructura del YAML:
    # {
    #   "aci_infrastructure": {
    #     "apics": [{"nombre": "APIC-1", "ip": "10.10.20.14"}, ...],
    #     "conectividad_general": [{"nombre": "Google DNS", "ip": "8.8.8.8"}, ...]
    #   }
    # }
    todos = []
    infraestructura = datos.get("aci_infrastructure", {})

    # .items() retorna pares (clave, valor) del diccionario.
    # Iteramos sobre cada categoría (apics, conectividad_general, etc.)
    for categoria, dispositivos in infraestructura.items():
        # 'dispositivos' es la lista de dicts de esa categoría.
        # La extendemos a nuestra lista plana 'todos'.
        todos.extend(dispositivos)

    return todos


# ── FUNCIÓN 2: check_host (sin cambios respecto a v1) ─────────────────────────
def check_host(hostname: str, count: int = 2) -> bool:
    """Verifica si un host responde a ping. Retorna True/False."""
    resultado = subprocess.run(
        ["ping", "-n", str(count), hostname],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return resultado.returncode == 0


# ── FUNCIÓN 3: verificar_dispositivos (mejorada) ──────────────────────────────
def verificar_dispositivos(dispositivos: list) -> None:
    """
    Recibe lista de dicts {'nombre': ..., 'ip': ...} y verifica cada uno.
    """
    print("\n" + "=" * 60)
    print("  ACI Infrastructure Check — Verificación de conectividad")
    print("=" * 60)

    alcanzables = 0
    no_alcanzables = 0

    for dispositivo in dispositivos:
        # Ahora cada elemento es un dict, no solo un string.
        # Accedemos a sus valores con la notación dict["clave"].
        nombre = dispositivo["nombre"]
        ip = dispositivo["ip"]

        if check_host(ip):
            # :.<30 rellena con puntos a la derecha hasta 30 caracteres.
            # Esto alinea los resultados en columnas para mejor legibilidad.
            print(f"  [ OK ]  {nombre:<28} {ip}")
            alcanzables += 1
        else:
            print(f"  [FAIL]  {nombre:<28} {ip}")
            no_alcanzables += 1

    print("-" * 60)
    print(f"  Total: {alcanzables} alcanzables | {no_alcanzables} no alcanzables")
    print("=" * 60 + "\n")

    if no_alcanzables > 0:
        sys.exit(1)


# ── PUNTO DE ENTRADA ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Ahora leemos los dispositivos del archivo YAML en lugar de
    # tenerlos hardcodeados. Si cambias el YAML, no tocas el código.
    dispositivos = cargar_dispositivos("dispositivos.yaml")
    verificar_dispositivos(dispositivos)
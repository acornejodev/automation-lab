#!/usr/bin/env python3
"""
Script:      aci_ping_check.py
Descripción: Verifica conectividad básica a dispositivos de infraestructura ACI.
             En un entorno real verificarías APICs, spines y leafs.
Autor:       Tu Nombre
Fecha:       Marzo 2026
"""

# ── IMPORTACIONES ──────────────────────────────────────────────────────────────
# "import" trae módulos (bibliotecas) que extienden lo que Python puede hacer.
# Python tiene muchos módulos incluidos por defecto — no necesitas instalarlos.

import subprocess
# subprocess permite ejecutar comandos del sistema operativo desde Python.
# Es como escribir un comando en la terminal, pero desde dentro de tu script.
# Lo usaremos para ejecutar el comando "ping".

import sys
# sys da acceso a funciones del intérprete Python, como sys.exit() para
# terminar el script con un código de error específico.


# ── FUNCIÓN 1: check_host ──────────────────────────────────────────────────────
def check_host(hostname: str, count: int = 2) -> bool:
    """
    Verifica si un host responde a ping.

    El bloque de texto entre triple comillas se llama 'docstring'.
    Documenta qué hace la función, sus parámetros y qué retorna.
    Buena práctica obligatoria en código de producción.

    Parámetros:
        hostname (str): IP o nombre del host. 'str' indica el tipo esperado.
        count (int): Paquetes ICMP a enviar. '= 2' es el valor por defecto
                     si no se pasa este argumento al llamar la función.

    Retorna:
        bool: True si el host responde, False si no responde.
    """

    # subprocess.run() ejecuta un comando externo y espera a que termine.
    # El primer argumento es una lista con el comando y sus argumentos.
    # En Windows, ping usa -n para el count (en Linux/Mac es -c).
    resultado = subprocess.run(
        ["ping", "-n", str(count), hostname],
        # stdout=subprocess.DEVNULL descarta la salida normal del ping.
        # Sin esto, cada ping imprimiría sus líneas en pantalla — no queremos eso.
        stdout=subprocess.DEVNULL,
        # stderr=subprocess.DEVNULL descarta los mensajes de error del ping.
        stderr=subprocess.DEVNULL,
    )

    # subprocess.run() retorna un objeto CompletedProcess.
    # Su atributo .returncode guarda el código de salida del comando:
    #   0  = el comando exitó sin errores (el host respondió al ping)
    #   !0 = el comando falló (host no responde, no existe, timeout)
    # La expresión "resultado.returncode == 0" evalúa a True o False.
    return resultado.returncode == 0


# ── FUNCIÓN 2: verificar_dispositivos ─────────────────────────────────────────
def verificar_dispositivos(dispositivos: list) -> None:
    """
    Itera sobre una lista de dispositivos y verifica cada uno.

    Parámetros:
        dispositivos (list): Lista de strings con IPs o FQDNs.

    Retorna:
        None — esta función no retorna un valor, solo imprime resultados.
              'None' es como decir "void" en otros lenguajes.
    """

    # Imprimimos un encabezado visual para el reporte
    print("\n" + "=" * 55)
    print("  ACI Infrastructure Check — Verificación de conectividad")
    print("=" * 55)

    # Inicializamos contadores. Empiezan en 0 y los incrementamos
    # dentro del loop por cada resultado OK o FAIL.
    alcanzables = 0
    no_alcanzables = 0

    # El loop 'for' itera sobre cada elemento de la lista.
    # En cada iteración, 'dispositivo' toma el valor del elemento actual.
    for dispositivo in dispositivos:

        # Llamamos a check_host() pasando el dispositivo actual.
        # La función retorna True o False, que usamos directamente en el if.
        if check_host(dispositivo):
            # f-string: las llaves {} dentro de f"..." insertan variables.
            # :.<20 es un formato que rellena con puntos hasta 20 caracteres.
            print(f"  [  OK  ]  {dispositivo}")
            alcanzables += 1          # "+= 1" es equivalente a "= alcanzables + 1"
        else:
            print(f"  [ FAIL ]  {dispositivo}")
            no_alcanzables += 1

    # Imprimimos el resumen final
    print("-" * 55)
    print(f"  Resultado: {alcanzables} alcanzables | {no_alcanzables} no alcanzables")
    print("=" * 55 + "\n")

    # Retornamos un código de error si hay dispositivos que no responden.
    # Esto es importante para pipelines de CI/CD en fases futuras:
    # un script que retorna 1 indica fallo, 0 indica éxito.
    if no_alcanzables > 0:
        sys.exit(1)


# ── PUNTO DE ENTRADA ───────────────────────────────────────────────────────────
# Esta condición verifica si este archivo se ejecuta DIRECTAMENTE
# (ej: python aci_ping_check.py) versus si es importado por otro script.
# Cuando Python ejecuta un archivo directamente, la variable especial
# __name__ toma el valor "__main__". Si es importado, toma el nombre del módulo.
# Es una convención estándar que SIEMPRE debes incluir en tus scripts.
if __name__ == "__main__":

    # Lista de dispositivos a verificar.
    # En scripts de producción esto vendría de un archivo YAML o CSV externo.
    # Por ahora lo definimos aquí directamente para concentrarnos en Git y Python.
    dispositivos_aci = [
        "8.8.8.8",        # Google DNS — debe responder (OK esperado)
        "1.1.1.1",        # Cloudflare DNS — debe responder (OK esperado)
        "192.168.1.1",    # Tu gateway local — puede variar según tu red
        "10.0.0.1",       # IP ficticia de APIC-1 — no existe (FAIL esperado)
        "10.0.0.2",       # IP ficticia de APIC-2 — no existe (FAIL esperado)
        "172.16.0.1"      # IP ficticia de un leaf — no existe (FAIL esperado)
    ]

    # Llamamos a la función principal con nuestra lista
    verificar_dispositivos(dispositivos_aci)
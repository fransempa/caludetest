#!/usr/bin/env python3
"""Elimina los archivos de una carpeta cuya última modificación fue hace más de 6 meses.

Uso:
    python3 eliminar_antiguos.py [ruta] [--recursivo] [--simular] [--si]

Si no se indica la ruta, el programa la pide por consola.
"""
import argparse
import os
import sys
import time

SEIS_MESES_SEGUNDOS = 183 * 24 * 60 * 60  # ~6 meses (183 días)


def buscar_antiguos(carpeta, recursivo):
    limite = time.time() - SEIS_MESES_SEGUNDOS
    antiguos = []
    if recursivo:
        entradas = (
            os.path.join(raiz, nombre)
            for raiz, _, nombres in os.walk(carpeta)
            for nombre in nombres
        )
    else:
        entradas = (os.path.join(carpeta, n) for n in os.listdir(carpeta))
    for ruta in entradas:
        if os.path.isfile(ruta) or os.path.islink(ruta):
            try:
                if os.lstat(ruta).st_mtime < limite:
                    antiguos.append(ruta)
            except OSError as e:
                print(f"No se pudo leer {ruta}: {e}", file=sys.stderr)
    return antiguos


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("ruta", nargs="?", help="carpeta a limpiar")
    parser.add_argument("--recursivo", action="store_true", help="incluir subcarpetas")
    parser.add_argument("--simular", action="store_true", help="solo listar, sin borrar")
    parser.add_argument("--si", action="store_true", help="no pedir confirmación")
    args = parser.parse_args()

    ruta = args.ruta or input("Ruta de la carpeta: ").strip()
    ruta = os.path.abspath(os.path.expanduser(ruta))
    if not os.path.isdir(ruta):
        sys.exit(f"Error: '{ruta}' no es una carpeta válida.")

    antiguos = buscar_antiguos(ruta, args.recursivo)
    if not antiguos:
        print("No hay archivos con más de 6 meses sin modificar.")
        return

    print(f"Archivos con más de 6 meses sin modificar ({len(antiguos)}):")
    for a in antiguos:
        print(f"  {a}")

    if args.simular:
        print("Modo simulación: no se borró nada.")
        return

    if not args.si and input("¿Eliminarlos? (s/N): ").strip().lower() not in ("s", "si", "sí"):
        print("Cancelado.")
        return

    borrados = 0
    for a in antiguos:
        try:
            os.remove(a)
            borrados += 1
        except OSError as e:
            print(f"No se pudo eliminar {a}: {e}", file=sys.stderr)
    print(f"Eliminados {borrados} de {len(antiguos)} archivos.")


if __name__ == "__main__":
    main()

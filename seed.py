"""Crea (o recrea) la base de datos de la demo.

Uso:  python seed.py              -> 60 000 usuarios + usuarios de prueba
      python seed.py --usuarios 1000
Detenga el servidor antes de ejecutarlo.
"""
import argparse
import time

import config
from app.demo_data import DEMO_USERS, create_database


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--usuarios", type=int, default=config.N_USERS, help="usuarios de relleno")
    args = parser.parse_args()

    start = time.monotonic()
    total = create_database(config.DB_PATH, n_users=args.usuarios)
    total_txt = "{:,}".format(total).replace(",", ".")
    print("Base de datos creada en {} ({} usuarios, {:.1f} s)".format(
        config.DB_PATH, total_txt, time.monotonic() - start))
    print("Usuarios de prueba: " + ", ".join(u for u, _, _ in DEMO_USERS) + "  (clave: Clave*2024)")


if __name__ == "__main__":
    main()

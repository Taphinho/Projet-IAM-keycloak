"""Initialize local secrets without replacing an existing environment."""
import os
import argparse
from pathlib import Path
import secrets
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extend", action="store_true", help="Ajouter les variables manquantes sans remplacer les valeurs existantes")
    args = parser.parse_args()
    existing = dotenv_values(ROOT / ".env") if args.extend else {}
    values = []
    for line in (ROOT / ".env.example").read_text().splitlines():
        if not line or line.startswith("#"):
            values.append(line)
            continue
        key, value = line.split("=", 1)
        if key in existing:
            continue
        if not value and ("PASSWORD" in key or "SECRET" in key):
            value = secrets.token_hex(32)
        values.append(f"{key}={value}")
    try:
        flags = os.O_CREAT | os.O_WRONLY | (os.O_APPEND if args.extend else os.O_EXCL)
        fd = os.open(ROOT / ".env", flags, 0o600)
    except FileExistsError:
        raise SystemExit(".env existe : aucune modification effectuée.")
    with os.fdopen(fd, "w") as stream:
        stream.write("\n" + "\n".join(values) + "\n")
    print("Secrets locaux générés dans .env (0600).")

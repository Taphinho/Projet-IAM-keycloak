"""Build an allowlisted source archive; refuse known local secrets."""
from pathlib import Path
import zipfile

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = ("app", "app_b", "docs", "ldap", "postgres", "scripts", "tests", "keycloak", ".github")
FILES = ("README.md", ".gitignore", ".dockerignore", ".env.example", "Dockerfile",
         "requirements.txt", "compose.yaml", "compose.apps.yaml")


def source_files():
    paths = [ROOT / name for name in FILES]
    for directory in DIRECTORIES:
        paths.extend((ROOT / directory).rglob("*"))
    result = []
    for path in paths:
        if path.is_symlink():
            raise ValueError("Lien symbolique refusé dans les sources")
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix in (".pyc", ".sqlite3", ".key", ".pem"):
            continue
        if ".sqlite3" in path.name or (path.name.startswith(".env") and path.name != ".env.example"):
            continue
        result.append(path)
    return sorted(set(result))


def audit(paths):
    values = dotenv_values(ROOT / ".env")
    secrets = [value.encode() for key, value in values.items()
               if value and len(value) >= 16 and ("PASSWORD" in key or "SECRET" in key)]
    private_headers = [b"-----BEGIN " + kind + b" PRIVATE KEY-----"
                       for kind in (b"RSA", b"EC", b"OPENSSH")]
    private_headers.append(b"-----BEGIN " + b"PRIVATE KEY-----")
    for path in paths:
        data = path.read_bytes()
        if any(secret in data for secret in secrets) or any(header in data for header in private_headers):
            raise ValueError(f"Publication refusée : secret détecté dans {path.relative_to(ROOT)}")


if __name__ == "__main__":
    paths = source_files()
    audit(paths)
    destination = ROOT / "dist/enterprise-iam-lab-source.zip"
    destination.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            archive.write(path, path.relative_to(ROOT))
    print(f"Archive vérifiée : {destination.name} ({len(paths)} fichiers).")

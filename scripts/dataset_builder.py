from pathlib import Path
import requests

def download_image(url: str, dest_folder: Path, filename: str):
    dest_folder.mkdir(parents=True, exist_ok=True)
    file_path = dest_folder / filename

    if file_path.exists():
        print(f"{file_path} já existe. Pulando download.")
        return

    try:
        resp = requests.get(url)
        resp.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(resp.content)
        print(f"Baixado {url} para {file_path}")
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")

# Teste / Use-case
#url = "https://github.com/ondyari/FaceForensics/raw/master/images/ex_original.png"
#download_image(url, Path("data/raw/test/original"), "ex_original.png")
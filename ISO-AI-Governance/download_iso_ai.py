#!/usr/bin/env python3
"""Descarga masiva autorizada de vistas previas ISO/IEC y publicaciones gratuitas NIST.
Uso: python ISO-AI-Governance/download_iso_ai.py
Desde un workflow: python ISO-AI-Governance/download_iso_ai.py --nist-only
No publica ni redistribuye documentos ISO sujetos a copyright.
"""
import argparse
import csv
import pathlib
import urllib.request
import urllib.error
import urllib.parse
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
CATALOG = HERE / "CATALOGO_40_NORMAS.csv"
FOLDER = HERE / "ISO_IA_5_Niveles"
RESULTS = FOLDER / "ESTADO_DESCARGAS.csv"
NIST = [
    ("01_Gobierno_Estrategico", "NIST_AI_RMF_100-1_COMPLETO.pdf", "https://nvlpubs.nist.gov/nistpubs/AI/NIST.AI.100-1.pdf"),
    ("01_Gobierno_Estrategico", "NIST_GENAI_600-1_COMPLETO.pdf", "https://nvlpubs.nist.gov/nistpubs/AI/NIST.AI.600-1.pdf"),
]

def get_pdf(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 ISO-AI-Research/1.0", "Accept": "application/pdf,*/*"})
        with urllib.request.urlopen(request, timeout=25) as response:
            data = response.read(12 * 1024 * 1024 + 1)
        if not data.lstrip().startswith(b"%PDF-") or len(data) > 12 * 1024 * 1024:
            return "ERROR_NO_PDF_O_TAMANO"
        path.write_bytes(data)
        return "DESCARGADO_PDF"
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
        return "ERROR_" + type(error).__name__ + "_" + str(error)[:95].replace("\n", " ")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nist-only", action="store_true", help="GitHub Action: solo PDFs NIST, libre distribución")
    args = parser.parse_args()
    rows = []
    with CATALOG.open(encoding="utf-8-sig", newline="") as file:
        catalog = list(csv.DictReader(file))
    for item in catalog:
        group = item["nivel"]
        folder = FOLDER / group
        folder.mkdir(parents=True, exist_ok=True)
        ref = item["norma"]
        source = item["enlace_iso_oficial"]
        name = ref.replace("ISO/IEC ", "").replace("/", "_").replace(" ", "_").replace(":", "_")
        (folder / (name + "_ENLACE_OFICIAL.url")).write_text(
            "[InternetShortcut]\nURL=" + source + "\n", encoding="utf-8"
        )
        status = "SOLO_ENLACE_OFICIAL"
        if not args.nist_only:
            status = get_pdf(item["vista_previa_ansi_candidata"], folder / (name + "_PREVIEW.pdf"))
        rows.append([group, ref, status, source, item["vista_previa_ansi_candidata"]])
        print(group, ref, status, flush=True)
    for group, name, url in NIST:
        status = get_pdf(url, FOLDER / group / name)
        rows.append([group, name, status, url, ""])
        print(group, name, status, flush=True)
    with RESULTS.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["Nivel", "Norma_o_documento", "Estado", "Fuente", "Vista_previa"])
        writer.writerows(rows)
    zippath = HERE / ("ISO_IA_NIST_Recursos_Completos.zip" if args.nist_only else "ISO_IA_Descargas_y_Previews.zip")
    with zipfile.ZipFile(zippath, "w", zipfile.ZIP_DEFLATED) as archive:
        for file in FOLDER.rglob("*"):
            if not file.is_file():
                continue
            # Copyright: previews descargadas desde ANSI permanecen en carpeta local
            # y NO se empaquetan para redistribución en GitHub.
            if args.nist_only or "_PREVIEW.pdf" not in file.name:
                archive.write(file, file.relative_to(HERE))
    print("\nZIP:", zippath)
    print("Vistas previas obtenidas para consulta individual:",
          sum(row[2] == "DESCARGADO_PDF" for row in rows[:len(catalog)]))
    print("PDFs completos NIST:", sum(row[2] == "DESCARGADO_PDF" for row in rows[len(catalog):]))

if __name__ == "__main__":
    main()

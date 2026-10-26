import json
import urllib.request
from datetime import datetime
import xml.etree.ElementTree as ET
import os

# ----------------------------------------------------------------------
# LISTA COMPLETA DE CANALES DE 40MEDIA GROUP
# ----------------------------------------------------------------------
CANALES = [
    {
        "id": "ent-channel",
        "name": "ENT Channel",
        "url": "https://api.40mediagroup.com/xmltv/programacion/entchannel/guia.json"
    },
    {
        "id": "ent-family",
        "name": "ENT Family",
        "url": "https://api.40mediagroup.com/xmltv/programacion/entfamily/guia.json"
    },
    {
        "id": "total-music",
        "name": "Total Music",
        "url": "https://api.40mediagroup.com/xmltv/programacion/totalmusic/guia.json"
    },
    {
        "id": "total-music-80s",
        "name": "Total Music 80s",
        "url": "https://api.40mediagroup.com/xmltv/programacion/totalmusic80s/guia.json"
    },
    {
        "id": "total-music-00s",
        "name": "Total Music 00s",
        "url": "https://api.40mediagroup.com/xmltv/programacion/totalmusic00s/guia.json"
    },
    {
        "id": "ent-extreme",
        "name": "ENT Extreme",
        "url": "https://api.40mediagroup.com/xmltv/programacion/entextreme/guia.json"
    },
    {
        "id": "ent-comedy",
        "name": "ENT Comedy",
        "url": "https://api.40mediagroup.com/xmltv/programacion/entcomedy/guia.json"
    },
    {
        "id": "ent-movies",
        "name": "ENT Movies",
        "url": "https://api.40mediagroup.com/xmltv/programacion/entmovies/guia.json"
    },
    {
        "id": "ent-drama",
        "name": "ENT Drama",
        "url": "https://api.40mediagroup.com/xmltv/programacion/entdrama/guia.json"
    },
    {
        "id": "ent-classic",
        "name": "ENT Classic",
        "url": "https://api.40mediagroup.com/xmltv/programacion/entclassic/guia.json"
    },
    {
        "id": "ent-life",
        "name": "ENT Life",
        "url": "https://api.40mediagroup.com/xmltv/programacion/entlife/guia.json"
    }
]

OUTPUT_FILE = "epg.xml"
# ----------------------------------------------------------------------

def iso_to_xmltv(iso_str: str) -> str:
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return dt.strftime("%Y%m%d%H%M%S %z")

def main():
    # 1. Cargar el XML existente o crear uno nuevo si no existe
    if os.path.exists(OUTPUT_FILE):
        try:
            tree = ET.parse(OUTPUT_FILE)
            root = tree.getroot()
        except ET.ParseError:
            root = ET.Element("tv", {"generator-info-name": "Automated-EPG"})
    else:
        root = ET.Element("tv", {"generator-info-name": "Automated-EPG"})

    # 2. Iterar sobre cada canal configurado en la lista
    for canal in CANALES:
        channel_id = canal["id"]
        json_url = canal["url"]
        
        print(f"Procesando canal: {canal['name']} ({channel_id})...")
        
        try:
            req = urllib.request.Request(json_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception as e:
            print(f"❌ Error al descargar el JSON para {channel_id}: {e}")
            continue

        channel_name = data.get("channel", canal["name"])
        programmes = data.get("programmes", [])

        # 3. Eliminar datos viejos de ESTE canal específico para evitar duplicados al actualizar
        for channel_elem in root.findall("channel"):
            if channel_elem.get("id") == channel_id:
                root.remove(channel_elem)
                
        for prog_elem in root.findall("programme"):
            if prog_elem.get("channel") == channel_id:
                root.remove(prog_elem)

        # 4. Insertar la cabecera del canal
        channel_elem = ET.SubElement(root, "channel", {"id": channel_id})
        display_name = ET.SubElement(channel_elem, "display-name")
        display_name.text = channel_name

        # 5. Insertar toda la programación del canal
        for prog in programmes:
            prog_elem = ET.SubElement(root, "programme", {
                "channel": channel_id,
                "start": iso_to_xmltv(prog["start"]),
                "stop": iso_to_xmltv(prog["stop"])
            })

            if prog.get("title"):
                ET.SubElement(prog_elem, "title", {"lang": "es"}).text = prog["title"]

            if prog.get("desc"):
                ET.SubElement(prog_elem, "desc", {"lang": "es"}).text = prog["desc"]

            if prog.get("category"):
                ET.SubElement(prog_elem, "category", {"lang": "es"}).text = prog["category"]

            if prog.get("icon"):
                ET.SubElement(prog_elem, "icon", {"src": prog["icon"]})

    # 6. Guardar el archivo XML unificado final
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    print(f"\n¡Proceso finalizado! Archivo '{OUTPUT_FILE}' actualizado con éxito para todos los canales.")

if __name__ == "__main__":
    main()

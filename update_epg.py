import json
import urllib.request
from datetime import datetime
import xml.etree.ElementTree as ET

# ----------------------------------------------------------------------
# REEMPLAZÁ ESTA URL por el enlace real donde el canal sube el JSON:
JSON_URL = "https://api.40mediagroup.com/xmltv/programacion/entextreme/guia.json"
# ----------------------------------------------------------------------

CHANNEL_ID = "ent-extreme"
OUTPUT_FILE = "epg.xml"

def iso_to_xmltv(iso_str: str) -> str:
    dt = datetime.fromisoformat(iso_str)
    return dt.strftime("%Y%m%d%H%M%S %z")

def main():
    req = urllib.request.Request(JSON_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))

    channel_name = data.get("channel", "ENT Extreme")
    programmes = data.get("programmes", [])

    root = ET.Element("tv", {"generator-info-name": "Automated-EPG"})

    channel_elem = ET.SubElement(root, "channel", {"id": CHANNEL_ID})
    display_name = ET.SubElement(channel_elem, "display-name")
    display_name.text = channel_name

    for prog in programmes:
        prog_elem = ET.SubElement(root, "programme", {
            "channel": CHANNEL_ID,
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

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    main()

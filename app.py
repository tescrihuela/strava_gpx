import streamlit as st
from io import BytesIO
from lxml import etree
import random
import datetime


def smooth_hr(previous_hr, target_hr, alpha=0.2):
    """
    Lissage exponentiel pour la fréquence cardiaque.
    - previous_hr : HR à n-1
    - target_hr : HR cible
    - alpha : Coefficient de lissage (plus bas = plus lisse)
    """
    return int(previous_hr + alpha * (target_hr - previous_hr))


def add_hr_to_gpx(file, base_hr, alpha=0.2):
    """
    Ajoute des fréquences cardiaques lissées dans un fichier GPX existant.
    """
    try:
        # Lire le fichier GPX
        parser = etree.XMLParser(remove_blank_text=False)
        tree = etree.parse(file, parser)
        root = tree.getroot()

        # Extraire les espaces de noms
        nsmap = root.nsmap
        default_ns = nsmap.get(None)  # Espace de noms par défaut

        if not default_ns:
            raise ValueError("Impossible de trouver un espace de noms par défaut dans le fichier GPX.")

        # Définir les espaces de noms explicites pour XPath
        ns = {'ns': default_ns, 'gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'}

        # Parcourir toutes les balises <time> en excluant celles sous <metadata>
        previous_hr = base_hr  # Initialise HR avec la valeur donnée par l'utilisateur
        for time_elem in root.xpath('.//ns:time', namespaces=ns):
            parent = time_elem.getparent()  # Récupérer le parent de <time>
            
            # Vérifier que le parent n'est pas <metadata>
            if parent.tag == f"{{{default_ns}}}metadata":
                continue  # Ignorer les <time> sous <metadata>

            if parent is not None:
                # Générer une valeur lissée pour HR
                target_hr = base_hr + int(random.gauss(0, 5))  # Ajouter une légère variation autour de la base
                smoothed_hr = smooth_hr(previous_hr, target_hr, alpha)
                previous_hr = smoothed_hr  # Mettre à jour HR précédent

                # Créer une balise <extensions> si nécessaire
                extensions = etree.Element('extensions')
                trackpoint_ext = etree.SubElement(extensions, '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}TrackPointExtension')
                hr_elem = etree.SubElement(trackpoint_ext, '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}hr')
                hr_elem.text = str(smoothed_hr)

                # Insérer <extensions> juste après <time>
                parent.insert(parent.index(time_elem) + 1, extensions)

        # Sauvegarder le contenu mis à jour
        updated_gpx = BytesIO()
        tree.write(updated_gpx, encoding='utf-8', xml_declaration=True, pretty_print=True)
        return updated_gpx.getvalue().decode('utf-8')

    except Exception as e:
        st.error(f"Erreur lors du traitement du fichier : {e}")
        return None


def display_gpx(date, time, base_hr, minutes, alpha=0.2):
    """
    Génère un nouveau fichier GPX avec des fréquences cardiaques lissées.
    """
    gpx_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" creator="Generated GPX" version="1.1">
  <trk>
    <name>Generated</name>
    <trkseg>"""
    start_datetime = datetime.datetime.strptime(f"{date}T{time}", "%Y-%m-%dT%H:%M")
    previous_hr = base_hr  # Initialise HR
    for i in range(minutes):
        current_datetime = start_datetime + datetime.timedelta(minutes=i)
        target_hr = base_hr + int(random.gauss(0, 5))  # Variation autour de la base
        smoothed_hr = smooth_hr(previous_hr, target_hr, alpha)
        previous_hr = smoothed_hr  # Mettre à jour HR précédent

        gpx_content += f"""
      <trkpt lat="49.427809" lon="1.1038437">
        <time>{current_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")}</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>{smoothed_hr}</gpxtpx:hr>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>"""
    gpx_content += "</trkseg></trk></gpx>"
    return gpx_content


# Interface Streamlit
st.title('Traitement des fichiers GPX')

# Onglet 1 : Génération d'un fichier GPX
tab1, tab2 = st.tabs(['Créer GPX', 'Ajouter HR à un GPX'])

alpha = 0.8
with tab1:
    # Génération d'un fichier GPX
    date = st.date_input('Choisir une date :', datetime.date.today())
    time = st.text_input('Choisir une heure :', '19:30')
    base_hr = st.number_input('Entrez la valeur de HR :', value=140)
    minutes = st.number_input("Entrez la durée en minutes :", min_value=0, value=75)

    if st.button('Afficher GPX'):
        gpx_content = display_gpx(date, time, base_hr, minutes, alpha)
        st.text_area('Contenu GPX :', gpx_content, height=300)
        st.download_button(label='Télécharger', data=gpx_content, file_name='generated.gpx', mime='text/xml')

with tab2:
    # Modification d'un fichier GPX existant
    uploaded_file = st.file_uploader("Uploader un fichier GPX :", type=['gpx'])
    base_hr = st.number_input('Entrez la valeur de HR :', value=142)

    if uploaded_file is not None:
        updated_gpx_content = add_hr_to_gpx(uploaded_file, base_hr, alpha)
        if updated_gpx_content:
            st.text_area('Contenu modifié du fichier GPX :', updated_gpx_content, height=300)
            st.download_button(label='Télécharger le fichier modifié', data=updated_gpx_content, file_name='updated.gpx', mime='text/xml')

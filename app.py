import streamlit as st
import datetime
import urllib.parse
import random

def display_gpx(date, time, hr, minutes):
    gpx_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" creator="TomTomWatch v1.10 (05.11.2023 @ 20:42:57 CET)" version="1.1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd">
  <trk>
    <name>Five</name>
    <type>Soccer</type>
    <desc>Created by: TomTomWatch v1.10 (05.11.2023 @ 20:42:57 CET). Logged by: 'TomTom GPS Watch' (serial: HR2426G00529).</desc>
    <trkseg>"""
        
    if minutes:
        start_datetime = datetime.datetime.strptime(f"{date}T{time}", "%Y-%m-%dT%H:%M") - datetime.timedelta(hours=1)
        end_datetime = start_datetime + datetime.timedelta(minutes=int(minutes))
        current_datetime = start_datetime
        while current_datetime < end_datetime:
            hr_with_noise = int(hr) + int(random.gauss(0, 10)) # Variance de 10
            gpx_content += f"""
      <trkpt lat="49.427809" lon="1.1038437">
        <time>{current_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")}</time>
        <hdop>6</hdop>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>{hr_with_noise}</gpxtpx:hr>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>"""
            current_datetime += datetime.timedelta(minutes=1)
        
        # Ajout d'un bloc trkpt supplémentaire à la fin de la séance
        gpx_content += f"""
      <trkpt lat="49.427809" lon="1.1038437">
        <time>{end_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")}</time>
        <hdop>6</hdop>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>{hr}</gpxtpx:hr>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>"""
        
    gpx_content += "</trkseg></trk></gpx>"
    
    return gpx_content

st.title('Generate GPX')

date = st.date_input('Choisir une date :', datetime.date.today())
time = st.text_input('Choisir une heure :', '19:30')
hr = st.number_input('Entrez la valeur de HR :', value=140)
minutes = st.number_input("Entrez la durée en minutes :", min_value=0, value=75)

if st.button('Afficher GPX'):
    gpx_content = display_gpx(date, time, hr, minutes)
    st.text_area('Contenu GPX :', gpx_content, height=300)
    
    st.download_button(label='Télécharger', data=gpx_content, file_name='five.gpx', mime='text/xml')

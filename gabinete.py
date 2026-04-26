import streamlit as st
import pandas as pd
from datetime import datetime, time
import urllib.parse
import os

st.set_page_config(page_title="Gestión de Turnos - Gabinete", layout="centered")

DB_FILE = "turnos.csv"

def cargar_datos():

    if os.path.exists(DB_FILE):

        df = pd.read_csv(DB_FILE)

        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date

        return df

    return pd.DataFrame(columns=["Cliente", "WhatsApp", "Servicio", "Fecha", "Hora"])


if 'turnos' not in st.session_state:

    st.session_state.turnos = cargar_datos()


st.markdown("""

    <style>

    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #ff4b4b; color: white; }

    .stDownloadButton>button { width: 100%; }

    </style>

    """, unsafe_allow_html=True)



st.title("💆‍♀️ Sistema de Turnos")


with st.expander("📝 Cargar Nuevo Turno", expanded=True):

    with st.form("form_turno", clear_on_submit=True):

        col_a, col_b = st.columns(2)

        with col_a:

            cliente = st.text_input("Nombre de la Clienta")

            servicio = st.selectbox("Servicio", [

                "Depilación laser.soprano ice Platinum", 
                "Ultracavitacion + vacumm", 
                "Limpieza facial profunda",
                "Tratamiento para piernas cansadas",
                "Radiofrecuencia facial",
                "Radiofrecuencia corporal",
                "Masajes descontracturantes",
                "Peeling enzimatico",
                "Dermaplaning",
                "Electroestimulacion",
                "Peeling quimico",
                "Tratamiento  piel acneica",
                "Tratamiento de hidratacion y nutricion facial",
                "Tratamiento de rejuvenicimiento cuello y escotte",            ])

        with col_b:


            tel = st.text_input("WhatsApp (Ej: 5493814445555)")

            fecha = st.date_input("Día del Turno", datetime.today())
        hora = st.time_input("Hora del Turno", value=time(9, 0))

        
        btn_guardar = st.form_submit_button("GUARDAR TURNO")



        if btn_guardar:

            if cliente and tel:

                nuevo_fila = pd.DataFrame([[cliente, tel, servicio, fecha, hora.strftime("%H:%M")]], 

                                         columns=["Cliente", "WhatsApp", "Servicio", "Fecha", "Hora"])

                st.session_state.turnos = pd.concat([st.session_state.turnos, nuevo_fila], ignore_index=True)

                st.session_state.turnos.to_csv(DB_FILE, index=False)

                st.success(f"Turno guardado para {cliente}")

                st.rerun()

            else:

                st.error("Por favor completa nombre y teléfono.")




st.subheader("📅 Turnos Programados")



if not st.session_state.turnos.empty:

    df_sorted = st.session_state.turnos.sort_values(by=["Fecha", "Hora"])

    for i, row in df_sorted.iterrows():
        with st.container():

            c1, c2, c3 = st.columns([2, 2, 1])


            fecha_f = row['Fecha'].strftime("%d/%m")

            

            c1.write(f"**{row['Hora']}** | {fecha_f}")

            c2.write(f"**{row['Cliente']}**\n{row['Servicio']}")

            texto = f"Hola {row['Cliente']}, paso a recordarte tu turno de {row['Servicio']} el día {fecha_f} a las {row['Hora']}. ¡Te espero no te olvides!"

            link = f"https://wa.me/{row['WhatsApp']}?text={urllib.parse.quote(texto)}"

            c3.link_button("📲", link)

            st.divider()
else:

    st.info("Todavía no hay turnos cargados.")


with st.sidebar:

    st.header("⚙️ Configuración")

    if st.button("Eliminar los turnos"):

        if os.path.exists(DB_FILE):

            os.remove(DB_FILE)

            st.session_state.turnos = pd.DataFrame(columns=["Cliente", "WhatsApp", "Servicio", "Fecha", "Hora"])

            st.rerun()

    st.write("---")

    csv = st.session_state.turnos.to_csv(index=False).encode('utf-8')

    st.download_button("Descargar Respaldo (CSV)", csv, "turnos_estetica.csv", "text/csv")

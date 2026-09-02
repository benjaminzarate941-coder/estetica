import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import urllib.parse
import os
import re

# ==================== CONFIGURACIÓN DE PÁGINA Y LOGO ====================

st.set_page_config(
    page_title="Gestión de Turnos - Gabinete", 
    layout="wide",
    page_icon="logo.png"  # <--- Tu logo como ícono de la pestaña
)

# Ocultar menú, footer y header de Streamlit para que se vea 100% tu marca
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

DB_FILE = "turnos.csv"

# ==================== FUNCIONES ====================

def cargar_datos():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            df['Hora'] = pd.to_datetime(df['Hora'], format='%H:%M').dt.time
            return df
        except:
            return pd.DataFrame(columns=["Cliente", "WhatsApp", "Servicio", "Fecha", "Hora"])
    return pd.DataFrame(columns=["Cliente", "WhatsApp", "Servicio", "Fecha", "Hora"])


def guardar_datos(df):
    df.to_csv(DB_FILE, index=False)


def validar_telefono(tel):
    tel_limpio = re.sub(r'\D', '', tel)
    return len(tel_limpio) >= 10, tel_limpio


def verificar_duplicado_cliente(df, cliente, fecha, hora):
    """Verifica si EL MISMO CLIENTE ya tiene turno en esa fecha y hora"""
    if df.empty:
        return False
    
    duplicados = df[
        (df['Cliente'].str.lower().str.strip() == cliente.lower().strip()) & 
        (df['Fecha'] == fecha) & 
        (df['Hora'].astype(str) == hora.strftime("%H:%M"))
    ]
    
    return not duplicados.empty


# ==================== ESTILOS PROFESIONALES ====================

st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        padding: 1rem 0;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 2.5em;
        background-color: #3498db;
        color: white;
        font-weight: 500;
        border: none;
    }
    
    .stButton>button:hover {
        background-color: #2980b9;
    }
    
    .stat-box {
        padding: 1.2rem;
        border-radius: 6px;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        text-align: center;
    }
    
    .stat-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2c3e50;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #7f8c8d;
        margin-top: 0.3rem;
    }
    
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# ==================== INICIALIZACIÓN ====================

if 'turnos' not in st.session_state:
    st.session_state.turnos = cargar_datos()

# ==================== HEADER CON LOGO ====================

# Mostrar el logo centrado en la parte superior
col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
with col_logo2:
    st.image("logo.png", width=180)

st.markdown('<div class="main-header">Sistema de Gestión de Turnos</div>', unsafe_allow_html=True)

# ==================== ESTADÍSTICAS ====================

hoy = datetime.today().date()
turnos_hoy = st.session_state.turnos[st.session_state.turnos['Fecha'] == hoy] if not st.session_state.turnos.empty else pd.DataFrame()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{len(turnos_hoy)}</div>
        <div class="stat-label">Turnos Hoy</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    semana_prox = hoy + timedelta(days=7)
    turnos_semana = st.session_state.turnos[
        (st.session_state.turnos['Fecha'] >= hoy) & 
        (st.session_state.turnos['Fecha'] <= semana_prox)
    ] if not st.session_state.turnos.empty else pd.DataFrame()
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{len(turnos_semana)}</div>
        <div class="stat-label">Próximos 7 Días</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    total = st.session_state.turnos['Cliente'].nunique() if not st.session_state.turnos.empty else 0
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{total}</div>
        <div class="stat-label">Clientes Únicos</div>
    </div>
    """, unsafe_allow_html=True)

# ==================== FORMULARIO ====================

with st.expander("Registrar Nuevo Turno", expanded=True):
    with st.form("form_turno", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        
        with col_a:
            cliente = st.text_input("Nombre del cliente")
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
                "Tratamiento de rejuvenicimiento cuello y escotte",            
            ])
        
        with col_b:
            tel = st.text_input("WhatsApp")
            col_f, col_h = st.columns(2)
            with col_f:
                fecha = st.date_input("Fecha", datetime.today())
            with col_h:
                hora = st.time_input("Hora", value=time(9, 0))
        
        if st.form_submit_button("Guardar Turno"):
            if not cliente or not tel:
                st.error("Complete nombre y WhatsApp")
            else:
                tel_valido, tel_limpio = validar_telefono(tel)
                if not tel_valido:
                    st.error("El número debe tener al menos 10 dígitos")
                elif verificar_duplicado_cliente(st.session_state.turnos, cliente, fecha, hora):
                    st.warning(f"{cliente} ya tiene un turno agendado para el {fecha.strftime('%d/%m')} a las {hora.strftime('%H:%M')}")
                else:
                    nuevo = pd.DataFrame([[cliente.strip(), tel_limpio, servicio, fecha, hora.strftime("%H:%M")]], 
                                        columns=["Cliente", "WhatsApp", "Servicio", "Fecha", "Hora"])
                    st.session_state.turnos = pd.concat([st.session_state.turnos, nuevo], ignore_index=True)
                    st.session_state.turnos = st.session_state.turnos.sort_values(by=["Fecha", "Hora"]).reset_index(drop=True)
                    guardar_datos(st.session_state.turnos)
                    st.success("Turno guardado correctamente")
                    st.rerun()

# ==================== FILTROS ====================

st.markdown("<hr>", unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    busqueda = st.text_input("Buscar cliente", placeholder="Nombre...")

with col_f2:
    servicios = sorted(st.session_state.turnos['Servicio'].unique()) if not st.session_state.turnos.empty else []
    filtro_serv = st.selectbox("Por servicio", ["Todos"] + servicios)

with col_f3:
    filtro_fecha = st.date_input("Por fecha", None)

# Filtrar
df = st.session_state.turnos.copy()

if busqueda:
    df = df[df['Cliente'].str.contains(busqueda, case=False, na=False)]

if filtro_serv != "Todos":
    df = df[df['Servicio'] == filtro_serv]

if filtro_fecha:
    df = df[df['Fecha'] == filtro_fecha]

df = df.sort_values(by=["Fecha", "Hora"]).reset_index(drop=True)

# ==================== LISTA DE TURNOS ====================

if not df.empty:
    fechas = df['Fecha'].unique()
    
    for fecha in sorted(fechas):
        turnos_dia = df[df['Fecha'] == fecha]
        st.markdown(f"**{fecha.strftime('%A %d/%m/%Y').title()}**")
        
        for idx, row in turnos_dia.iterrows():
            cols = st.columns([0.7, 2, 2, 1])
            
            with cols[0]:
                st.write(f"**{row['Hora']}**")
            
            with cols[1]:
                st.write(f"**{row['Cliente']}**")
                st.caption(row['Servicio'])
            
            with cols[2]:
                fecha_f = row['Fecha'].strftime("%d/%m")
                texto = f"Hola {row['Cliente']}, le recordamos su turno de {row['Servicio']} para el {fecha_f} a las {row['Hora']} hs. Saludos."
                link = f"https://wa.me/{row['WhatsApp']}?text={urllib.parse.quote(texto)}"
                st.link_button("Enviar recordatorio", link)
            
            with cols[3]:
                if st.button("Eliminar", key=f"del_{idx}"):
                    st.session_state.turnos = st.session_state.turnos.drop(idx).reset_index(drop=True)
                    guardar_datos(st.session_state.turnos)
                    st.success("Eliminado")
                    st.rerun()
            
            st.markdown("---")
else:
    st.info("No hay turnos registrados")

# ==================== SIDEBAR ====================

with st.sidebar:
    st.header("Opciones")
    
    if st.button("Exportar CSV"):
        if not st.session_state.turnos.empty:
            csv = st.session_state.turnos.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Descargar",
                csv,
                f"turnos_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
    
    st.write("---")
    
    if st.button("Limpiar todo"):
        if st.checkbox("¿Confirmar?"):
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            st.session_state.turnos = pd.DataFrame(columns=["Cliente", "WhatsApp", "Servicio", "Fecha", "Hora"])
            st.success("Datos eliminados")
            st.rerun()
    
    st.write("---")
    st.caption(f"Registros: {len(st.session_state.turnos)}")

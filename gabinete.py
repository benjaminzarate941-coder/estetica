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
    page_icon="logo.png"
)

# Ocultar menú, footer, header y marca de creador de Streamlit
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
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

# ==================== PALETA DE COLORES PROFESIONAL (CLÍNICA / GABINETE) ====================

st.markdown("""
<style>
    /* Fondo general limpio y luminoso */
    .stApp {
        background-color: #f8fafc;
    }

    .main-header {
        font-size: 1.6rem;
        font-weight: 600;
        color: #1e293b;
        padding: 0.5rem 0;
        margin-bottom: 1rem;
        text-align: center;
        letter-spacing: -0.5px;
    }
    
    /* Botones con tono corporativo elegante y suave */
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        height: 2.5em;
        background-color: #0284c7;
        color: white;
        font-weight: 500;
        border: none;
        transition: background-color 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #0369a1;
    }
    
    /* Tarjetas de estadísticas sobrias */
    .stat-box {
        padding: 1.1rem;
        border-radius: 8px;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    
    .stat-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 0.2rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Tipografía general */
    h1, h2, h3, p, label {
        color: #1e293b;
    }
    
    hr {
        margin: 1.2rem 0;
        border: none;
        border-top: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== INICIALIZACIÓN ====================

if 'turnos' not in st.session_state:
    st.session_state.turnos = cargar_datos()

# ==================== HEADER CON LOGO ====================

col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
with col_logo2:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)

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
        <div class="stat-label">Próx. 7 Días</div>
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

st.markdown("<br>", unsafe_allow_html=True)

# ==================== FORMULARIO ====================

with st.expander("📅 Registrar Nuevo Turno", expanded=False):
    with st.form("form_turno", clear_on_submit=True):
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
            "Tratamiento piel acneica",
            "Tratamiento de hidratacion y nutricion facial",
            "Tratamiento de rejuvenicimiento cuello y escotte",            
        ])
        
        tel = st.text_input("WhatsApp (ej: 3815000000)")
        
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
    busqueda = st.text_input("🔍 Buscar cliente", placeholder="Nombre...")

with col_f2:
    servicios = sorted(st.session_state.turnos['Servicio'].unique()) if not st.session_state.turnos.empty else []
    filtro_serv = st.selectbox("📂 Por servicio", ["Todos"] + servicios)

with col_f3:
    filtro_fecha = st.date_input("📆 Por fecha específica", value=None)

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

st.markdown("### Listado de Turnos")

if not df.empty:
    fechas = df['Fecha'].unique()
    
    for fecha in sorted(fechas):
        turnos_dia = df[df['Fecha'] == fecha]
        st.markdown(f"**📌 {fecha.strftime('%A %d/%m/%Y').title()}**")
        
        for idx, row in turnos_dia.iterrows():
            with st.container():
                cols = st.columns([0.8, 2.2, 1.8, 1])
                
                with cols[0]:
                    st.markdown(f"🕒 **{row['Hora']}**")
                
                with cols[1]:
                    st.markdown(f"👤 **{row['Cliente']}**")
                    st.caption(row['Servicio'])
                
                with cols[2]:
                    fecha_f = row['Fecha'].strftime("%d/%m")
                    texto = f"Hola {row['Cliente']}, le recordamos su turno de {row['Servicio']} para el {fecha_f} a las {row['Hora']} hs. Saludos."
                    link = f"https://wa.me/{row['WhatsApp']}?text={urllib.parse.quote(texto)}"
                    st.link_button("💬 Recordatorio", link)
                
                with cols[3]:
                    if st.button("❌ Borrar", key=f"del_{idx}"):
                        st.session_state.turnos = st.session_state.turnos.drop(idx).reset_index(drop=True)
                        guardar_datos(st.session_state.turnos)
                        st.success("Eliminado")
                        st.rerun()
                
            st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)
else:
    st.info("No hay turnos registrados con los filtros actualizados.")

# ==================== SIDEBAR ====================

with st.sidebar:
    st.header("Panel de Control")
    
    if st.button("📥 Exportar Base CSV"):
        if not st.session_state.turnos.empty:
            csv = st.session_state.turnos.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Descargar Archivo",
                csv,
                f"turnos_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
        else:
            st.warning("No hay datos para exportar")
    
    st.write("---")
    
    if st.button("🗑️ Limpiar Base de Datos"):
        if st.checkbox("Confirmar eliminación total"):
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            st.session_state.turnos = pd.DataFrame(columns=["Cliente", "WhatsApp", "Servicio", "Fecha", "Hora"])
            st.success("Base de datos reseteada")
            st.rerun()
    
    st.write("---")
    st.caption(f"Total registros: {len(st.session_state.turnos)}")

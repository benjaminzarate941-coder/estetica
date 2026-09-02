import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import urllib.parse
import os
import re

st.set_page_config(
    page_title="Gestión de Turnos - Gabinete", 
    layout="wide",
    page_icon="💆‍♀️"
)

DB_FILE = "turnos.csv"

# ==================== FUNCIONES AUXILIARES ====================

def cargar_datos():
    """Carga los turnos desde CSV o crea DataFrame vacío"""
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            df['Hora'] = pd.to_datetime(df['Hora'], format='%H:%M').dt.time
            return df
        except Exception as e:
            st.error(f"Error al cargar datos: {e}")
            return pd.DataFrame(columns=["Cliente", "WhatsApp", "Servicio", "Fecha", "Hora"])
    return pd.DataFrame(columns=["Cliente", "WhatsApp", "Servicio", "Fecha", "Hora"])


def guardar_datos(df):
    """Guarda el DataFrame en CSV"""
    df.to_csv(DB_FILE, index=False)


def validar_telefono(tel):
    """Valida formato de teléfono para WhatsApp"""
    tel_limpio = re.sub(r'\D', '', tel)
    if len(tel_limpio) < 10:
        return False, tel_limpio
    return True, tel_limpio


def verificar_duplicado(df, cliente, fecha, hora):
    """Verifica si ya existe un turno para esa persona en ese horario"""
    if df.empty:
        return False
    
    duplicados = df[
        (df['Cliente'].str.lower() == cliente.lower()) & 
        (df['Fecha'] == fecha) & 
        (df['Hora'] == hora.strftime("%H:%M"))
    ]
    return not duplicados.empty


def generar_link_whatsapp(cliente, servicio, fecha, hora, whatsapp):
    """Genera link de WhatsApp con mensaje personalizado"""
    fecha_f = fecha.strftime("%d/%m")
    texto = f"Hola {cliente}, paso a recordarte tu turno de {servicio} el día {fecha_f} a las {hora}. ¡Te espero, no te olvides! 💆‍♀️"
    link = f"https://wa.me/{whatsapp}?text={urllib.parse.quote(texto)}"
    return link


# ==================== INICIALIZACIÓN ====================

if 'turnos' not in st.session_state:
    st.session_state.turnos = cargar_datos()

# ==================== ESTILOS CSS ====================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ff4b4b;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #ff3333;
    }
    .turno-card {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 0.5rem;
        border-left: 4px solid #ff4b4b;
    }
    .stats-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #e8f4f8;
        margin-bottom: 1rem;
    }
    div[data-testid="stExpander"] {
        border: 2px solid #ff4b4b;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================

st.markdown('<div class="main-header">💆‍♀️ Sistema de Gestión de Turnos</div>', unsafe_allow_html=True)

# ==================== ESTADÍSTICAS RÁPIDAS ====================

col_stats1, col_stats2, col_stats3 = st.columns(3)

hoy = datetime.today().date()
turnos_hoy = st.session_state.turnos[st.session_state.turnos['Fecha'] == hoy] if not st.session_state.turnos.empty else pd.DataFrame()

with col_stats1:
    st.metric("📅 Turnos Hoy", len(turnos_hoy))

with col_stats2:
    semana_prox = hoy + timedelta(days=7)
    turnos_semana = st.session_state.turnos[
        (st.session_state.turnos['Fecha'] >= hoy) & 
        (st.session_state.turnos['Fecha'] <= semana_prox)
    ] if not st.session_state.turnos.empty else pd.DataFrame()
    st.metric("📊 Próximos 7 días", len(turnos_semana))

with col_stats3:
    st.metric("👥 Total Clientes", st.session_state.turnos['Cliente'].nunique() if not st.session_state.turnos.empty else 0)

# ==================== FORMULARIO NUEVO TURNO ====================

with st.expander("➕ Cargar Nuevo Turno", expanded=True):
    with st.form("form_turno", clear_on_submit=True):
        st.subheader("📝 Datos del Turno")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            cliente = st.text_input("Nombre de la Clienta *", placeholder="Ej: María González")
            servicio = st.selectbox("Servicio *", [
                "Depilación laser soprano ice Platinum", 
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
                "Tratamiento de rejuvenecimiento cuello y escote",
            ])
        
        with col_b:
            tel = st.text_input("WhatsApp *", placeholder="Ej: 5493814445555")
            col_fecha, col_hora = st.columns(2)
            with col_fecha:
                fecha = st.date_input("Día del Turno *", datetime.today())
            with col_hora:
                hora = st.time_input("Hora del Turno *", value=time(9, 0))
        
        btn_guardar = st.form_submit_button("💾 GUARDAR TURNO")
        
        if btn_guardar:
            # Validaciones
            errores = []
            
            if not cliente.strip():
                errores.append("El nombre es obligatorio")
            
            if not tel.strip():
                errores.append("El WhatsApp es obligatorio")
            else:
                tel_valido, tel_limpio = validar_telefono(tel)
                if not tel_valido:
                    errores.append("El número de WhatsApp debe tener al menos 10 dígitos")
            
            if errores:
                for error in errores:
                    st.error(f"❌ {error}")
            else:
                # Verificar duplicados
                if verificar_duplicado(st.session_state.turnos, cliente, fecha, hora):
                    st.warning(f"⚠️ Ya existe un turno para {cliente} el {fecha.strftime('%d/%m')} a las {hora.strftime('%H:%M')}")
                else:
                    # Guardar turno
                    nuevo_fila = pd.DataFrame([[
                        cliente.strip(), 
                        tel_limpio, 
                        servicio, 
                        fecha, 
                        hora.strftime("%H:%M")
                    ]], columns=["Cliente", "WhatsApp", "Servicio", "Fecha", "Hora"])
                    
                    st.session_state.turnos = pd.concat([st.session_state.turnos, nuevo_fila], ignore_index=True)
                    st.session_state.turnos = st.session_state.turnos.sort_values(by=["Fecha", "Hora"]).reset_index(drop=True)
                    guardar_datos(st.session_state.turnos)
                    
                    st.success(f"✅ Turno guardado exitosamente para {cliente}")
                    st.balloons()
                    st.rerun()

# ==================== FILTROS Y BÚSQUEDA ====================

st.markdown("---")
st.subheader("🔍 Buscar Turnos")

col_filtros1, col_filtros2, col_filtros3 = st.columns(3)

with col_filtros1:
    busqueda = st.text_input("Buscar por nombre", placeholder="Escribe el nombre...")

with col_filtros2:
    filtro_servicio = st.selectbox("Filtrar por servicio", ["Todos"] + list(set(st.session_state.turnos['Servicio'].unique()) if not st.session_state.turnos.empty else []))

with col_filtros3:
    filtro_fecha = st.date_input("Filtrar por fecha", None)

# Aplicar filtros
df_filtrado = st.session_state.turnos.copy()

if busqueda:
    df_filtrado = df_filtrado[df_filtrado['Cliente'].str.contains(busqueda, case=False, na=False)]

if filtro_servicio != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Servicio'] == filtro_servicio]

if filtro_fecha:
    df_filtrado = df_filtrado[df_filtrado['Fecha'] == filtro_fecha]

df_filtrado = df_filtrado.sort_values(by=["Fecha", "Hora"]).reset_index(drop=True)

# ==================== LISTA DE TURNOS ====================

st.markdown("---")
st.subheader(f"📅 Turnos Programados ({len(df_filtrado)})")

if not df_filtrado.empty:
    # Agrupar por fecha
    fechas_unicas = df_filtrado['Fecha'].unique()
    
    for fecha_grupo in sorted(fechas_unicas):
        turnos_fecha = df_filtrado[df_filtrado['Fecha'] == fecha_grupo]
        
        st.markdown(f"### 📆 {fecha_grupo.strftime('%A %d de %B de %Y').title()}")
        
        for idx, row in turnos_fecha.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
                
                with col1:
                    st.markdown(f"**{row['Hora']}**")
                
                with col2:
                    st.markdown(f"**{row['Cliente']}**")
                    st.caption(row['Servicio'])
                
                with col3:
                    link = generar_link_whatsapp(
                        row['Cliente'], 
                        row['Servicio'], 
                        row['Fecha'], 
                        row['Hora'], 
                        row['WhatsApp']
                    )
                    st.link_button("📲 Recordar", link)
                
                with col4:
                    if st.button("🗑️", key=f"del_{idx}", help="Eliminar turno"):
                        st.session_state.turnos = st.session_state.turnos.drop(idx)
                        st.session_state.turnos = st.session_state.turnos.reset_index(drop=True)
                        guardar_datos(st.session_state.turnos)
                        st.success("Turno eliminado")
                        st.rerun()
                
                st.divider()
else:
    st.info("ℹ️ No hay turnos que coincidan con los filtros aplicados.")

# ==================== SIDEBAR ====================

with st.sidebar:
    st.header("⚙️ Configuración")
    
    st.markdown("### 📊 Acciones")
    
    if st.button("🗑️ Eliminar TODOS los turnos", type="secondary"):
        if st.session_state.turnos.empty:
            st.warning("No hay turnos para eliminar")
        else:
            if st.checkbox("Confirmar eliminación total"):
                if os.path.exists(DB_FILE):
                    os.remove(DB_FILE)
                st.session_state.turnos = pd.DataFrame(columns=["Cliente", "WhatsApp", "Servicio", "Fecha", "Hora"])
                st.success("✅ Todos los turnos han sido eliminados")
                st.rerun()
    
    st.write("---")
    
    st.markdown("### 💾 Respaldo")
    
    if not st.session_state.turnos.empty:
        csv = st.session_state.turnos.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"turnos_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    st.write("---")
    
    st.markdown("### ℹ️ Información")
    st.caption(f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    st.caption(f"Total de turnos: {len(st.session_state.turnos)}")

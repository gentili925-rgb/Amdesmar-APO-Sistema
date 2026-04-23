import streamlit as st
import datetime
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Andesmar Pro - Sistema A.P.O.", layout="wide")

# --- FUNCIONES DE LÓGICA DE TRAMOS ---
def obtener_info_ruta_nac(p):
    etapas = {
        1: "Mendoza -> Jujuy", 2: "Jujuy -> Córdoba", 3: "Posta Córdoba (Espera)",
        4: "Córdoba -> Trelew", 5: "Posta Trelew (Espera)", 6: "Trelew -> Gallegos",
        7: "Rulo Gallegos (Descanso)", 8: "Gallegos -> Trelew", 9: "Posta Trelew (Espera)",
        10: "Trelew -> Córdoba", 11: "Posta Córdoba (Espera)", 12: "Córdoba -> Mendoza",
        13: "Llegando a Base"
    }
    tramo = etapas.get(p["dia_del_ciclo"], "En ruta")
    progreso = p["dia_del_ciclo"] / 13
    return tramo, progreso

def obtener_detalle_franco_nac(p):
    hoy = datetime.datetime.now()
    dias_pasados = (hoy - p["ultimo_arribo"]).days
    dias_restantes = 6 - dias_pasados
    return f"Faltan {max(0, dias_restantes)} días", max(0, dias_restantes)

# --- INICIALIZACIÓN DE DATOS PERSISTENTES ---
if 'db_parejas_nac' not in st.session_state:
    apellidos_nac = ["GARCIA-LOPEZ", "MARTINEZ-RUIZ", "RODRIGUEZ-SOSA", "GONZALEZ-DIAZ", "PEREZ-SANTOS", "SANCHEZ-ORTEGA", "ROMERO-CASTRO", "FERNANDEZ-GIL", "ALVAREZ-MOYA", "GOMEZ-VALDEZ", "RAMIREZ-CANO", "MORALES-NIETO", "FLORES-RIVAS", "BENITEZ-AGUADO", "VARGAS-CALVO", "CASTILLO-LOZA", "MENDEZ-PUERTA", "GUZMAN-VACA", "PACHECO-PEÑA", "VILLALBA-LUZ"]
    db_nac = []
    hoy = datetime.datetime.now()
    for i, ape in enumerate(apellidos_nac):
        dia = (i % 19) + 1
        db_nac.append({
            "pareja": ape, "estado": "EN RUTA" if dia <= 13 else "FRANCO", 
            "dia_del_ciclo": dia, "ultimo_arribo": hoy - datetime.timedelta(days=(dia-13) if dia > 13 else 0),
            "obs": ""
        })
    st.session_state.db_parejas_nac = db_nac
    st.session_state.int_nac = ["5394", "5395", "5396", "5397", "5398", "5399", "5501", "5502", "5503", "5504"]

if 'db_chile' not in st.session_state:
    st.session_state.db_chile = [
        {"interno": "1023", "pareja": "MORALES - RODRIGUEZ", "tramo": "Mendoza - Santiago", "hora": "07:00", "estado": "EN RUTA", "ubicacion": "Ruta 7", "obs": ""},
        {"interno": "2002", "pareja": "ALIS - BORIS", "tramo": "Mendoza - Santiago", "hora": "09:00", "estado": "EN RUTA", "ubicacion": "Salida Mza", "obs": ""},
        {"interno": "1018", "pareja": "ROJAS, L. - VALDEZ", "tramo": "Mendoza - Santiago", "hora": "12:30", "estado": "EN RUTA", "ubicacion": "Aduana", "obs": ""},
        {"interno": "1022", "pareja": "GOMEZ - SALINAS", "tramo": "Mendoza - Santiago", "hora": "22:00", "estado": "LISTO", "ubicacion": "Mendoza", "obs": ""},
        {"interno": "1024", "pareja": "BURGOA - MONTIEL", "tramo": "Santiago - Mendoza", "hora": "08:30", "estado": "EN RUTA", "ubicacion": "Caracoles", "obs": ""},
        {"interno": "5334", "pareja": "NAVARRO - GELVES", "tramo": "Viña - Mendoza", "hora": "07:30", "estado": "EN RUTA", "ubicacion": "Chile", "obs": ""}
    ]

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("Andesmar Pro")
    st.divider()
    modo = st.radio("Menú Principal:", ["📊 Panel General", "🇨🇱 Línea CHILE", "🇦🇷 Línea NACIONAL", "👥 DIAGRAMACIÓN"])

# --- VISTAS ---

if modo == "📊 Panel General":
    st.title("Operaciones Globales")
    c1, c2, c3 = st.columns(3)
    c1.metric("Unidades Nac. en Ruta", len([p for p in st.session_state.db_parejas_nac if p['estado']=="EN RUTA"]))
    c2.metric("Servicios Chile Hoy", len(st.session_state.db_chile))
    c3.metric("Paso Internacional", "ABIERTO")

elif modo == "🇨🇱 Línea CHILE":
    st.title("Fichas de Servicio: Chile")
    for serv in st.session_state.db_chile:
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 2, 2])
            with col1: st.markdown(f"## 🚍 {serv['interno']}")
            with col2:
                st.write(f"**Pareja:** {serv['pareja']}")
                st.write(f"**Tramo:** {serv['tramo']}")
                if serv['obs']: st.warning(f"Nota: {serv['obs']}")
            with col3:
                st.write(f"**Estado:** {serv['estado']}")
                st.write(f"**Ubicación:** {serv['ubicacion']}")
                st.progress(0.5, text=f"Hora: {serv['hora']}")

elif modo == "🇦🇷 Línea NACIONAL":
    st.title("Fichas de Ruta: Nacional (Tramos Detallados)")
    for i, interno in enumerate(st.session_state.int_nac):
        p = st.session_state.db_parejas_nac[i]
        if p["estado"] == "EN RUTA":
            tramo_actual, porcentaje = obtener_info_ruta_nac(p)
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 2, 2])
                with col1: st.markdown(f"## 🚍 {interno}")
                with col2:
                    st.write(f"**Pareja:** {p['pareja']}")
                    st.write(f"**Tramo Actual:** {tramo_actual}")
                    if p['obs']: st.warning(f"Nota: {p['obs']}")
                with col3:
                    st.write(f"**Estado:** EN RUTA")
                    st.progress(porcentaje, text=f"Día {p['dia_del_ciclo']} de la vuelta")

elif modo == "👥 DIAGRAMACIÓN":
    st.title("Módulo de Diagramación Integral (Manual)")
    tab1, tab2 = st.tabs(["🇦🇷 Ajustes Nacional", "🇨🇱 Ajustes Chile"])
    
    with tab1:
        st.subheader("Gestión de Parejas Nacionales")
        for idx, p in enumerate(st.session_state.db_parejas_nac):
            det, dias = obtener_detalle_franco_nac(p) if p['estado'] == "FRANCO" else (f"Día {p['dia_del_ciclo']}/13", 0)
            with st.expander(f"👤 {p['pareja']} - {p['estado']} ({det})"):
                col1, col2 = st.columns(2)
                with col1:
                    nuevo_est = st.selectbox("Estado:", ["FRANCO", "EN RUTA"], index=0 if p['estado']=="FRANCO" else 1, key=f"est_n_{idx}")
                    if nuevo_est != p['estado']:
                        st.session_state.db_parejas_nac[idx]['estado'] = nuevo_est
                        st.rerun()
                    if p['estado'] == "FRANCO":
                        ajuste = st.number_input("Días de franco restantes:", value=dias, key=f"d_n_{idx}")
                        if ajuste != dias:
                            st.session_state.db_parejas_nac[idx]['ultimo_arribo'] = datetime.datetime.now() - datetime.timedelta(days=6-ajuste)
                            st.rerun()
                with col2:
                    st.session_state.db_parejas_nac[idx]['obs'] = st.text_input("Observación:", value=p['obs'], key=f"obs_n_{idx}")

    with tab2:
        st.subheader("Gestión de Servicios Chile")
        for idx, c in enumerate(st.session_state.db_chile):
            with st.expander(f"🚍 {c['interno']} - {c['pareja']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state.db_chile[idx]['estado'] = st.selectbox("Estado:", ["LISTO", "EN RUTA", "DESCANSO"], index=1 if c['estado']=="EN RUTA" else 0, key=f"est_c_{idx}")
                    st.session_state.db_chile[idx]['ubicacion'] = st.text_input("Ubicación:", value=c['ubicacion'], key=f"ub_c_{idx}")
                with col2:
                    st.session_state.db_chile[idx]['obs'] = st.text_input("Nota:", value=c['obs'], key=f"obs_c_{idx}")

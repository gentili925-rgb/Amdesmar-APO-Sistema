import streamlit as st
import datetime
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Andesmar Pro - Sistema A.P.O.", layout="wide")

# --- ESTADOS GLOBALES (PERSISTENCIA) ---
if 'estado_paso' not in st.session_state:
    st.session_state.estado_paso = "ABIERTO"

# --- PARÁMETROS ---
DIAS_MICRO_RETORNO = 10
DIAS_PAREJA_RETORNO = 13
DIAS_TOTAL_FRANCO = 6

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
    progreso = min(p["dia_del_ciclo"] / 13, 1.0)
    return tramo, progreso

def obtener_detalle_franco_nac(p):
    hoy = datetime.datetime.now()
    dias_pasados = (hoy - p["ultimo_arribo"]).days
    dias_restantes = DIAS_TOTAL_FRANCO - dias_pasados
    return f"Faltan {max(0, dias_restantes)} días", max(0, dias_restantes)

# --- INICIALIZACIÓN DE DATOS ---
if 'db_parejas_nac' not in st.session_state:
    apellidos_nac = [
        "GARCIA-LOPEZ", "MARTINEZ-RUIZ", "RODRIGUEZ-SOSA", "GONZALEZ-DIAZ", 
        "PEREZ-SANTOS", "SANCHEZ-ORTEGA", "ROMERO-CASTRO", "FERNANDEZ-GIL", 
        "ALVAREZ-MOYA", "GOMEZ-VALDEZ", "RAMIREZ-CANO", "MORALES-NIETO", 
        "FLORES-RIVAS", "BENITEZ-AGUADO", "VARGAS-CALVO", "CASTILLO-LOZA", 
        "MENDEZ-PUERTA", "GUZMAN-VACA", "PACHECO-PEÑA", "VILLALBA-LUZ", 
        "PAREJA 115", "PAREJA 116"
    ]
    db_nac = []
    hoy = datetime.datetime.now()
    st.session_state.int_nac = ["5394", "5395", "5396", "5397", "5398", "5399", "5501", "5502", "5503", "5504", "115", "116"]
    for i, ape in enumerate(apellidos_nac):
        if i <= 12:
            dia = i + 1
            estado = "EN RUTA"
            f_arribo = hoy - datetime.timedelta(days=1)
        elif i <= 18:
            dia = 14
            estado = "FRANCO"
            dias_ya_descansados = i - 13 
            f_arribo = hoy - datetime.timedelta(days=dias_ya_descansados)
        else:
            dia = 14
            estado = "LISTO (RESERVA)"
            f_arribo = hoy - datetime.timedelta(days=DIAS_TOTAL_FRANCO)
        db_nac.append({"pareja": ape, "estado": estado, "dia_del_ciclo": dia, "ultimo_arribo": f_arribo, "obs": "Refuerzo" if i >= 19 else ""})
    st.session_state.db_parejas_nac = db_nac

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
    modo = st.radio("Menú Principal:", ["📊 Panel General", "🇨🇱 Línea CHILE", "🇦🇷 Mendoza, Jujuy y Gallegos", "👥 DIAGRAMACIÓN"])

# --- VISTAS ---

if modo == "📊 Panel General":
    st.title("Operaciones Globales")
    c1, c2, c3 = st.columns(3)
    c1.metric("En Ruta (Nac.)", len([p for p in st.session_state.db_parejas_nac if p['estado']=="EN RUTA"]))
    c2.metric("Disponibles (Base)", len([p for p in st.session_state.db_parejas_nac if p['estado']!="EN RUTA"]))
    with c3:
        st.markdown(f"**Paso Internacional:** {st.session_state.estado_paso}")
        nuevo_estado = st.selectbox("Cambiar estado:", ["ABIERTO", "CERRADO", "PREVENTIVO"], index=["ABIERTO", "CERRADO", "PREVENTIVO"].index(st.session_state.estado_paso))
        if nuevo_estado != st.session_state.estado_paso:
            st.session_state.estado_paso = nuevo_estado
            st.rerun()
    if st.session_state.estado_paso == "CERRADO":
        st.error("⚠️ ALERTA: PASO CERRADO. Salidas a Chile suspendidas.")
    elif st.session_state.estado_paso == "PREVENTIVO":
        st.warning("⚠️ AVISO: Posible cierre de paso por condiciones climáticas.")

elif modo == "🇨🇱 Línea CHILE":
    st.title("Fichas de Servicio: Chile")
    for idx, serv in enumerate(st.session_state.db_chile):
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 2, 2])
            with col1: st.markdown(f"## 🚍 {serv['interno']}")
            with col2:
                st.write(f"**Pareja:** {serv['pareja']}")
                st.write(f"**Tramo:** {serv['tramo']}")
            with col3:
                es_mza = serv['ubicacion'] == "Mendoza"
                esta_cerrado = st.session_state.estado_paso == "CERRADO"
                if esta_cerrado and es_mza:
                    st.error("🚫 SALIDA BLOQUEADA (Paso Cerrado)")
                lista_ub = ["Mendoza", "Salida Mza", "Uspallata", "Aduana", "Chile", "Santiago", "Ruta 7", "Caracoles"]
                idx_ub = lista_ub.index(serv['ubicacion']) if serv['ubicacion'] in lista_ub else 0
                nueva_ub = st.selectbox(f"Ubicación ({serv['interno']}):", lista_ub, index=idx_ub, key=f"ub_ch_{idx}", disabled=(esta_cerrado and es_mza))
                if nueva_ub != serv['ubicacion']:
                    st.session_state.db_chile[idx]['ubicacion'] = nueva_ub
                    st.session_state.db_chile[idx]['estado'] = "LISTO" if nueva_ub == "Mendoza" else "EN RUTA"
                    st.rerun()

elif modo == "🇦🇷 Mendoza, Jujuy y Gallegos":
    st.title("Fichas de Ruta: Mendoza, Jujuy y Gallegos")
    for i, interno in enumerate(st.session_state.int_nac):
        p = st.session_state.db_parejas_nac[i]
        llave_aux = f"aux_st_{interno}"
        if interno in ["115", "116"] and llave_aux not in st.session_state:
            st.session_state[llave_aux] = "DISPONIBLE"
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 2, 2])
            with col1: st.markdown(f"## 🚍 {interno}")
            with col2:
                if interno in ["115", "116"]:
                    if st.session_state[llave_aux] == "DISPONIBLE":
                        st.write("**Unidad en Base:** Mendoza")
                        st.write("*(Reserva Técnica / Sin pareja)*")
                    else:
                        st.write(f"**Pareja en Servicio:** {st.session_state.get(f'ref_p_{interno}', 'En curso')}")
                else:
                    if p["estado"] == "EN RUTA":
                        st.write(f"**Pareja:** {p['pareja']}")
                        tramo_actual, _ = obtener_info_ruta_nac(p)
                        st.write(f"**Tramo Actual:** {tramo_actual}")
                    else:
                        det_franco, _ = obtener_detalle_franco_nac(p)
                        st.write(f"**Estado Base:** {p['estado']}")
                        st.write(f"**Cronograma:** {det_franco}")
            with col3:
                if interno in ["115", "116"]:
                    if st.session_state[llave_aux] == "DISPONIBLE":
                        st.success("UNIDAD DISPONIBLE")
                        listos = [pa['pareja'] for pa in st.session_state.db_parejas_nac if pa['estado'] == "LISTO (RESERVA)"]
                        p_sel = st.selectbox("Asignar Pareja:", listos if listos else ["Sin Personal"], key=f"sel_aux_{interno}")
                        if st.button(f"DESPACHAR {interno}", key=f"btn_d_{interno}") and p_sel != "Sin Personal":
                            st.session_state[llave_aux] = f"EN SERVICIO"
                            st.session_state[f"ref_p_{interno}"] = p_sel
                            for idx_p, busq in enumerate(st.session_state.db_parejas_nac):
                                if busq['pareja'] == p_sel:
                                    st.session_state.db_parejas_nac[idx_p]['estado'] = "EN RUTA"
                            st.rerun()
                    else:
                        st.warning(f"UNIDAD EN SERVICIO")
                        if st.button(f"FINALIZAR AUXILIO {interno}", key=f"btn_f_{interno}"):
                            p_vuelve = st.session_state.get(f"ref_p_{interno}", "")
                            for idx_p, busq in enumerate(st.session_state.db_parejas_nac):
                                if busq['pareja'] == p_vuelve:
                                    st.session_state.db_parejas_nac[idx_p]['estado'] = "LISTO (RESERVA)"
                            st.session_state[llave_aux] = "DISPONIBLE"
                            st.rerun()
                elif p["estado"] == "EN RUTA":
                    _, porcentaje = obtener_info_ruta_nac(p)
                    st.progress(porcentaje, text=f"Día {p['dia_del_ciclo']} de 13")
                else:
                    st.info("Unidad en Mantenimiento/Base")

elif modo == "👥 DIAGRAMACIÓN":
    st.title("Módulo de Diagramación Integral")
    tab1, tab2 = st.tabs(["🇦🇷 Ajustes Mendoza/Jujuy/Gallegos", "🇨🇱 Ajustes Chile"])
    with tab1:
        for idx, p in enumerate(st.session_state.db_parejas_nac):
            if p['estado'] == "EN RUTA":
                det = f"Día {p['dia_del_ciclo']}/13"
            else:
                det, _ = obtener_detalle_franco_nac(p)
            with st.expander(f"👤 {p['pareja']} - {p['estado']} ({det})"):
                col1, col2 = st.columns(2)
                with col1:
                    nuevo_est = st.selectbox("Cambiar Estado:", ["EN RUTA", "FRANCO", "LISTO (RESERVA)"], index=0 if p['estado']=="EN RUTA" else (1 if p['estado']=="FRANCO" else 2), key=f"est_n_{idx}")
                    if nuevo_est != p['estado']:
                        st.session_state.db_parejas_nac[idx]['estado'] = nuevo_est
                        st.rerun()
                with col2:
                    if p['estado'] != "EN RUTA":
                        _, dias_actuales = obtener_detalle_franco_nac(p)
                        ajuste = st.number_input("Días restantes de franco:", value=int(dias_actuales), key=f"d_n_{idx}")
                        if ajuste != dias_actuales:
                            st.session_state.db_parejas_nac[idx]['ultimo_arribo'] = datetime.datetime.now() - datetime.timedelta(days=DIAS_TOTAL_FRANCO - ajuste)
                            st.rerun()
                    st.session_state.db_parejas_nac[idx]['obs'] = st.text_input("Observación:", value=p['obs'], key=f"obs_n_{idx}")

    with tab2:
        for idx, c in enumerate(st.session_state.db_chile):
            # Lógica de sincronización visual para Chile
            estado_visual = c['estado']
            with st.expander(f"🚍 {c['interno']} - {c['pareja']} (Estado: {estado_visual})"):
                nuevo_est_ch = st.selectbox("Cambiar Estado Interno:", ["LISTO", "EN RUTA", "DESCANSO"], index=["LISTO", "EN RUTA", "DESCANSO"].index(c['estado']), key=f"est_c_{idx}")
                if nuevo_est_ch != c['estado']:
                    st.session_state.db_chile[idx]['estado'] = nuevo_est_ch
                    st.rerun()

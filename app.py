import streamlit as st
import webbrowser
import urllib.parse

st.set_page_config(page_title="Venta de Números", layout="wide")

# Inicializar estado si no existe
if 'registros' not in st.session_state:
    st.session_state.registros = {}
if 'vendidos' not in st.session_state:
    st.session_state.vendidos = set()

st.title("🔢 Selector de Números 00-99")

# Cuadrícula de números
cols = st.columns(10)
seleccionados = []

for i in range(100):
    num = f"{i:02d}"
    with cols[i % 10]:
        # Si ya está vendido, deshabilitar
        if num in st.session_state.vendidos:
            st.button(num, key=num, disabled=True, type="secondary")
        else:
            if st.checkbox(num, key=f"chk_{num}"):
                seleccionados.append(num)

# Lateral para valores y reporte
with st.sidebar:
    valor = st.text_input("Valor en Colones", placeholder="500")
    if st.button("Registrar"):
        if seleccionados and valor:
            st.session_state.registros[valor] = st.session_state.registros.get(valor, []) + seleccionados
            for n in seleccionados: st.session_state.vendidos.add(n)
            st.success("¡Registrado!")
            st.rerun()

    st.write("### Reporte Actual")
    reporte_texto = ""
    for v, nums in st.session_state.registros.items():
        linea = f"{', '.join(nums)} = {v} colones"
        st.text(linea)
        reporte_texto += linea + "\n"

    if reporte_texto:
        # Botón de WhatsApp (Link directo)
        url_wa = f"https://wa.me/?text={urllib.parse.quote(reporte_texto)}"
        st.link_button("📲 Enviar a WhatsApp", url_wa)
import streamlit as st
import urllib.parse

st.set_page_config(page_title="Venta de Números CR", layout="wide")

if 'registros' not in st.session_state:
    st.session_state.registros = []
if 'vendidos' not in st.session_state:
    st.session_state.vendidos = set()

st.title("🔢 Selector de Números 00-99")

# Cuadrícula
cols = st.columns(10)
seleccionados = []

for i in range(100):
    num = f"{i:02d}"
    with cols[i % 10]:
        if num in st.session_state.vendidos:
            st.button(num, key=f"btn_{num}", disabled=True)
        else:
            if st.checkbox(num, key=f"chk_{num}"):
                seleccionados.append(num)

with st.sidebar:
    st.header("🛒 Registrar Venta")
    valor_input = st.text_input("Precio por número (₡)", placeholder="Ej: 200")

    if st.button("Agregar a la lista"):
        if seleccionados and valor_input.isdigit():
            precio_unitario = int(valor_input)
            nums_ordenados = sorted(seleccionados)
            cantidad = len(nums_ordenados)
            subtotal = cantidad * precio_unitario

            nueva_linea = {
                "numeros": nums_ordenados,
                "cantidad": cantidad,
                "precio": precio_unitario,
                "subtotal": subtotal
            }

            st.session_state.registros.append(nueva_linea)
            for n in seleccionados:
                st.session_state.vendidos.add(n)

            st.success(f"Agregado: ₡{subtotal}")
            st.rerun()
        else:
            st.error("Revisa selección y precio.")

    st.divider()
    st.write("### 📝 Resumen del Reporte")

    cuerpo_reporte = ""
    suma_total_final = 0

    for reg in st.session_state.registros:
        lista_nums = ", ".join(reg["numeros"])
        linea = f"{lista_nums} = ₡{reg['subtotal']} ({reg['cantidad']} x ₡{reg['precio']})"
        st.text(linea)
        cuerpo_reporte += linea + "\n"
        suma_total_final += reg["subtotal"]

    if suma_total_final > 0:
        st.divider()
        texto_total = f"💰 TOTAL A PAGAR: ₡{suma_total_final}"
        st.subheader(texto_total)

        mensaje_completo = f"Resumen de Venta:\n{cuerpo_reporte}\n{texto_total}"
        url_wa = f"https://wa.me/?text={urllib.parse.quote(mensaje_completo)}"
        st.link_button("📲 Enviar por WhatsApp", url_wa, type="primary", use_container_width=True)

        if st.button("Limpiar Todo"):
            st.session_state.registros = []
            st.session_state.vendidos = set()
            st.rerun()

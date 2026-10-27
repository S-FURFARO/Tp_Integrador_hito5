import streamlit as st
import pymysql

# Configuración de página
st.set_page_config(page_title="Adelanto TP", layout="wide")

# Función para obtener la conexión a la base de datos remota
def get_connection():
    return pymysql.connect(
        host="sql201.infinityfree.com",
        user="if0_43285229",
        password="1YZWW74oZ2l4cIR",
        database="if0_43285229_Tp_Integrador_hito5",
        cursorclass=pymysql.cursors.DictCursor
    )

st.title("🏗️ Adelanto TP")
st.caption("Vista general de obras, registro de avances mediante procedimiento almacenado y stock de materiales.")

# Verificación de conexión y navegación
try:
    conn = get_connection()
    st.sidebar.success("Conectado a InfinityFree (BD Remota)")
    conn.close()
except Exception as e:
    st.sidebar.error(f"Error de conexión: {e}")

# Pestañas principales
tab1, tab2, tab3 = st.tabs(["Vista General de Obras", "Registrar Avance", "Materiales"])

with tab1:
    st.header("Vista general de obras")
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            query = """
            SELECT O.N_expediente, O.Ubicación, O.Estado, O.Percent_total_ejec, 
                CONCAT(I.Nombre, ' ', I.Apellido) AS Inspector
            FROM OBRA O
            INNER JOIN INSPECTOR I ON O.ID_Inspector = I.ID_Inspector;
            """
            cursor.execute(query)
            obras = cursor.fetchall()
            
            st.metric(label="Obras con inspector asignado", value=len(obras))
            st.dataframe(obras, use_container_width=True)
            st.caption("INNER JOIN OBRA y INSPECTOR por ID: solo se listan las obras que tienen un inspector asignado.")
        conn.close()
    except Exception as e:
        st.error(f"Error al cargar las obras: {e}")

with tab2:
    st.header("Registrar avance de obra")
    with st.form("form_avance"):
        expediente = st.number_input("Número de Expediente", step=1, min_value=1)
        porcentaje = st.number_input("Porcentaje de Avance (%)", min_value=0.0, max_value=100.0, step=0.1)
        submitted = st.form_submit_button("Actualizar Avance")
        
        if submitted:
            try:
                conn = get_connection()
                with conn.cursor() as cursor:
                    # Llamada al procedimiento almacenado
                    cursor.callproc("RegistrarAvanceObra", (expediente, porcentaje))
                conn.commit()
                st.success("¡Avance registrado exitosamente mediante procedimiento almacenado!")
                conn.close()
            except Exception as e:
                st.error(f"Error al registrar el avance: {e}")

with tab3:
    st.header("Stock de Materiales")
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM MATERIAL;")
            materiales = cursor.fetchall()
            st.dataframe(materiales, use_container_width=True)
        conn.close()
    except Exception as e:
        st.error(f"Error al cargar materiales: {e}")

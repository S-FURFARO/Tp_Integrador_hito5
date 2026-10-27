import streamlit as st
import sqlite3
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Adelanto TP", layout="wide")

# Conexión a base de datos SQLite local (funciona perfecto en Streamlit Cloud)
def get_connection():
    conn = sqlite3.connect("tp_integrador.db")
    return conn

# Inicializar datos de prueba si no existen
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS INSPECTOR (
            ID_Inspector INTEGER PRIMARY KEY,
            Nombre TEXT,
            Apellido TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS OBRA (
            N_expediente INTEGER PRIMARY KEY,
            Ubicación TEXT,
            Estado TEXT,
            Percent_total_ejec REAL,
            ID_Inspector INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS MATERIAL (
            ID_Material INTEGER PRIMARY KEY,
            Nombre_Material TEXT,
            Stock INTEGER
        )
    """)
    # Insertar datos de ejemplo si las tablas están vacías
    cursor.execute("SELECT COUNT(*) FROM INSPECTOR")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO INSPECTOR VALUES (1, 'Carlos', 'Gómez')")
        cursor.execute("INSERT INTO OBRA VALUES (101, 'Complejo Penitenciario VI', 'En Ejecución', 45.5, 1)")
        cursor.execute("INSERT INTO MATERIAL VALUES (1, 'Cementi 50kg', 120)")
        conn.commit()
    conn.close()

init_db()

st.title("🏗️ Adelanto TP")
st.caption("Vista general de obras, registro de avances y stock de materiales.")

st.sidebar.success("Conectado a Base de Datos (Streamlit Cloud)")

# Pestañas principales
tab1, tab2, tab3 = st.tabs(["Vista General de Obras", "Registrar Avance", "Materiales"])

with tab1:
    st.header("Vista general de obras")
    conn = get_connection()
    query = """
    SELECT O.N_expediente, O.Ubicación, O.Estado, O.Percent_total_ejec, 
        I.Nombre || ' ' || I.Apellido AS Inspector
    FROM OBRA O
    INNER JOIN INSPECTOR I ON O.ID_Inspector = I.ID_Inspector;
    """
    obras = pd.read_sql(query, conn)
    conn.close()
    
    st.metric(label="Obras con inspector asignado", value=len(obras))
    st.dataframe(obras, use_container_width=True)

with tab2:
    st.header("Registrar avance de obra")
    with st.form("form_avance"):
        expediente = st.number_input("Número de Expediente", step=1, min_value=1)
        porcentaje = st.number_input("Porcentaje de Avance (%)", min_value=0.0, max_value=100.0, step=0.1)
        submitted = st.form_submit_button("Actualizar Avance")
        
        if submitted:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE OBRA SET Percent_total_ejec = ? WHERE N_expediente = ?", (porcentaje, expediente))
            conn.commit()
            conn.close()
            st.success("¡Avance registrado exitosamente!")

with tab3:
    st.header("Stock de Materiales")
    conn = get_connection()
    materiales = pd.read_sql("SELECT * FROM MATERIAL;", conn)
    conn.close()
    st.dataframe(materiales, use_container_width=True)
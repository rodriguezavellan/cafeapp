import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams
from PIL import Image


# Configuración de página
st.set_page_config(page_title="Análisis de Ventas de Gio's Café", layout="wide")

# Estilo general café
PRIMARY_BROWN = "#4E342E"
BROWN_PALETTE = ["#6D4C41", "#A1887F", "#BCAAA4", "#8D6E63", "#D7CCC8"]

# Estilo para Streamlit
st.markdown("""
    <style>
        h1, h2, h3, h4, h5, h6, .stMetric, .stText, .stSubheader, .stHeader {
            color: #4E342E !important;
        }
        .css-1v0mbdj, .css-qri22k, .css-h5rgaw {
            color: #4E342E !important;
        }
        .main {
            background-color: #FDF6EC;
        }
    </style>
""", unsafe_allow_html=True)

# Estilo global para gráficos
sns.set_style("whitegrid")
sns.set_palette(BROWN_PALETTE)
rcParams['axes.labelcolor'] = PRIMARY_BROWN
rcParams['xtick.color'] = PRIMARY_BROWN
rcParams['ytick.color'] = PRIMARY_BROWN
rcParams['axes.titlecolor'] = PRIMARY_BROWN
rcParams['axes.edgecolor'] = PRIMARY_BROWN

# Logo
logo = Image.open("logo-cafe.png")
st.image(logo, width=120)

# Sidebar
st.sidebar.title("☕ Navegación")
seccion = st.sidebar.radio("Ir a:", ["🧹 Limpieza de Datos", "📦 Análisis de Producto", "📅 Temporalidad", "💰 Ventas y Patrones"])

# Cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("cafe_limpio.csv", parse_dates=["Transaction Date"])
    #return pd.read_csv("https://github.com/rodriguezavellan/cafeapp/blob/main/cafe_limpio.csv", parse_dates=["Transaction Date"])
    

cafe = cargar_datos()
cafe['Ingreso'] = cafe['Quantity'] * cafe['Price Per Unit']

st.title("Análisis de Ventas de Gio's Café")

# Sección de Limpieza de Datos
if seccion == "🧹 Limpieza de Datos":
    st.header("🧹 Limpieza de Datos")
    st.write("Visualiza la tabla limpia y con columnas nuevas creadas.")
    st.subheader("Vista de tabla Final")
    st.dataframe(cafe.head())

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Código para analizar")
        code = """
        def reporte_valores_invalidos(df, columna, valores_invalidos=['Unknown', 'Error', 'Nan'], imprimir=True):
            conteo_valores = df[columna].value_counts(dropna=False)
            conteo_invalidos = conteo_valores[conteo_valores.index.isin(valores_invalidos)]
            total_invalidos = conteo_invalidos.sum()
            total_filas = len(df)
            porcentaje = (total_invalidos / total_filas) * 100
            return {
                'columna': columna,
                'conteo_por_valor': conteo_invalidos.to_dict(),
                'total_invalidos': total_invalidos,
                'total_filas': total_filas,
                'porcentaje': round(porcentaje, 2)
            }
        """
        st.text_area(" ", code, height=400)

    with col2:
        st.subheader("Explicación")
        st.write("""
        **📍 Columna analizada: 'Payment Method'**  
        Valores inválidos encontrados: NaN, Error, Unknown  
        **Total inválidos:** 3178 de 10000 filas  
        **Porcentaje inválido:** 31.78%

        ---

        **📍 Columna analizada: 'Location'**  
        Valores inválidos encontrados: NaN, Error, Unknown  
        **Total inválidos:** 3961 de 10000 filas  
        **Porcentaje inválido:** 39.61%
        """)
         # Crear dos columnas con proporciones
    col3, col4 = st.columns([2, 1])  # Columna de código más ancha
    
    with col3:
        st.subheader("Código para analizar")
    
        code = """
        # Rellenar Items desconocidos 
        productos_y_precios = dict(zip(cafe['Item'], cafe['Price Per Unit']))
        # Bucle para recorrer el DataFrame y reemplazar 'Producto Desconocido'
        for idx, row in cafe.iterrows():
        # Si el valor de 'Item' es 'Producto Desconocido' y el precio coincide
        
        if row['Item'] == 'Producto Desconocido' and row['Price Per Unit'] in productos_y_precios.values():
        
        # Buscar el nombre del producto cuyo precio coincide
        producto = [producto for producto, precio in productos_y_precios.items() if precio == row['Price Per Unit']]
        
        if producto:
            # Asignar el nombre del producto al 'Item'
            cafe.at[idx, 'Item'] = producto[0]

            # Definir clasificaciones
            bebidas = ['Coffee', 'Smoothie', 'Juice', 'Tea']
            comidas = ['Cake', 'Cookie', 'Salad', 'Sandwich']
            
            # Función clasificadora
            def clasificar_item(item):
                if item in bebidas:
                    return 'Bebida'
                elif item in comidas:
                    return 'Comida'
                else:
                    return 'Otro'  # Para Producto Desconocido u otros no clasificados
        
                # Crear nueva columna 'Tipo'
                cafe['Tipo'] = cafe['Item'].apply(clasificar_item)
                
        """
        # Mostrar el código con scroll
        st.text_area(" ", code, height=400)
    
    with col4:
        st.subheader("Explicación")
        st.write("""
            **📍 Columna analizada: 'Payment Method'**  
            Valores inválidos encontrados:  
            - NaN: 2579  
            - Error: 306  
            - Unknown: 293  
            **Total inválidos:** 3178 de 10000 filas  
            **Porcentaje inválido:** 31.78%
            
            ---
            
            **📍 Columna analizada: 'Location'**  
            Valores inválidos encontrados:  
            - NaN: 3265  
            - Error: 358  
            - Unknown: 338  
            **Total inválidos:** 3961 de 10000 filas  
            **Porcentaje inválido:** 39.61%
            """)

        st.write("### Campos sin valor Desconocido")
        st.dataframe(cafe[['Item']].head(4))
    # --- Sección 1: Análisis de Producto ---
elif seccion == "📦 Análisis de Producto":
    st.header("📦 Análisis de Producto")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("¿Cuáles son los productos más vendidos?")
        ventas_item = cafe.groupby("Item")["Quantity"].sum().sort_values(ascending=False).reset_index()
        fig1, ax1 = plt.subplots()
        sns.barplot(data=ventas_item, x="Quantity", y="Item", ax=ax1, palette="Set2")
        ax1.set_title("Cantidad vendida por producto")
        st.pyplot(fig1)

    with col2:
        st.subheader("¿Qué productos generan mayor ingreso?")
        ingresos_por_producto = cafe.groupby('Item')['Ingreso'].sum().sort_values(ascending=False).reset_index()
        ingresos_por_producto.columns = (['Producto', 'Importe'])

        productos_seleccionados = st.multiselect(
            "Selecciona productos para ver ingresos:",
            opciones := ingresos_por_producto['Producto'].tolist(),
            default=opciones[:3]
        )

        st.dataframe(
            ingresos_por_producto[ingresos_por_producto['Producto'].isin(productos_seleccionados)]
            .reset_index(drop=True),
            use_container_width=True
        )

    st.subheader("¿Hay productos con bajo nivel de ventas que podrían dejar de ofrecerse?")
    producto_menos = ventas_item.iloc[-3:]  # Últimos 3 menos vendidos
    st.dataframe(producto_menos.rename(columns={"Item": "Producto","Quantity": "Cantidad Vendida"}))

# --- Sección 2: Temporalidad ---
elif seccion == "📅 Temporalidad":
    st.header("📅 Temporalidad")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("¿En qué días de la semana se produce mayor volumen de ventas?")
        dias_ventas = cafe.groupby("Día")["Quantity"].sum().reset_index().sort_values("Quantity", ascending=False)
        fig3, ax3 = plt.subplots()
        sns.barplot(data=dias_ventas, x="Día", y="Quantity", ax=ax3, palette="coolwarm")
        ax3.set_title("Cantidad vendida por día")
        ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45)
        st.pyplot(fig3)

    with col2:
        st.subheader("¿Hubo algún mes particularmente alto o bajo en términos de facturación?")
        ingresos_mes = cafe.groupby("Mes")["Ingreso"].sum().reset_index().sort_values("Ingreso", ascending=False)
        fig4, ax4 = plt.subplots()
        sns.barplot(data=ingresos_mes, x="Mes", y="Ingreso", ax=ax4, palette="Blues")
        ax4.set_title("Ingresos mensuales")
        ax4.set_xticklabels(ax4.get_xticklabels(), rotation=45)
        st.pyplot(fig4)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Mayor 📊Cantidad de Ventas por Mes")
        Venta_por_mes = cafe.groupby("Mes")["Quantity"].sum().reset_index().sort_values(by="Quantity", ascending=False)
        Venta_por_mes.columns = ["Mes", "Cantidad"]


        # Mostrar la tabla (opcional)
        st.dataframe(Venta_por_mes)
        
        st.subheader("Mayor 💰 Importe de Ventas por Mes")
        Venta_por_mes = cafe.groupby("Mes")["Total Spent"].sum().reset_index().sort_values(by="Total Spent", ascending=False)
        Venta_por_mes.columns = ["Mes", "Cantidad"]


        # Mostrar la tabla (opcional)
        st.dataframe(Venta_por_mes)

        

    with col4:
       

        # Crear ventas_ingresos_mes con cantidad e ingreso por mes
        ventas_ingresos_mes = cafe.groupby("Mes").agg({
            "Item": "count",               # Cantidad de ventas
            "Total Spent": "sum"          # Ingreso total
        }).reset_index()
        
        ventas_ingresos_mes.columns = ["Mes", "Cantidad", "Ingreso"]
        
        # Crear Venta_por_mes para encontrar el mes con mayor importe
        Venta_por_mes = cafe.groupby("Mes")["Total Spent"].sum().reset_index().sort_values(by="Total Spent", ascending=False)
        Venta_por_mes.columns = ["Mes", "Cantidad"]
        
        # Mostrar en la app
        st.subheader("📊 Cantidad Vendida vs Ingresos por Mes")
        
        # Gráfico de barras y línea
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Crear gráfico combinado de cantidad vs ingresos por mes
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Barras: Cantidad de ventas
        color_barras = 'tab:blue'
        ax1.set_xlabel('Mes')
        ax1.set_ylabel('Cantidad', color=color_barras)
        ax1.bar(
            ventas_ingresos_mes["Mes"].values, 
            ventas_ingresos_mes["Cantidad"].values, 
            color=color_barras, 
            alpha=0.6
        )
        ax1.tick_params(axis='y', labelcolor=color_barras)
        
        # Línea: Ingreso
        ax2 = ax1.twinx()
        color_linea = 'tab:green'
        ax2.set_ylabel('Ingreso ($)', color=color_linea)
        ax2.plot(
            ventas_ingresos_mes["Mes"].values, 
            ventas_ingresos_mes["Ingreso"].values, 
            color=color_linea, 
            marker='o', 
            linewidth=2
        )
        ax2.tick_params(axis='y', labelcolor=color_linea)
        
        # Títulos y formato
        plt.title("📈 Cantidad Vendida vs Ingresos por Mes", fontsize=14, fontweight='bold')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.4)
        plt.tight_layout()
        
        # Mostrar en la app
        st.pyplot(fig)
        
        # Mostrar el mes con mayor importe
        st.markdown("### 🏆 Mes con mayor importe de ventas")
        st.dataframe(Venta_por_mes.head(1))
          

# --- Sección 3: Ventas y Patrones Generales ---
if seccion == "💰 Ventas y Patrones":
    st.header("💰 Ventas y Patrones Generales")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("¿Cuál es el ticket promedio por operación?")
        ticket_promedio = cafe["Ingreso"].mean()
        st.metric(label="Ticket promedio", value=f"${ticket_promedio:.2f}")

        st.subheader("Ticket Promedio Comida Bebida")
        ticket_tipo = cafe.groupby("Tipo")["Ingreso"].mean().reset_index()
        st.dataframe(ticket_tipo)

        st.subheader("¿Existen diferencias entre semana y fin de semana?")
        cafe["Tipo Día"] = cafe["Día"].apply(lambda x: "Fin de semana" if x in ["Sábado", "Domingo"] else "Semana")
        ticket_tipo_dia = cafe.groupby("Tipo Día")["Ingreso"].mean().reset_index()
        sns.barplot(data=ticket_tipo_dia, x="Tipo Día", y="Ticket Promedio", palette="muted")
        plt.title("Ticket Promedio: Semana vs Fin de Semana")
        plt.ylabel("Importe promedio ($)")
        plt.xlabel("Tipo de Día")
        plt.tight_layout()
        st.pyplot(plt)

    with col2:
        st.subheader("¿Cómo varía la facturación diaria?")
        fact_diaria = cafe.groupby("Transaction Date")["Ingreso"].sum().reset_index()
        fig5, ax5 = plt.subplots()
        sns.lineplot(data=fact_diaria, x="Transaction Date", y="Ingreso", ax=ax5)
        ax5.set_title("Facturación diaria")
        ax5.set_ylabel("Ingreso ($)")
        ax5.set_xlabel("Fecha")
        st.pyplot(fig5)

    st.subheader("¿Qué categoría de productos predomina en las ventas?")
    tipo_resumen = cafe.groupby("Tipo")["Ingreso"].sum().reset_index()
    fig7, ax7 = plt.subplots()
    sns.barplot(data=tipo_resumen, x="Tipo", y="Ingreso", ax=ax7, palette="Accent")
    ax7.set_title("Ingreso total: Comida vs Bebida")
    st.pyplot(fig7)

    st.subheader("Producto con buenas ventas y buen precio")
    productos_resumen = cafe.groupby("Item")[["Quantity", "Ingreso"]].sum().reset_index()
    productos_resumen["Precio Promedio"] = productos_resumen["Ingreso"] / productos_resumen["Quantity"]
    umbral_volumen = productos_resumen["Quantity"].quantile(0.75)
    umbral_precio_promedio = productos_resumen["Precio Promedio"].mean()

    productos_destacados = productos_resumen[
        (productos_resumen["Quantity"] > umbral_volumen) &
        (productos_resumen["Precio Promedio"] > umbral_precio_promedio)
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=productos_destacados,
        x="Quantity",
        y="Precio Promedio",
        hue="Item",
        palette="viridis",
        s=100,
        ax=ax
    )
    ax.set_title("Productos Destacados: Alto Volumen y Buen Precio Promedio")
    ax.set_xlabel("Cantidad Vendida")
    ax.set_ylabel("Precio Promedio por Producto")
    ax.legend(title="Producto", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("¿Qué productos combinan un volumen alto con un buen precio promedio?")
    resumen_productos = cafe.groupby("Item").agg({"Quantity": "sum", "Price Per Unit": "mean"}).reset_index()
    fig8, ax8 = plt.subplots()
    sns.scatterplot(data=resumen_productos, x="Quantity", y="Price Per Unit", hue="Item", s=100, palette="Set2")
    ax8.set_title("Volumen vs Precio Promedio")
    st.pyplot(fig8)
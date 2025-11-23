import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
from scipy.stats import norm
import streamlit.components.v1 as components

# Configuración de la página
st.set_page_config(layout="wide", page_title="Simulación TLC - Concurso Docente")

# Título y Descripción
st.title("🎯 El Teorema del Límite Central: De la Geometría a la Normal")
st.markdown("""
Esta simulación demuestra cómo el **promedio** de variables aleatorias independientes (dardos en una diana) 
converge a una Distribución Normal, independientemente de la distribución original, revelando el orden dentro del caos.
""")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("⚙️ Configuración del Experimento")

# 1. Parámetros seleccionables por el usuario
n_tiros = st.sidebar.number_input("Dardos por día (n)", min_value=1, max_value=200, value=10, step=1)
n_dias = st.sidebar.slider("Total de días a simular", min_value=500, max_value=5000, value=2000, step=100)
velocidad = st.sidebar.slider("Velocidad de animación (Días/Frame)", min_value=10, max_value=200, value=50)

# Botón de inicio
start_btn = st.sidebar.button("▶️ Iniciar Simulación", type="primary")

# --- LÓGICA DE SIMULACIÓN ---
if start_btn:
    # Usamos un spinner para indicar que está calculando (la generación del video toma unos segundos)
    with st.spinner('Lanzando miles de dardos y generando animación... por favor espera...'):
        
        # Configuración estética
        plt.style.use('dark_background')
        
        # --- 1. CÁLCULO MATEMÁTICO ---
        total_tiros = n_dias * n_tiros
        
        # Generación de coordenadas en el disco (Uniforme)
        r_raw = np.sqrt(np.random.uniform(0, 1, total_tiros))
        theta_raw = np.random.uniform(0, 2 * np.pi, total_tiros)
        x_raw = r_raw * np.cos(theta_raw)
        y_raw = r_raw * np.sin(theta_raw)
        
        # Agrupar por días y calcular PROMEDIOS
        x_matrix = x_raw.reshape((n_dias, n_tiros))
        y_matrix = y_raw.reshape((n_dias, n_tiros))
        
        x_promedios = np.mean(x_matrix, axis=1)
        y_promedios = np.mean(y_matrix, axis=1)
        
        # --- 2. CÁLCULO DE LA CURVA TEÓRICA DINÁMICA ---
        varianza_poblacion = 0.25
        sigma_teorico = np.sqrt(varianza_poblacion / n_tiros)
        
        # Generar curva normal perfecta
        x_teorico = np.linspace(-0.6, 0.6, 200)
        y_teorico = norm.pdf(x_teorico, 0, sigma_teorico)
        
        # --- 3. CONFIGURACIÓN VISUAL ---
        fig = plt.figure(figsize=(14, 5))
        # Ajustamos un poco los márgenes para web
        plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.15)
        
        fig.suptitle(f'Convergencia con n={n_tiros} dardos/día', fontsize=18, color='white', fontweight='bold')
        gs = GridSpec(1, 3, figure=fig)
        
        # PANEL 1: La Diana
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.set_xlim(-0.7, 0.7); ax1.set_ylim(-0.7, 0.7)
        ax1.set_aspect('equal')
        ax1.add_patch(plt.Circle((0, 0), 1, color='green', fill=False, ls='--', alpha=0.3))
        scat_promedios = ax1.scatter([], [], s=15, c=[], cmap='cool', alpha=0.6, vmin=-0.5, vmax=0.5)
        ax1.set_title("1. Promedios (Vista Real)", color='cyan')
        ax1.axis('off')
        
        # PANEL 2: Densidad
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.set_title("2. Mapa de Calor", color='orange')
        bins_2d = np.linspace(-0.6, 0.6, 40)
        hist_data = np.zeros((len(bins_2d)-1, len(bins_2d)-1))
        mesh = ax2.pcolormesh(bins_2d, bins_2d, hist_data, cmap='inferno', shading='auto')
        ax2.set_aspect('equal'); ax2.axis('off')
        
        # PANEL 3: Histograma
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.set_title("3. Distribución Marginal X", color='lime')
        ax3.set_xlim(-0.6, 0.6)
        ax3.set_yticks([])
        
        bins_x = np.linspace(-0.6, 0.6, 50)
        _, _, bar_container = ax3.hist([], bins=bins_x, density=True, color='lime', alpha=0.6, edgecolor='black')
        
        ax3.plot(x_teorico, y_teorico, color='white', linestyle='--', linewidth=2.5, label='Normal Teórica')
        ax3.legend(loc='upper right', fontsize=8, frameon=False)
        
        info_text = fig.text(0.5, 0.02, '', ha='center', color='white', fontsize=12)
        
        # --- 4. ANIMACIÓN ---
        def update(frame):
            idx = (frame + 1) * velocidad
            if idx > n_dias: idx = n_dias
            
            x_c = x_promedios[:idx]
            y_c = y_promedios[:idx]
            
            # 1. Scatter
            scat_promedios.set_offsets(np.c_[x_c, y_c])
            scat_promedios.set_array(x_c)
            
            # 2. Mapa de Calor
            H, _, _ = np.histogram2d(x_c, y_c, bins=bins_2d)
            mesh.set_array(H.T.ravel())
            mesh.set_clim(0, H.max())
            
            # 3. Histograma
            counts, _ = np.histogram(x_c, bins=bins_x, density=True)
            max_h_data = 0
            for count, rect in zip(counts, bar_container.patches):
                rect.set_height(count)
                if count > max_h_data: max_h_data = count
            
            # Ajuste dinámico de altura
            current_max_y = max(max_h_data, np.max(y_teorico)) * 1.15
            ax3.set_ylim(0, current_max_y if current_max_y > 0 else 1)
            
            info_text.set_text(f'Días simulados: {idx} / {n_dias}')
            
            return scat_promedios, mesh, *bar_container.patches, info_text

        # Calcular frames y generar HTML
        num_frames = int(np.ceil(n_dias / velocidad))
        anim = animation.FuncAnimation(fig, update, frames=num_frames, interval=30, blit=False)
        
        # Renderizar como componente HTML (JavaScript)
        # Esto mantiene la fluidez perfecta de la animación
        components.html(anim.to_jshtml(), height=600)
        
        st.success("Simulación completada. Observa cómo la curva verde se ajusta a la teórica blanca.")
else:
    # Mensaje de bienvenida
    st.info("👈 Configura los parámetros en el menú izquierdo y presiona 'Iniciar Simulación'.")

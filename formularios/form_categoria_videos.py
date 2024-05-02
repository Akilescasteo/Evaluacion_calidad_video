# Paso 2. Selección de video por categoría
import tkinter as tk
from PIL import Image, ImageTk  # Para manejo de imágenes
import util.util_imagenes as util_img  # Utilidades para el manejo de rutas de imágenes
from config import COLOR_BARRA_SUPERIOR, COLOR_MENU_LATERAL, COLOR_VERDE_OSCURO  # Importación de colores desde configuración
from formularios.FormularioSeleccionEscalabilidad import FormularioSeleccionEscalabilidad
from tkinter import Label  # Importar Label específicamente para etiquetas de imagen

# Definición de la clase FormularioSeleccionVideo, que extiende de tk.Frame
class FormularioSeleccionVideo(tk.Frame):
    def __init__(self, master, categoria, cambio_panel_callback=None):
        super().__init__(master)  # Inicialización de la clase base
        self.cambio_panel_callback = cambio_panel_callback  # Callback para cambio de panel
        self.categoria = categoria  # Categoría actual para la selección de video
        
        # Diccionario que mapea claves de categorías a archivos de video
        self.videos = {
            "1": ["akiyo_cif.yuv", "deadline_cif.yuv"],
            "2": ["football_cif.yuv", "soccer_cif.yuv"],
            "3": ["BigBuckBunny_cif.yuv", "ElephantsDream_cif.yuv"],
            "4": ["crew_cif.yuv", "football4_cif.yuv"],
            "5": ["bus_cif.yuv", "HallMonitor_cif.yuv"]
        }

        # Configuración inicial de Canvas y Scrollbars
        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")  # Canvas sin bordes y fondo blanco
        self.frame = tk.Frame(self.canvas, background="#ffffff")  # Frame dentro del canvas con el mismo fondo
        self.vsb = tk.Scrollbar(self, bg=COLOR_BARRA_SUPERIOR, orient="vertical", command=self.canvas.yview)  # Barra de desplazamiento vertical
        self.hsb = tk.Scrollbar(self, bg=COLOR_BARRA_SUPERIOR, orient="horizontal", command=self.canvas.xview)  # Barra de desplazamiento horizontal
        self.canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)  # Configuración de las barras de desplazamiento al canvas

        # Empaquetado de los componentes
        self.vsb.pack(side="right", fill="y")  # Barra vertical a la derecha
        self.hsb.pack(side="bottom", fill="x")  # Barra horizontal abajo
        self.canvas.pack(side="left", fill="both", expand=True)  # Canvas a la izquierda
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")  # Creación de una ventana dentro del canvas para el frame
        self.frame.bind("<Configure>", self.onFrameConfigure)  # Evento de configuración para ajustar el scroll

        self.ancho_menu = 10  # Ancho predeterminado para botones de selección
        self.alto_menu = 3  # Alto predeterminado para botones de selección
        self.mostrar_videos()  # Método para mostrar videos según la categoría

    def mostrar_videos(self):
        fuente_botones = ('Helvetica', 15)  # Fuente y tamaño para los botones
        videos = self.videos[self.categoria] if self.categoria in self.videos else []  # Obtener videos de la categoría o lista vacía si no hay correspondencia

        row = 0  # Inicializar fila
        column = 0  # Inicializar columna
        for i, video in enumerate(videos):  # Iterar sobre los videos obtenidos
            nombre_base = video.split('.')[0]  # Obtener el nombre base del archivo
            ruta_imagen = util_img.obtener_ruta_base() + f"/imagenes/{nombre_base}.png"  # Ruta a la imagen asociada al video
            imagen_original = Image.open(ruta_imagen)  # Abrir la imagen
            imagen_redimensionada = imagen_original.resize((352, 288), Image.Resampling.LANCZOS)  # Redimensionar la imagen
            imagen = ImageTk.PhotoImage(imagen_redimensionada)  # Convertir la imagen para uso en tkinter
            
            label_imagen = Label(self.frame, image=imagen)  # Crear una etiqueta para la imagen
            label_imagen.image = imagen  # Guardar la imagen en una propiedad para evitar que sea eliminada por el recolector de basura
            label_imagen.grid(row=row, column=column, padx=10, pady=10)  # Posicionar la etiqueta de imagen

            boton = tk.Button(self.frame, text=video, bd=0, bg=COLOR_MENU_LATERAL, fg="white",  # Botón para seleccionar el video
                              font=fuente_botones, width=self.ancho_menu, height=self.alto_menu,  # Configuración de fuente y tamaño
                              command=lambda v=video: self.seleccionar_video(v))  # Comando al presionar el botón
            boton.grid(row=row + 1, column=column, padx=10, pady=2, sticky='ew')  # Posicionar el botón

            column += 1  # Incrementar la columna
            if column > 1:  # Si se excede el número de columnas permitidas, reiniciar columna y aumentar fila
                column = 0
                row += 2

        boton_regresar = tk.Button(self.frame, text="Regresar", bd=0, bg=COLOR_VERDE_OSCURO, fg="white",  # Botón para regresar
                                   font=fuente_botones, command=self.accion_regresar)  # Configuración del botón
        boton_regresar.grid(row=row + 1, column=0, columnspan=2, padx=10, pady=2, sticky='ew')  # Posicionar el botón de regreso

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))  # Ajustar la región desplazable para abarcar todo el frame

    def accion_regresar(self):
        from formularios.form_videos import FormularioVideosDesign  # Importar formulario de videos
        if self.cambio_panel_callback:
            self.cambio_panel_callback(FormularioVideosDesign)  # Llamar al callback de cambio de panel

    def seleccionar_video(self, video):
        print(f"Vídeo seleccionado: {video}")  # Imprimir en consola el video seleccionado
        if self.cambio_panel_callback:
            self.cambio_panel_callback(FormularioSeleccionEscalabilidad, video, self.categoria)  # Llamar al callback con los parámetros necesarios
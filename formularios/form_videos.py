# Paso 1. Aquí se detallan las categorías de los videos con sus respectivas imágenes
# Importación de módulos y paquetes necesarios para la interfaz gráfica y manejo de imágenes
import tkinter as tk
from config import COLOR_BARRA_SUPERIOR  # Importar color definido en archivo de configuración
from formularios.form_categoria_videos import FormularioSeleccionVideo
import util.util_imagenes as util_img  # Módulo para manejo de rutas de imágenes
from PIL import Image, ImageTk  # Importar funcionalidades para manejar imágenes
from tkinter import Label  # Importar componente Label

# Definición de la clase FormularioVideosDesign, que extiende de tk.Frame
class FormularioVideosDesign(tk.Frame):
    def __init__(self, master, cambio_panel_callback=None):
        super().__init__(master)  # Inicialización de la clase base
        self.cambio_panel_callback = cambio_panel_callback  # Callback para cambio de panel
        
        # Obtiene la ruta base donde se encuentran las imágenes
        ruta_imagen = util_img.obtener_ruta_base()
        # Diccionario que mapea claves de categoría a sus nombres
        self.categorias = {
            "1": "Video Conferencia",
            "2": "Entretenimiento",
            "3": "Animaciones",
            "4": "Tiempo Real",
            "5": "Video Vigilancia"
        }
        # Diccionario que mapea claves de categoría a rutas de imágenes asociadas
        self.categoria_imagenes = {
            "1": [ruta_imagen + "/imagenes/akiyo_cif.png", ruta_imagen + "/imagenes/deadline_cif.png"],
            "2": [ruta_imagen + "/imagenes/football_cif.png", ruta_imagen + "/imagenes/soccer_cif.png"],
            "3": [ruta_imagen + "/imagenes/BigBuckBunny_cif.png", ruta_imagen + "/imagenes/ElephantsDream_cif.png"],
            "4": [ruta_imagen + "/imagenes/crew_cif.png", ruta_imagen + "/imagenes/football4_cif.png"],
            "5": [ruta_imagen + "/imagenes/bus_cif.png", ruta_imagen + "/imagenes/HallMonitor_cif.png"]
        }
        
        # Creación de un canvas para manejar el contenido desplazable y barras de desplazamiento
        self.canvas = tk.Canvas(self)  # Crear el canvas dentro del frame actual
        self.v_scroll = tk.Scrollbar(self, bg=COLOR_BARRA_SUPERIOR, orient='vertical', command=self.canvas.yview)  # Barra vertical
        self.h_scroll = tk.Scrollbar(self, bg=COLOR_BARRA_SUPERIOR, orient='horizontal', command=self.canvas.xview)  # Barra horizontal
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)  # Configurar el canvas con las barras

        # Empaquetado de los widgets dentro del frame
        self.v_scroll.pack(side='right', fill='y')  # Empaquetado de la barra vertical
        self.h_scroll.pack(side='bottom', fill='x')  # Empaquetado de la barra horizontal
        self.canvas.pack(side='left', fill='both', expand=True)  # Empaquetado del canvas

        # Creación de un frame interior dentro del canvas para colocar contenido
        self.interior = tk.Frame(self.canvas)  # Crear frame interior
        self.canvas.create_window((0, 0), window=self.interior, anchor='nw')  # Colocar el frame interior en el canvas

        self.crear_botones_categoria()  # Llamada al método para crear los botones de categoría

        # Configuración de un evento para ajustar la región desplazable del canvas según el contenido
        self.interior.bind('<Configure>', self._on_frame_configure)

    def crear_botones_categoria(self):
        row = 0
        column = 0
        # Iterar sobre cada categoría para crear su representación visual
        for clave, categoria in self.categorias.items():
            frame_categoria = tk.Frame(self.interior, bg='white', cursor="hand2")  # Frame para cada categoría
            frame_categoria.grid(row=row, column=column, padx=10, pady=5, sticky="nsew")  # Usar grid para posicionar
            self.interior.grid_columnconfigure(column, weight=1)  # Ajustar la configuración de las columnas
            self.interior.grid_rowconfigure(row, weight=1)  # Ajustar la configuración de las filas

            # Vinculación del evento de clic al frame
            frame_categoria.bind('<Button-1>', lambda e, c=clave: self.seleccionar_categoria(c))

            label_titulo = tk.Label(frame_categoria, text=categoria, font=('Helvetica', 18, 'bold'), bg='white')  # Etiqueta con el título
            label_titulo.grid(row=0, column=0, sticky="ew")  # Posicionamiento de la etiqueta
            label_titulo.bind('<Button-1>', lambda e, c=clave: self.seleccionar_categoria(c))  # Vinculación del clic a la etiqueta

            frame_contenido = tk.Frame(frame_categoria, bg='white')  # Frame para las imágenes
            frame_contenido.grid(row=1, column=0, sticky="ew")  # Posicionamiento del frame de imágenes
            frame_contenido.bind('<Button-1>', lambda e, c=clave: self.seleccionar_categoria(c))  # Vinculación del clic al frame de imágenes

            images = []  # Lista para almacenar objetos de imagen
            for imagen_path in self.categoria_imagenes[clave]:  # Cargar cada imagen
                imagen = Image.open(imagen_path)  # Abrir la imagen
                imagen = imagen.resize((352, 288), Image.Resampling.LANCZOS)  # Redimensionar la imagen
                photo = ImageTk.PhotoImage(imagen)  # Convertir a formato utilizable en tkinter
                images.append(photo)  # Agregar al listado de imágenes

            # Colocar cada imagen en el frame y vincular eventos
            for i, photo in enumerate(images):
                label_imagen = tk.Label(frame_contenido, image=photo, bg='white')  # Crear label para la imagen
                label_imagen.image = photo  # Asignar la imagen al label para evitar que se limpie por el recolector de basura
                label_imagen.grid(row=0, column=i, padx=5)  # Posicionamiento de la imagen
                label_imagen.bind('<Button-1>', lambda e, c=clave: self.seleccionar_categoria(c))  # Vinculación del clic a la imagen

            column += 1  # Incrementar la columna para colocar el siguiente conjunto
            if column > 1:  # Si se alcanza el límite de columnas, se reinicia y se aumenta la fila
                column = 0
                row += 1

    def _on_frame_configure(self, event=None):
        # Ajuste del área desplazable del canvas según su contenido
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def seleccionar_categoria(self, categoria_clave):
        # Método para manejar la selección de una categoría
        print(f"Categoría seleccionada: {self.categorias[categoria_clave]}")  # Mostrar en consola la categoría seleccionada
        if self.cambio_panel_callback:  # Si existe un callback definido, llamarlo con los parámetros necesarios
            self.cambio_panel_callback(FormularioSeleccionVideo, categoria_clave)
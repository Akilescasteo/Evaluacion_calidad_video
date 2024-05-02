#Paso 3: Codificación de video
import tkinter as tk
import subprocess # Para ejecutar comandos del sistema
import os # Para manipulación de rutas y directorios
import threading # Para ejecución de procesos en paralelo
import util.util_ventana as util_ventana # Utilidad para centrar ventanas
from tkinter import messagebox # Para mostrar mensajes emergentes
from tkinter import simpledialog # Para solicitar datos al usuario
from config import COLOR_MENU_LATERAL, COLOR_VERDE_OSCURO, COLOR_MENU_CURSOR_ENCIMA # Configuración de colores
from formularios.FormularioReproducir import VideoPlayer # Formulario para reproducir video

# Definición de la clase FormularioSeleccionEscalabilidad, que extiende de tk.Frame
class FormularioSeleccionEscalabilidad(tk.Frame):
    def __init__(self, master, video_seleccionado, categoria, cambio_panel_callback=None):
        super().__init__(master) # Inicialización de la clase base
        self.video_seleccionado = video_seleccionado # Video seleccionado para codificar
        self.cambio_panel_callback = cambio_panel_callback # Callback para cambio de panel
        self.categoria = categoria  # Categoría del video
        self.ancho_menu = 20  # Ancho estandarizado para botones
        self.alto_menu = 4  # Alto estandarizado para botones
        self.crear_opciones_escalabilidad()  # Método para crear opciones de escalabilidad

    def crear_opciones_escalabilidad(self): 
        fuente_botones = ('Helvetica', 15) # Fuente para los botones
        
        # Botón para calidad (QP)
        boton = tk.Button(self, text="Calidad (QP)", bd=0, bg=COLOR_MENU_LATERAL, fg="white",
                              font=fuente_botones,  # Aplica la fuente y tamaño definido
                              width=self.ancho_menu, height=self.alto_menu, command=lambda: self.seleccionar_escalabilidad("qp"))
        boton.pack(pady=2, padx=10, fill=tk.X)
        boton.bind("<Enter>", lambda e, b=boton: b.config(bg=COLOR_MENU_CURSOR_ENCIMA), add='+')
        boton.bind("<Leave>", lambda e, b=boton: b.config(bg=COLOR_MENU_LATERAL), add='+')

        # Botón para escala temporal (FPS)
        boton1 = tk.Button(self, text="Temporal (FPS)", bd=0, bg=COLOR_MENU_LATERAL, fg="white",
                              font=fuente_botones,  # Aplica la fuente y tamaño definido
                              width=self.ancho_menu, height=self.alto_menu, command=lambda: self.seleccionar_escalabilidad("fps"))

        boton1.pack(pady=2, padx=10, fill=tk.X)
        boton1.bind("<Enter>", lambda e, b=boton1: b.config(bg=COLOR_MENU_CURSOR_ENCIMA), add='+')
        boton1.bind("<Leave>", lambda e, b=boton1: b.config(bg=COLOR_MENU_LATERAL), add='+')

        # Botón para escala espacial (Bitrate)
        boton2 = tk.Button(self, text="Espacial (Bitrate)", bd=0, bg=COLOR_MENU_LATERAL, fg="white",
                              font=fuente_botones,  # Aplica la fuente y tamaño definido
                              width=self.ancho_menu, height=self.alto_menu, command=lambda: self.seleccionar_escalabilidad("bitrate"))

        boton2.pack(pady=2, padx=10, fill=tk.X)
        boton2.bind("<Enter>", lambda e, b=boton2: b.config(bg=COLOR_MENU_CURSOR_ENCIMA), add='+')
        boton2.bind("<Leave>", lambda e, b=boton2: b.config(bg=COLOR_MENU_LATERAL), add='+')
        
        # Botón para regresar al menú anterior
        boton_regresar = tk.Button(self, text="Regresar", bd=0, bg=COLOR_VERDE_OSCURO, fg="white",
                               font=('Helvetica', 15),
                               width=self.ancho_menu, height=self.alto_menu, command=self.accion_regresar)
        boton_regresar.pack(pady=2, padx=10, fill=tk.X)

    def accion_regresar(self):
        # Método para manejar la acción de regreso
        print("Regreso")
        from formularios.form_categoria_videos import FormularioSeleccionVideo
        if self.cambio_panel_callback:
            self.cambio_panel_callback(FormularioSeleccionVideo, self.categoria)

    def seleccionar_escalabilidad(self, tipo_escalabilidad):
        # Método para seleccionar la escalabilidad y validar la entrada
        valor = None
        while valor is None:
            if tipo_escalabilidad == "qp":
                valor_temporal = simpledialog.askstring("Input", f"Ingrese el valor para {tipo_escalabilidad} (0 - 60):")
                if valor_temporal.isdigit() and 0 <= int(valor_temporal) <= 60:
                    valor = valor_temporal
                else:
                    messagebox.showerror("Valor fuera de rango", "Ocurrió un error con el valor proporcionado. Por favor, intente de nuevo.")
                    print("Valor fuera de rango. Intente de nuevo.")
            elif tipo_escalabilidad == "fps":
                valor_temporal = simpledialog.askstring("Input", f"Ingrese el valor para {tipo_escalabilidad} (2 - 30):")
                if valor_temporal.isdigit() and 2 <= int(valor_temporal) <= 30:
                    valor = valor_temporal
                else:
                    messagebox.showerror("Valor fuera de rango", "Ocurrió un error con el valor proporcionado. Por favor, intente de nuevo.")
                    print("Valor fuera de rango. Intente de nuevo.")
            elif tipo_escalabilidad == "bitrate":
                valor_temporal = simpledialog.askstring("Input", f"Ingrese el valor para {tipo_escalabilidad} (25k - ...):")
                if valor_temporal.lower().endswith('k') and valor_temporal[:-1].isdigit() and int(valor_temporal[:-1]) >= 25:
                    valor = valor_temporal
                else:
                    messagebox.showerror("Valor fuera de rango", "Ocurrió un error con el valor proporcionado. Por favor, intente de nuevo.")
                    print("Valor fuera de rango. Intente de nuevo.")
            else:
                print("Tipo de escalabilidad no soportado.")
                break

        if valor:
            print(f"Escalabilidad seleccionada: {tipo_escalabilidad}, Valor: {valor}")
            # Llamada al método de codificación
            self.mostrar_ventana_carga(tipo_escalabilidad, valor)
        else:
            print("Debe proporcionar un valor para la escalabilidad.")
    
    def mostrar_ventana_carga(self, tipo_escalabilidad, valor):
        # Método para mostrar una ventana de carga durante la codificación
        self.ventana_carga = tk.Toplevel(self)
        self.ventana_carga.title("Codificando")
        anchura = 400
        altura = 100
        util_ventana.centrar_ventana(self.ventana_carga, anchura, altura)
        self.label_carga = tk.Label(self.ventana_carga, text="Codificado el video", font=('Helvetica', 10))
        self.label_carga.pack(expand=True)
        self.ventana_carga.grab_set()  # Hace la ventana modal
        self.ventana_carga.update_idletasks()  # Actualiza la UI
        
        self.cargar_completado = False
        # Inicia el proceso de codificación en un hilo separado
        threading.Thread(target=lambda: self.codificar_video(tipo_escalabilidad, valor), daemon=True).start()
        self.ventana_carga.after(100, self.verificar_codificacion_completada)

    def verificar_codificacion_completada(self):
        # Método para verificar el estado de la codificación
        if self.cargar_completado:
            self.ventana_carga.destroy()  # Cierra la ventana cuando la codificación ha terminado
            messagebox.showinfo("Codificación Exitosa", "El video se reproducirá cuando se presione OK")
        else:
            self.ventana_carga.after(100, self.verificar_codificacion_completada)

    def codificar_video(self, tipo_escalabilidad, valor_escalabilidad):
        # Método para ejecutar el proceso de codificación de video usando FFmpeg
        script_dir = os.path.dirname(os.path.abspath(__file__)) # Directorio del script actual
        documentos_dir = os.path.join(os.path.expanduser('~'), 'Documentos') # Directorio de documentos del usuario
        ruta_salida = os.path.join(documentos_dir, 'Calidad_Video', 'Videos_Codificados') # Ruta de salida para videos codificados
        os.makedirs(ruta_salida, exist_ok=True) # Crear la carpeta si no existe

        # Diccionario para mapear números de categoría a nombres
        categorias = {
            "1": "Video_Conferencia",
            "2": "Entretenimiento",
            "3": "Animaciones",
            "4": "Tiempo_Real",
            "5": "Video_Vigilancia"
        }
        
        nombre_categoria = categorias.get(self.categoria, "Desconocido") # Obtener nombre de la categoría

        video_entrada = os.path.join(script_dir, f"Videos/{nombre_categoria}/{self.video_seleccionado}") # Ruta del video de entrada
        print(video_entrada)
        print(ruta_salida)
        os.makedirs(ruta_salida, exist_ok=True)
        # Comando base de FFmpeg
        ffmpeg_command = [  
            "ffmpeg",
            "-s", "cif",
            "-y",
            "-i", video_entrada,
            "-vcodec", "libx264",
            "-s", "cif"
        ]

        # Ajuste del comando FFmpeg basado en la elección del usuario
        if tipo_escalabilidad == "qp":
            ffmpeg_command.extend(["-qp", valor_escalabilidad])
            video_salida = f"{self.video_seleccionado.split('.')[0]}_qp_{valor_escalabilidad}.mp4"
            print(video_salida)
            archivo_salida_completo = os.path.join(ruta_salida, video_salida)
            print(archivo_salida_completo)
        elif tipo_escalabilidad == "fps":
            ffmpeg_command.extend(["-r", valor_escalabilidad])
            video_salida = f"{self.video_seleccionado.split('.')[0]}_fps_{valor_escalabilidad}.mp4"
            print(video_salida)
            archivo_salida_completo = os.path.join(ruta_salida, video_salida)
            print(archivo_salida_completo)
        elif tipo_escalabilidad == "bitrate":
            ffmpeg_command.extend(["-b:v", valor_escalabilidad])
            video_salida = f"{self.video_seleccionado.split('.')[0]}_bitrate_{valor_escalabilidad}.mp4"
            print(video_salida)
            archivo_salida_completo = os.path.join(ruta_salida, video_salida)
            print(archivo_salida_completo)
        
        ffmpeg_command.append(archivo_salida_completo) # Agregar ruta de salida al comando

        # Ejecutar el comando FFmpeg y manejar posibles errores
        try:
            subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(f"La codificación fue exitosa. Archivo guardado en: {archivo_salida_completo}")
            self.cargar_completado = True # Marcar la codificación como completada
            respuesta = messagebox.showinfo("Codificación Exitosa", "El video se reproducirá cuando se presione OK")
            if respuesta == "ok":
                self.cambio_panel_callback(VideoPlayer, archivo_salida_completo, self.categoria, self.video_seleccionado)

        except subprocess.CalledProcessError as e:
            print("Ocurrió un error durante la codificación:", e.stderr)
            messagebox.showerror("Error en la Codificación", "Ocurrió un error durante la codificación. Por favor, intente de nuevo.")
            self.cargar_completado = True # Aún en caso de error, marcar como completada para cerrar la ventana de carga
#Paso 5. Listar videos codificados
import tkinter as tk
from tkinter import messagebox
import os
import cv2
from PIL import Image, ImageTk
import threading
import random
import util.util_ventana as util_ventana
from config import COLOR_BARRA_SUPERIOR, COLOR_MENU_LATERAL, COLOR_VERDE_OSCURO, COLOR_ROJO_OSCURO

class FormularioListaVideos(tk.Frame):
    def __init__(self, master, formulario_maestro, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.formulario_maestro = formulario_maestro

        self.contenedor_principal = tk.Frame(self)
        self.contenedor_principal.pack(fill='both', expand=True, side=tk.TOP)

        self.contenedor_canvas = tk.Frame(self.contenedor_principal)
        self.contenedor_canvas.pack(fill='both', expand=True)

        self.scrollbar_v = tk.Scrollbar(self.contenedor_canvas, bg=COLOR_BARRA_SUPERIOR, orient='vertical')
        self.scrollbar_v.pack(side='right', fill='y')
        self.scrollbar_h = tk.Scrollbar(self.contenedor_canvas, bg=COLOR_BARRA_SUPERIOR, orient='horizontal')
        self.scrollbar_h.pack(side='bottom', fill='x')
        self.canvas = tk.Canvas(self.contenedor_canvas, yscrollcommand=self.scrollbar_v.set, xscrollcommand=self.scrollbar_h.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar_v.config(command=self.canvas.yview)
        self.scrollbar_h.config(command=self.canvas.xview)

        self.frame_interior = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame_interior, anchor='nw')
        self.frame_interior.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.ruta_videos = os.path.join(os.path.expanduser('~'), 'Documentos', 'Calidad_Video', 'Videos_Codificados')
        self.videos_seleccionados = []
        self.categoria_seleccionada = None
        self.botones_video = {}

        self.mostrar_ventana_carga()
        
        self.boton_guardar = tk.Button(self.contenedor_principal, text="Guardar Selección", bg=COLOR_VERDE_OSCURO, fg="white", command=self.guardar_seleccion)
        self.boton_guardar.pack(side=tk.BOTTOM, pady=5)

    def mostrar_ventana_carga(self):
        self.ventana_carga = tk.Toplevel(self)
        self.ventana_carga.title("Cargando")
        anchura = 400
        altura = 100
        util_ventana.centrar_ventana(self.ventana_carga, anchura, altura)
        self.label_carga = tk.Label(self.ventana_carga, text="Un momento, se están cargando la lista de videos", font=('Helvetica', 10))
        self.label_carga.pack(expand=True)
        self.ventana_carga.grab_set()  # Hace la ventana modal
        self.ventana_carga.update_idletasks()  # Actualiza la UI

        self.cargar_completado = False
        threading.Thread(target=self.listar_videos).start()
        self.actualizar_etiqueta_carga()

    def actualizar_etiqueta_carga(self):
        if not self.cargar_completado:
            current_text = self.label_carga['text']
            if len(current_text.split('.')) > 5:
                self.label_carga.config(text="Un momento, se están cargando la lista de videos")
            else:
                self.label_carga.config(text=current_text + ".")
            self.ventana_carga.after(500, self.actualizar_etiqueta_carga)
        else:
            self.ventana_carga.destroy()

    def listar_videos(self):
        self.clear_video_display()  # Limpiar los videos mostrados previamente
        videos_por_fila = 5
        fila = 0
        columna = 0
        archivos = sorted(os.listdir(self.ruta_videos))

        for archivo in archivos:
            if archivo.endswith(".mp4"):
                categoria = archivo.split('_')[0]
                if self.categoria_seleccionada is None or self.categoria_seleccionada == categoria:
                    video_path = os.path.join(self.ruta_videos, archivo)
                    portada = self.obtener_portada(video_path)

                    video_frame = tk.Frame(self.frame_interior, borderwidth=1, relief="raised")
                    video_frame.grid(row=fila, column=columna, pady=5, padx=5, sticky="nw")

                    label_imagen = tk.Label(video_frame, image=portada)
                    label_imagen.image = portada
                    label_imagen.pack(side="top", pady=2)

                    label_nombre = tk.Label(video_frame, text=archivo, wraplength=200)
                    label_nombre.pack(side="bottom", pady=2)

                    boton_video = tk.Button(video_frame, text="Seleccionar", bg=COLOR_MENU_LATERAL, fg="white",
                                            command=lambda archivo=archivo: self.seleccionar_video(archivo))
                    boton_video.pack(side="bottom", pady=2)

                    self.botones_video[archivo] = boton_video

                    columna += 1
                    if columna >= videos_por_fila:
                        columna = 0
                        fila += 1
        self.cargar_completado = True

    def clear_video_display(self):
        for widget in self.frame_interior.winfo_children():
            widget.destroy()

    def obtener_portada(self, video_path):
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(frame)
            portada = ImageTk.PhotoImage(image=im)
            return portada
        else:
            raise ValueError("No se pudo obtener el primer frame del video.")

    def seleccionar_video(self, nombre_video):
        categoria_actual = nombre_video.split('_')[0]
        if not self.categoria_seleccionada:
            self.categoria_seleccionada = categoria_actual
            self.videos_seleccionados.append(nombre_video)
            self.canvas.yview_moveto(0)
            self.listar_videos()
            self.botones_video[nombre_video].config(relief="sunken", bg="red", fg="white")
        elif nombre_video in self.videos_seleccionados:
            self.videos_seleccionados.remove(nombre_video)
            self.botones_video[nombre_video].config(relief="raised", bg=COLOR_MENU_LATERAL, fg="white")
            if not self.videos_seleccionados:
                self.categoria_seleccionada = None
                self.listar_videos()
        elif len(self.videos_seleccionados) < 4:
            self.videos_seleccionados.append(nombre_video)
            self.botones_video[nombre_video].config(relief="sunken", bg="white", fg="black")
        else:
            messagebox.showinfo("Selección completa", "Ya has seleccionado 4 videos. Guarda tu selección o deselecciona un video.")

    def guardar_seleccion(self):
        if self.videos_seleccionados:
            random.shuffle(self.videos_seleccionados)
            self.formulario_maestro.videos_seleccionados = [os.path.join(self.ruta_videos, video) for video in self.videos_seleccionados]
            messagebox.showinfo("Éxito", "Videos seleccionados guardados.")
        else:
            messagebox.showinfo("Error", "No se seleccionó ningún video.")
#Paso 4: Reproduccion de video, acción eliminar
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import os
from tkinter import messagebox

from config import COLOR_MENU_LATERAL, COLOR_VERDE_OSCURO, COLOR_ROJO_OSCURO

class VideoPlayer(tk.Frame):
    def __init__(self, master, video_path, categoria, video_seleccionado, cambio_panel_callback=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.video_path = video_path
        self.video_seleccionado = video_seleccionado
        self.cambio_panel_callback = cambio_panel_callback
        self.categoria = categoria
        # Configuración de OpenCV para reproducir video...
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError("Unable to open video file.")

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.delay = int(1000 / self.fps)
        
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.total_duration_ms = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) * (1000 / self.fps))

        self.canvas = tk.Canvas(self, width=self.width, height=self.height)
        self.canvas.pack()

        self.time_label = ttk.Label(self, text="00:00 / " + self.format_time(self.total_duration_ms))
        self.time_label.pack()

        self.show_preview()

        # Frame para los controles que se expandirá para llenar el espacio horizontal (fill='x')
        self.controls_frame = ttk.Frame(self)
        self.controls_frame.pack(fill='x', pady=5)

        # Contenedor para los botones, que luego se centrará usando pack
        self.button_container = ttk.Frame(self.controls_frame)
        self.button_container.pack(expand=True)

        # Botones de control empaquetados con side='left' en el contenedor de botones
        self.play_button = tk.Button(self.button_container, text="Play", bg=COLOR_MENU_LATERAL, fg="white",
                              command=self.play_video)
        self.play_button.pack(side='left', padx=5)

        self.boton_eliminar = tk.Button(self.button_container, text="Eliminar", bd=0, bg=COLOR_ROJO_OSCURO, fg="white",
                                        command=self.accion_eliminar)
        self.boton_eliminar.pack(side='left', padx=5)

        self.boton_regresar = tk.Button(self.button_container, text="Regresar", bd=0, bg=COLOR_VERDE_OSCURO, fg="white",
                                        command=self.accion_regresar)
        self.boton_regresar.pack(side='left', padx=5)

        # Centrar el contenedor de botones en el Frame de controles
        self.button_container.pack(side='top', pady=5)

        self.paused = True

    def accion_regresar(self):
        from formularios.FormularioSeleccionEscalabilidad import FormularioSeleccionEscalabilidad
        self.cap.release()
        if self.cambio_panel_callback:
            self.cambio_panel_callback(FormularioSeleccionEscalabilidad, self.video_seleccionado, self.categoria)
    
    def accion_eliminar(self):
        from formularios.FormularioSeleccionEscalabilidad import FormularioSeleccionEscalabilidad
        self.cap.release()
        if self.cambio_panel_callback:
            os.remove(self.video_path)
            messagebox.showinfo("Información", "Se ha eliminado el video.")
            self.cambio_panel_callback(FormularioSeleccionEscalabilidad, self.video_seleccionado, self.categoria)
    
    def format_time(self, ms):
        seconds = int(ms / 1000)
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes:02}:{seconds:02}"

    def update_time_label(self, end=False):
        if self.cap.isOpened():
            pos_msec = self.cap.get(cv2.CAP_PROP_POS_MSEC) - (1000 / self.fps) if not end else self.total_duration_ms
            elapsed_time = self.format_time(pos_msec)
            self.time_label.config(text=f"{elapsed_time} / {self.format_time(self.total_duration_ms)}")

    def show_preview(self):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = self.cap.read()
        if ret:
            self.display_frame(frame)
            self.update_time_label()
        else:
            raise ValueError("Unable to read video file.")

    def toggle_video_playback(self):
        if self.paused:
            self.paused = False
            self.play_button.config(text="Pause")
            self.update_video()
        else:
            self.paused = True
            self.play_button.config(text="Play")

    def play_video(self):
        self.play_button.config(text="Pause", bg=COLOR_MENU_LATERAL, fg="white", command=self.toggle_video_playback)
        self.toggle_video_playback()

    def update_video(self):
        if self.paused:
            return

        ret, frame = self.cap.read()
        if ret:
            self.display_frame(frame)
            self.update_time_label()
            self.after(self.delay, self.update_video)
        else:
            self.play_button.config(text="Restart", command=self.restart_video)
            self.update_time_label(end=True)

    def display_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo

    def restart_video(self):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.paused = True
        self.play_video()
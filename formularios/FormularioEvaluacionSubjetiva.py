import tkinter as tk
from formularios.Reproduccion_todo import VideoPlayer1
from config import COLOR_BARRA_SUPERIOR, COLOR_MENU_LATERAL, COLOR_VERDE_OSCURO, COLOR_ROJO_OSCURO
from formularios.Puntuacion import StarRating
from tkinter import messagebox

import os  # Se necesita para extraer el nombre del archivo de la ruta del video

class FormularioEvaluacionSubjetiva(tk.Frame):
    def __init__(self, master, formulario_maestro, videos, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.formulario_maestro = formulario_maestro
        self.videos = videos
        print(self.videos)
        self.ratings = {}
        self.paused = True  # Asegúrate de que este es el estado inicial correcto
        self.video_ended = False
        # Crear un contenedor para el Canvas y las Scrollbars
        self.contenedor = tk.Frame(self)
        self.contenedor.pack(fill='both', expand=True)

        # Scrollbar Vertical
        self.scrollbar_v = tk.Scrollbar(self.contenedor, bg=COLOR_BARRA_SUPERIOR, orient='vertical')
        self.scrollbar_v.pack(side='right', fill='y')

        # Scrollbar Horizontal
        self.scrollbar_h = tk.Scrollbar(self.contenedor, bg=COLOR_BARRA_SUPERIOR, orient='horizontal')
        self.scrollbar_h.pack(side='bottom', fill='x')

        # Canvas
        self.canvas = tk.Canvas(self.contenedor, yscrollcommand=self.scrollbar_v.set, xscrollcommand=self.scrollbar_h.set)
        self.canvas.pack(side='left', fill='both', expand=True)

        # Configurar el Canvas con las Scrollbars
        self.scrollbar_v.config(command=self.canvas.yview)
        self.scrollbar_h.config(command=self.canvas.xview)

        # Frame dentro del Canvas para contener los videos
        self.frame_interior = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame_interior, anchor='nw')
        self.frame_interior.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.players = []
        self.crear_videos()

        # Botones de control en un frame común
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(pady=20)

        # Botón para iniciar la reproducción simultánea
        self.btn_control = tk.Button(self.control_frame, text="Reproducir Todos", bg=COLOR_MENU_LATERAL, fg="white", command=self.control_reproduccion)
        self.btn_control.pack(side='left', padx=10)

        # Botón para guardar la evaluación
        self.btn_guardar = tk.Button(self.control_frame, text="Guardar Evaluación", bg=COLOR_VERDE_OSCURO, fg="white", command=self.guardar_evaluacion)
        self.btn_guardar.pack(side='left', padx=10)

    def crear_videos(self):
        videos_por_fila = 2
        fila = columna = 0
        for video_path in self.videos:
            if columna >= videos_por_fila:
                columna = 0
                fila += 1
            video_container = tk.Frame(self.frame_interior)
            video_container.grid(row=fila, column=columna, pady=5, padx=5, sticky="nw")

            player = VideoPlayer1(video_container, video_path, on_video_end=self.on_video_end)
            player.pack()
            
            star_rating = StarRating(video_container, on_rating=lambda rating, vp=video_path: self.set_rating(vp, rating))
            star_rating.pack(pady=5)
            
            self.players.append(player)

            columna += 1

    def on_video_end(self):
        # Esta función es llamada por VideoPlayer1 cuando un video termina
        if all(player.video_ended for player in self.players):
            # Si todos los videos han terminado, actualiza el texto del botón
            self.btn_control.config(text="Reiniciar Todos")
            
    def control_reproduccion(self):
        all_ended = all(player.video_ended for player in self.players)
        if all_ended:
            self.reiniciar_todos()
            self.btn_control.config(text="Pausar Todos")
        elif any(player.paused for player in self.players):
            self.reproducir_todos()
            self.btn_control.config(text="Pausar Todos")
        else:
            self.pausar_todos()
            self.btn_control.config(text="Reproducir Todos")

    def reproducir_todos(self):
        for player in self.players:
            player.play_video()
        self.btn_control.config(text="Pausar Todos")

    def pausar_todos(self):
        for player in self.players:
            player.pause_video()

    def reiniciar_todos(self):
        for player in self.players:
            player.restart_video()

    def set_rating(self, video_path, rating):
        self.ratings[video_path] = rating

    def guardar_evaluacion(self):
        # Aquí puedes guardar las puntuaciones en un archivo o base de datos
        if not hasattr(self.formulario_maestro, 'evaluaciones_subjetivas'):
            self.formulario_maestro.evaluaciones_subjetivas = {}  # Asegúrate de que el formulario maestro tenga este atributo

        for video, rating in self.ratings.items():
            self.formulario_maestro.evaluaciones_subjetivas[video] = rating
            #print(f"Video: {video}, Rating: {rating}")  # Ahora rating es un entero
        
        # Imprimir todas las evaluaciones subjetivas almacenadas en el formulario maestro
        print("Evaluaciones Subjetivas Guardadas:")
        print(self.ratings)
        for video, rating in self.formulario_maestro.evaluaciones_subjetivas.items():
            print(f"Video: {video}, Rating: {rating}")

        messagebox.showinfo("Éxito", "Evaluación Subjetiva guardada, vaya al apartado de gráficas para compararla con la evaluación Objetiva")

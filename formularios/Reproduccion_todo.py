import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2

class VideoPlayer1(tk.Frame):
    min_duration_ms = float('inf')  # Inicializa con infinito para asegurar que cualquier video inicial sea más corto

    def __init__(self, master, video_path, on_video_end=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.on_video_end = on_video_end
        self.video_ended = False

        if not self.cap.isOpened():
            raise ValueError("Unable to open video file.")

        # Calcula la duración de este video
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        total_duration_ms = frame_count * (1000 / fps)

        # Actualiza la duración mínima si este video es más corto
        if total_duration_ms < VideoPlayer1.min_duration_ms:
            VideoPlayer1.min_duration_ms = total_duration_ms

        self.fps = fps
        self.delay = int(1000 / self.fps)
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.canvas = tk.Canvas(self, width=self.width, height=self.height)
        self.canvas.pack()

        self.time_label = ttk.Label(self, text="00:00 / " + self.format_time(VideoPlayer1.min_duration_ms))
        self.time_label.pack()
        self.paused = True
        self.show_preview()

    def format_time(self, ms):
        seconds = int(ms / 1000)
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes:02}:{seconds:02}"

    def update_time_label(self, end=False):
        if self.cap.isOpened():
            current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            current_time_ms = current_frame * self.delay
            if current_time_ms > VideoPlayer1.min_duration_ms:
                current_time_ms = VideoPlayer1.min_duration_ms  # Limita el tiempo transcurrido a la duración mínima
            elapsed_time = self.format_time(current_time_ms)
            self.time_label.config(text=f"{elapsed_time} / {self.format_time(VideoPlayer1.min_duration_ms)}")
            if end:
                self.time_label.config(text=f"{self.format_time(VideoPlayer1.min_duration_ms)} / {self.format_time(VideoPlayer1.min_duration_ms)}")

    def show_preview(self):
        ret, frame = self.read_frame()
        if ret:
            self.display_frame(frame)
            self.update_time_label()

    def play_video(self):
        self.paused = False
        self.update_video()

    def pause_video(self):
        self.paused = True

    def read_frame(self):
        return self.cap.read()

    def display_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo

    def update_video(self):
        if self.paused:
            return

        ret, frame = self.cap.read()
        if ret:
            self.display_frame(frame)
            self.update_time_label()
            self.after(self.delay, self.update_video)
        else:
            self.video_ended = True
            if self.on_video_end:
                self.on_video_end()

    def restart_video(self):
        self.video_ended = False
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.play_video()
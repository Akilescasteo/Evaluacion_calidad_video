import tkinter as tk
import util.util_imagenes as util_img

class StarRating(tk.Frame):
    def __init__(self, master, on_rating=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.on_rating = on_rating
        self.rating = 0  # La puntuación actual

        # Cargar imágenes una sola vez
        self.star_empty = util_img.leer_imagen("imagenes/Estrella_vacia.png", (50, 50))
        self.star_filled = util_img.leer_imagen("imagenes/Estrella_solida.png", (50, 50))

        self.stars = []
        for i in range(5):  # Crear 5 estrellas
            star = tk.Button(self, image=self.star_empty, bd=0, command=lambda i=i: self.set_rating(i+1))
            star.pack(side='left', padx=2)
            self.stars.append(star)
    
    def set_rating(self, rating):
        self.rating = rating
        for i in range(5):
            if i < rating:
                self.stars[i].config(image=self.star_filled)
            else:
                self.stars[i].config(image=self.star_empty)
        if self.on_rating:
            self.on_rating(rating)  # Llamar a la función callback con la nueva puntuación
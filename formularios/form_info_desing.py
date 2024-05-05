import tkinter as tk

import webbrowser

import util.util_ventana as util_ventana
import util.util_imagenes as util_img

class FormularioInfoDesign(tk.Toplevel): #Ventana secundaria 

    def __init__(self) -> None:
        super().__init__()
        self.config_window()
        self.contruirWidget()

    def config_window(self):
        # Configuración inicial de la ventana
        self.title('Notas de la versión')
        icon_image_path = util_img.leer_imagen(("imagenes/logo-univ.png"), (80, 100))
        #icon_image = tk.PhotoImage(file=icon_image_path)
        icon_image = icon_image_path
        self.iconphoto(True, icon_image)

        w, h = 450, 150
        util_ventana.centrar_ventana(self, w, h)     
    
    def contruirWidget(self):         
        self.labelVersion = tk.Label(self, text="Version : 1.0.0")

        w, h = 400, 100
        util_ventana.centrar_ventana(self, w, h)     
    
    def contruirWidget(self):         
        self.labelVersion = tk.Label(self, text="Version : 1.0")

        self.labelVersion.config(fg="#000000", font=(
            "Roboto", 15), pady=10, width=20)
        self.labelVersion.pack()

        self.labelAutor = tk.Label(self, text="Autor : Bladimir Flores")
        self.labelAutor.config(fg="#000000", font=(
            "Roboto", 15), pady=10, width=20)

        self.labelAutor.pack()

        enlace_github = "https://github.com/Akilescasteo/Evaluacion_calidad_video.git"
        self.labelEnlace = tk.Label(self, text=enlace_github, fg="blue", cursor="hand2")
        self.labelEnlace.pack(pady=10)
        self.labelEnlace.bind("<Button-1>", lambda e: webbrowser.open(enlace_github))

        self.labelAutor.pack()

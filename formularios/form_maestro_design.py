#0. Formulario Maestro
import tkinter as tk
from tkinter import font # Fuente de las letras
from config import COLOR_BARRA_SUPERIOR, COLOR_MENU_LATERAL, COLOR_CUERPO_PRINCIPAL, COLOR_MENU_CURSOR_ENCIMA

import util.util_ventana as util_ventana
import util.util_imagenes as util_img
from tkinter import messagebox

from formularios.form_info_desing import FormularioInfoDesign
from formularios.form_sitio_construccion import FormularioSitioConstruccionDesign
from formularios.form_graficas_design import FormularioGraficasDesign
from formularios.form_videos import FormularioVideosDesign
from formularios.FormularioListaVideos import FormularioListaVideos
from formularios.FormularioReproducir import VideoPlayer
from formularios.FormularioEvaluacionSubjetiva import FormularioEvaluacionSubjetiva

class FormularioMaestroDesign(tk.Tk):
    def __init__(self):
        super().__init__()
        self.logo = util_img.leer_imagen(("imagenes/dspace.png"), (560, 136))
        self.perfil = util_img.leer_imagen(("imagenes/logo-univ.png"), (80, 100))
        self.img_sitio_construccion = util_img.leer_imagen(("imagenes/sitio_construccion.png"), (200, 200))
        self.videos_seleccionados = []  # Inicializa la lista de vídeos seleccionados
        self.evaluaciones_subjetivas = {}
        self.panel_graficas = None
        
        self.average_lpips = {'AlexNet': [], 'SqueezeNet': [], 'VGG': []}
        self.confidence_intervals_lpips = {'AlexNet': [], 'SqueezeNet': [], 'VGG': []}
        self.average_psnr = {'AlexNet': [], 'SqueezeNet': [], 'VGG': []}
        self.average_ssim = {'AlexNet': [], 'SqueezeNet': [], 'VGG': []}
        self.confidence_intervals_psnr = {'AlexNet': [], 'SqueezeNet': [], 'VGG': []}
        self.confidence_intervals_ssim = {'AlexNet': [], 'SqueezeNet': [], 'VGG': []}

        self.config_window()
        self.paneles()
        self.controles_barra_superior()
        self.controles_menu_lateral()
        self.controles_cuerpo()

    def config_window(self):
        # Configuración inicial de la ventana
        self.title('Evaluar Calidad de Video')
        icon_image = util_img.leer_imagen(("imagenes/logo-univ.png"), (80, 100))
        self.iconphoto(True, icon_image)
        w, h = 1300, 850
        util_ventana.centrar_ventana(self, w, h)
    
    def paneles(self):        
         # Crear paneles: barra superior, menú lateral y cuerpo principal
        self.barra_superior = tk.Frame(
            self, bg=COLOR_BARRA_SUPERIOR, height=50)
        self.barra_superior.pack(side=tk.TOP, fill='both')      

        self.menu_lateral = tk.Frame(self, bg=COLOR_MENU_LATERAL, width=150)
        self.menu_lateral.pack(side=tk.LEFT, fill='both', expand=False) 
        
        self.cuerpo_principal = tk.Frame(
            self, bg=COLOR_CUERPO_PRINCIPAL)
        self.cuerpo_principal.pack(side=tk.RIGHT, fill='both', expand=True)

    def controles_barra_superior(self):
        # Configuración de la barra superior
        font_awesome = font.Font(family='FontAwesome', size=12)
        # Etiqueta de título
        self.labelTitulo = tk.Label(self.barra_superior, text="Calidad de Video")
        self.labelTitulo.config(fg="#fff", font=(
            "Roboto", 15), bg=COLOR_BARRA_SUPERIOR, pady=10, width=16)
        self.labelTitulo.pack(side=tk.LEFT)

        # Botón del menú lateral
        self.buttonMenuLateral = tk.Button(self.barra_superior, text="\uf0c9", font=font_awesome,
                                           command=self.toggle_panel, bd=0, bg=COLOR_BARRA_SUPERIOR, fg="white")
        self.buttonMenuLateral.pack(side=tk.LEFT)

        # Etiqueta de informacion
        self.labelTitulo = tk.Label(
            self.barra_superior, text="bladimirf22@gmail.com")
        self.labelTitulo.config(fg="#fff", font=(
            "Roboto", 10), bg=COLOR_BARRA_SUPERIOR, padx=10, width=20)
        self.labelTitulo.pack(side=tk.RIGHT)

    def controles_menu_lateral(self):
        # Configuración del menú lateral
        ancho_menu = 20
        alto_menu = 2
        font_awesome = font.Font(family='FontAwesome', size=15)
         
         # Etiqueta de perfil
        self.labelPerfil = tk.Label(
            self.menu_lateral, image=self.perfil, bg=COLOR_MENU_LATERAL)
        self.labelPerfil.pack(side=tk.TOP, pady=10, padx=10)

        # Botones del menú lateral
        
        self.buttonDashBoard = tk.Button(self.menu_lateral)        
        self.buttonProfile = tk.Button(self.menu_lateral)        
        self.buttonPicture = tk.Button(self.menu_lateral)
        self.buttonInfo = tk.Button(self.menu_lateral)        
        self.buttonSettings = tk.Button(self.menu_lateral)

        buttons_info = [
            ("Videos", "\uf008", self.buttonDashBoard, self.abrir_panel_videos),
            ("Videos Codificados", "\uf144", self.buttonPicture, self.abrir_lista_videos),
            ("Gráficas", "\uf080", self.buttonProfile, self.abrir_panel_graficas),
            ("Evaluación Subjetiva", "\uf183", self.buttonSettings, self.abrir_panel_evaluacion_subjetiva),
            ("Info", "\uf129", self.buttonInfo, self.abrir_panel_info)
        ]

        for text, icon, button, comando in buttons_info:
            self.configurar_boton_menu(button, text, icon, font_awesome, ancho_menu, alto_menu, comando)

    def controles_cuerpo(self):
        # Imagen en el cuerpo principal
        label = tk.Label(self.cuerpo_principal, image=self.logo,
                         bg=COLOR_CUERPO_PRINCIPAL)
        label.place(x=0, y=0, relwidth=1, relheight=1)

    def configurar_boton_menu(self, button, text, icon, font_awesome, ancho_menu, alto_menu, comando):
        button.config(text=f"  {icon}    {text}", anchor="w", font=font_awesome,
                      bd=0, bg=COLOR_MENU_LATERAL, fg="white", width=ancho_menu, height=alto_menu,
                      command = comando)
        button.pack(side=tk.TOP)
        self.bind_hover_events(button)

    def bind_hover_events(self, button):
        # Asociar eventos Enter y Leave con la función dinámica
        button.bind("<Enter>", lambda event: self.on_enter(event, button))
        button.bind("<Leave>", lambda event: self.on_leave(event, button))

    def on_enter(self, event, button):
        # Cambiar estilo al pasar el ratón por encima
        button.config(bg=COLOR_MENU_CURSOR_ENCIMA, fg='white')

    def on_leave(self, event, button):
        # Restaurar estilo al salir el ratón
        button.config(bg=COLOR_MENU_LATERAL, fg='white')

    def toggle_panel(self):
        # Alternar visibilidad del menú lateral
        if self.menu_lateral.winfo_ismapped():
            self.menu_lateral.pack_forget()
        else:
            self.menu_lateral.pack(side=tk.LEFT, fill='y')

    def abrir_panel_info(self):
        FormularioInfoDesign()
    
    def abrir_panel_en_construccion(self):
        self.limpiar_panel(self.cuerpo_principal)
        FormularioSitioConstruccionDesign(self.cuerpo_principal, self.img_sitio_construccion)

    def abrir_panel_graficas(self):
        if not self.panel_graficas or not self.panel_graficas.winfo_exists():
            self.crear_panel_graficas()
        else:
            self.limpiar_panel1(self.cuerpo_principal)
            self.panel_graficas.pack(fill='both', expand=True)

    def crear_panel_graficas(self):
        if self.videos_seleccionados:
            print(self.average_lpips)
            print(self.confidence_intervals_lpips)
            print(self.average_psnr)
            print(self.average_ssim)
            print(self.confidence_intervals_psnr)
            print(self.confidence_intervals_ssim)

            self.limpiar_panel1(self.cuerpo_principal)
            self.panel_graficas = FormularioGraficasDesign(self.cuerpo_principal, self, self.average_lpips, self.confidence_intervals_lpips, self.average_psnr, 
                                                           self.average_ssim, self.confidence_intervals_psnr, self.confidence_intervals_ssim, self.videos_seleccionados, 
                                                           self.evaluaciones_subjetivas)
            self.panel_graficas.pack(fill='both', expand=True)
        else:
            messagebox.showinfo("Advertencia", "No se han seleccionado videos.")
    
    def abrir_panel_videos(self):
        self.limpiar_panel(self.cuerpo_principal)
        panel_videos = FormularioVideosDesign(self.cuerpo_principal, self.cambiar_a_panel_especifico)
        panel_videos.pack(fill='both', expand=True)

    def cambiar_a_panel_especifico(self, panel_clase, *args):
        self.limpiar_panel(self.cuerpo_principal)
        if panel_clase == FormularioEvaluacionSubjetiva:
            panel = panel_clase(self.cuerpo_principal, self, args[0])
        else:
            panel = panel_clase(self.cuerpo_principal, *args, self.cambiar_a_panel_especifico)
        panel.pack(fill='both', expand=True)

    def abrir_lista_videos(self):
        self.limpiar_panel(self.cuerpo_principal)
        formulario_lista_videos = FormularioListaVideos(self.cuerpo_principal, self)
        formulario_lista_videos.pack(fill='both', expand=True)

    def mostrar_reproductor_video(self, video_path):
        self.limpiar_panel(self.cuerpo_principal)
        reproductor = VideoPlayer(self.cuerpo_principal, video_path)
        reproductor.pack(fill='both', expand=True)

    def abrir_panel_evaluacion_subjetiva(self):
        self.limpiar_panel(self.cuerpo_principal)
        if self.videos_seleccionados:
            panel_evaluacion_subjetiva = FormularioEvaluacionSubjetiva(self.cuerpo_principal, self, self.videos_seleccionados)
            panel_evaluacion_subjetiva.pack(fill='both', expand=True)
        else:
            messagebox.showinfo("Advertencia", "No se han seleccionado videos.")

    def limpiar_panel(self, panel):
        for widget in panel.winfo_children():
            widget.destroy()
    
    def limpiar_panel1(self, contenedor):
        for widget in contenedor.winfo_children():
            if widget != self.panel_graficas:
                widget.pack_forget()  # o widget.destroy() si realmente necesitas eliminar los otros widgets

    def abrir_panel_videos_con_categoria(self, categoria):
        self.limpiar_panel(self.cuerpo_principal)
        panel_videos = FormularioVideosDesign(self.cuerpo_principal, categoria, self.cambiar_a_panel_especifico)
        panel_videos.pack(fill='both', expand=True)
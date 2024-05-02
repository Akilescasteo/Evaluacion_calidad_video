#Paso 6: Graficas
import tkinter as tk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import cv2
import lpips
import torch
from skimage.metrics import structural_similarity as ssim
import subprocess as sp
import util.util_imagenes as util_img
import os
import util.util_ventana as util_ventana
import threading

from config import COLOR_BARRA_SUPERIOR, COLOR_VERDE_OSCURO, COLOR_ROJO_OSCURO

class FormularioGraficasDesign(tk.Frame):
    # Definir variables de clase que no dependen de instancias específicas
    def __init__(self, master, formulario_maestro, average_lpips, confidence_intervals_lpips, average_psnr, average_ssim, 
                 confidence_intervals_psnr, confidence_intervals_ssim, videos, ranking):
        super().__init__(master)
        self.formulario_maestro = formulario_maestro
        self.ranking = ranking if ranking is not None else {}
        print(f"Ranking: {self.ranking}")
        self.pack(fill='both', expand=True)
        # self.pack(fill='both', expand=True)
        self.distorted_videos = videos
        
        self.average_lpips = average_lpips
        self.confidence_intervals_lpips = confidence_intervals_lpips
        self.average_psnr = average_psnr
        self.average_ssim = average_ssim
        self.confidence_intervals_psnr = confidence_intervals_psnr
        self.confidence_intervals_ssim = confidence_intervals_ssim

        # Extrae el prefijo del nombre del video
        video_name = os.path.basename(self.distorted_videos[0])  # Obtiene el nombre del archivo
        video_prefix = video_name.split('_')[0]  # Divide por '_' y toma la primera parte

        # Diccionario que mapea prefijos de nombres a rutas de videos originales
        video_paths = {
            "akiyo": "/formularios/Videos/Video_Conferencia/akiyo_cif.yuv",
            "deadline": "/formularios/Videos/Video_Conferencia/deadline_cif.yuv",
            "bus": "/formularios/Videos/Video_Vigilancia/bus_cif.yuv",
            "HallMonitor": "/formularios/Videos/Video_Vigilancia/HallMonitor_cif.yuv",
            "football4": "/formularios/Videos/Tiempo_Real/football4_422_cif.yuv",
            "crew": "/formularios/Videos/Tiempo_Real/crew_cif.yuv",
            "soccer": "/formularios/Videos/Entretenimiento/soccer_cif.yuv",
            "football": "/formularios/Videos/Entretenimiento/football_cif.yuv",
            "BigBuckBunny": "/formularios/Videos/Animaciones/BigBuckBunny_cif.yuv",
            "ElephantsDream": "/formularios/Videos/Animaciones/ElephantsDream_cif.yuv"
        }
        
        # Configura la ruta del video original basada en el prefijo extraído
        base_path = util_img.obtener_ruta_base()
        self.original_video_path = base_path + video_paths.get(video_prefix, "/default/path/if/not/found.yuv")

        self.width, self.height = 352, 288
        self.init_figure()
        self.create_widgets()  # Crear y empacar todos los widgets necesarios
        
        self.graficar_metricas_genericas(self.ax1, self.average_psnr, self.confidence_intervals_psnr, 'PSNR por Video', 'PSNR [dB]')
        self.graficar_metricas_genericas(self.ax2, self.average_ssim, self.confidence_intervals_ssim, 'SSIM por Video', 'SSIM [Correlación (0-1)]')
        self.graficar_lpips(self.ax3, self.average_lpips, self.confidence_intervals_lpips)
        self.canvas.draw()
        #self.init_metrics()
        
    def init_figure(self):
        # Solo inicializa la figura una vez, evitando la recreación si ya existe
        if not hasattr(self, 'figura'):
            self.figura = Figure(figsize=(12, 6), dpi=100)
            self.ax1 = self.figura.add_subplot(231) # PSNR
            self.ax2 = self.figura.add_subplot(232) # SSIM
            self.ax3 = self.figura.add_subplot(212) # LPIPS
            self.ax4 = self.figura.add_subplot(233) # Evaluacion Subjetiva

            self.figura.subplots_adjust(hspace=0.4, wspace=0.3)
            
            self.canvas = FigureCanvasTkAgg(self.figura, master=self)
            self.canvas_widget = self.canvas.get_tk_widget()
            self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def create_widgets(self):
        self.frame_botones = tk.Frame(self)
        # Mantener el frame en la parte inferior y expandir solo horizontalmente
        self.frame_botones.pack(side=tk.BOTTOM, fill=tk.X, expand=False, padx=10, pady=10)

        # Contenedor interno para centrar los botones horizontalmente
        inner_frame = tk.Frame(self.frame_botones)
        inner_frame.pack(padx=20)  # Añade un poco de padding alrededor

        self.btn_cargar = tk.Button(inner_frame, text="Cargar y Graficar Métricas", bg=COLOR_BARRA_SUPERIOR, fg="white", command=self.cargar_graficar)
        self.btn_cargar.pack(side=tk.LEFT, padx=10)  # Use padding to space out the buttons

        self.btn_vgg = tk.Button(inner_frame, text="Añadir VGG", bg=COLOR_VERDE_OSCURO, fg="white", command=self.add_vgg)
        self.btn_vgg.pack(side=tk.LEFT, padx=10)  # Use padding to space out the buttons
        
        self.btn_subjetivo = tk.Button(inner_frame, text="Añadir Evaluación Subjetiva", bg=COLOR_ROJO_OSCURO, fg="white", command=self.accion_evaluacion_subjetiva)
        self.btn_subjetivo.pack(side=tk.LEFT, padx=10)  # Use padding to space out the buttons
    
    # def init_metrics(self):
    #     # Inicializar modelos LPIPS y diccionarios para almacenar resultados solo una vez

    def cargar_graficar(self):
        # Procesar videos con AlexNet y SqueezeNet
        if not hasattr(self, 'lpips_alex'):
            self.lpips_alex = lpips.LPIPS(net='alex')
            self.lpips_squeeze = lpips.LPIPS(net='squeeze')
            
            self.average_lpips = {'AlexNet': [], 'SqueezeNet': [], 'VGG': []}
            self.confidence_intervals_lpips = {'AlexNet': [], 'SqueezeNet': [], 'VGG': []}
            self.average_psnr = {'AlexNet': [], 'SqueezeNet': [], 'VGG': []}
            self.average_ssim = {'AlexNet': [], 'SqueezeNet': [], 'VGG': []}
            self.confidence_intervals_psnr = {'AlexNet': [], 'SqueezeNet': [], 'VGG': []}
            self.confidence_intervals_ssim = {'AlexNet': [], 'SqueezeNet': [], 'VGG': []}

        #self.process_videos(self.lpips_alex, 'AlexNet')
        self.mostrar_ventana_carga(self.lpips_alex, 'AlexNet')
        #self.process_videos(self.lpips_squeeze, 'SqueezeNet')
        self.mostrar_ventana_carga(self.lpips_squeeze, 'SqueezeNet')
        self.graficar_metricas_genericas(self.ax1, self.average_psnr, self.confidence_intervals_psnr, 'PSNR por Video', 'PSNR [dB]')
        self.graficar_metricas_genericas(self.ax2, self.average_ssim, self.confidence_intervals_ssim, 'SSIM por Video', 'SSIM [Correlación (0-1)]')
        self.graficar_lpips(self.ax3, self.average_lpips, self.confidence_intervals_lpips)
        self.canvas.draw()

    def add_vgg(self):
        # Opcionalmente añadir VGG y rehacer los gráficos
        response = messagebox.askyesno("Confirmar", "¿Desea añadir la red neuronal VGG?")
        if response:
            print("Añadiendo VGG y recalculando...")
            #self.graficar_lpips(self.ax3, vgg=True)
            lpips_vgg = lpips.LPIPS(net='vgg')
            self.process_videos(lpips_vgg, 'VGG')
            # Rehacer las gráficas incluyendo VGG
            self.graficar_lpips(self.ax3, self.average_lpips, self.confidence_intervals_lpips, remake=True)
            self.canvas.draw()

    def mostrar_ventana_carga(self, lpips, modelo):
        self.ventana_carga = tk.Toplevel(self)
        self.ventana_carga.title("Cargando")
        anchura = 600
        altura = 100
        util_ventana.centrar_ventana(self.ventana_carga, anchura, altura)
        self.label_carga = tk.Label(self.ventana_carga, text=f"Se están generando las gráficas del modelo: {modelo}", font=('Helvetica', 10))
        self.label_carga.pack(expand=True)
        self.ventana_carga.grab_set()  # Hace la ventana modal
        self.ventana_carga.update_idletasks()  # Actualiza la UI

        self.cargar_completado = False
        threading.Thread(target=self.process_videos(lpips, modelo)).start()
        self.actualizar_etiqueta_carga(modelo)

    def actualizar_etiqueta_carga(self, modelo):
        if not self.cargar_completado:
            current_text = self.label_carga['text']
            if len(current_text.split('.')) > 5:
                self.label_carga.config(text=f"Se están generando las gráficas del modelo: {modelo}")
            else:
                self.label_carga.config(text=current_text + ".")
            self.ventana_carga.after(500, self.actualizar_etiqueta_carga)
        else:
            self.ventana_carga.destroy()
    
    # Función para calcular PSNR
    def calculate_psnr(self, img1, img2):
        psnr_value = cv2.PSNR(img1, img2)#Usa OpenCV para calcular el PSNR entre las dos imagenes
        return psnr_value

    # Función para calcular SSIM
    def calculate_ssim(self, img1, img2):
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)#Convierte la primera imagen a escala de grises
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)#Convierte la segunda imagen a escala de grises
        ssim_value, _ = ssim(img1_gray, img2_gray, full=True)#Calcula el SSIM entre las dos imágenes en escala de grises
        return ssim_value

    # Función para calcular LPIPS con un modelo específico
    def calc_lpips(self, tensor_img1, tensor_img2, model):
        with torch.no_grad():
            distance = model.forward(tensor_img1, tensor_img2)
        return distance.item()

    def calcular_intervalo_confianza(self, datos):
        n = len(datos)
        promedio = np.mean(datos)
        desviacion = np.std(datos)
        z_critico = 1.96 # Intervalo de confianza del 95%
        margen_error = z_critico * (desviacion / np.sqrt(n))
        return promedio - margen_error, promedio + margen_error, margen_error

    # Function to read video frames
    def get_video_frames(self, video_path, video_format='yuv', width=352, height=288):
        pipe = None
        process = False
        try:
            if video_format == 'mp4':
                command = [
                    'ffmpeg', '-i', video_path,
                    '-vf', f'scale={width}:{height}',
                    '-pix_fmt', 'yuv420p',
                    '-f', 'rawvideo', 'pipe:1'
                ]
                pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.DEVNULL, bufsize=10**8)
                process = True
            else:
                pipe = open(video_path, "rb")
                process = False

            frame_size = width * height * 3 // 2
            while True:
                yuv_frame = pipe.stdout.read(frame_size) if process else pipe.read(frame_size)
                if not yuv_frame:
                    break
                yuv_frame = np.frombuffer(yuv_frame, np.uint8).reshape((height * 3 // 2, width))
                y_frame = yuv_frame[0:height, :]
                u_frame = cv2.resize(yuv_frame[height:height + height // 4, :], (width, height))
                v_frame = cv2.resize(yuv_frame[height + height // 4:, :], (width, height))
                yuv444_frame = cv2.merge((y_frame, u_frame, v_frame))
                frame = cv2.cvtColor(yuv444_frame, cv2.COLOR_YUV2BGR)
                yield frame
        finally:
            if pipe:
                if process:
                    if hasattr(pipe.stdout, 'close'):
                        pipe.stdout.close()
                    pipe.terminate()
                else:
                    pipe.close()

    def process_videos(self, model, model_name):
        for video_name in self.distorted_videos:
            original_video_frames = self.get_video_frames(self.original_video_path, 'yuv', self.width, self.height)
            distorted_video_frames = self.get_video_frames(video_name, 'mp4' if video_name.endswith('.mp4') else 'yuv', self.width, self.height)
            lpips_values, psnr_values, ssim_values = [], [], []

            for original_frame, distorted_frame in zip(original_video_frames, distorted_video_frames):
                tensor_original = lpips.im2tensor(cv2.cvtColor(original_frame, cv2.COLOR_BGR2RGB))
                tensor_distorted = lpips.im2tensor(cv2.cvtColor(distorted_frame, cv2.COLOR_BGR2RGB))
                lpips_value = self.calc_lpips(tensor_original, tensor_distorted, model)
                psnr_value = self.calculate_psnr(original_frame, distorted_frame)
                ssim_value = self.calculate_ssim(original_frame, distorted_frame)

                lpips_values.append(lpips_value)
                psnr_values.append(psnr_value)
                ssim_values.append(ssim_value)

            avg_lpips = np.mean(lpips_values)
            ci_lpips, _, me_lpips = self.calcular_intervalo_confianza(lpips_values)
            avg_psnr = np.mean(psnr_values)
            ci_psnr, _, me_psnr = self.calcular_intervalo_confianza(psnr_values)
            avg_ssim = np.mean(ssim_values)
            ci_ssim, _, me_ssim = self.calcular_intervalo_confianza(ssim_values)

            self.average_lpips[model_name].append(avg_lpips)
            self.confidence_intervals_lpips[model_name].append(me_lpips)
            self.average_psnr[model_name].append(avg_psnr)
            self.confidence_intervals_psnr[model_name].append(me_psnr)
            self.average_ssim[model_name].append(avg_ssim)
            self.confidence_intervals_ssim[model_name].append(me_ssim)

            self.formulario_maestro.average_lpips = self.average_lpips
            self.formulario_maestro.confidence_intervals_lpips = self.confidence_intervals_lpips
            self.formulario_maestro.average_psnr = self.average_psnr
            self.formulario_maestro.confidence_intervals_psnr = self.confidence_intervals_psnr
            self.formulario_maestro.average_ssim = self.average_ssim
            self.formulario_maestro.confidence_intervals_ssim = self.confidence_intervals_ssim

            print(f'Video: {video_name}')
            print(f'LPIPS promedio: {avg_lpips:.3f}, PSNR promedio: {avg_psnr:.2f}, SSIM promedio: {avg_ssim:.3f}')
            print('---------------------------------------------------')
        self.cargar_completado = True

    # Función para graficar los promedios de LPIPS y los intervalos de confianza para los tres modelos
    # Funciones de graficación ajustadas para permitir actualización
    def get_video_names(self):
        # Extraer solo los nombres de archivo de las rutas completas y eliminar '_cif'
        return [os.path.basename(video).replace('_cif', '').replace('.mp4', '') for video in self.distorted_videos]

    def get_simple_video_names(self):
        # Obtener solo la parte del nombre del video antes del primer guion bajo
        return [name.split('_')[0] for name in self.get_video_names()]
    
    def get_suffix_video_names(self):
        # Obtener solo la parte del nombre del video después del primer guion bajo
        return ['_'.join(name.split('_')[1:]) for name in self.get_video_names()]

    def graficar_lpips(self, ax, average_lpips, confidence_intervals_lpips, remake=False):
        """ Graficar los resultados LPIPS para todos los modelos dados en los diccionarios. """
        width = 0.2
        video_names = self.get_video_names()  # Obtener nombres de los videos
        positions = np.arange(len(video_names))
        ax.clear()

        if remake:
            ax.cla()

        for i, (model_name, averages) in enumerate(average_lpips.items()):
            intervals = confidence_intervals_lpips[model_name]

            if averages and intervals and len(averages) == len(intervals):
                ax.bar(positions+i* width, averages, yerr=intervals, width=width, capsize=5, label=model_name)
            else:
                print(f"Advertencia: Datos faltantes para el modelo {model_name}, no se graficará.")

        ax.set_title('LPIPS por Video y Modelo', fontsize=16)
        ax.set_xlabel('Videos', fontsize=14)
        ax.set_ylabel('LPIPS [Similitud Perceptual (0-1)]', fontsize=12)
        ax.set_xticks(positions + width / 2)
        ax.set_xticklabels(video_names)  # Asignar nombres de archivo como etiquetas
        ax.legend()

    def graficar_metricas_genericas(self, ax, metricas, intervalos, titulo, ylabel):
        positions = np.arange(len(self.distorted_videos))
        ax.clear()
        suffix_video_names = self.get_suffix_video_names()  # Obtener sufijos de nombres de videos
        simple_video_names = self.get_simple_video_names()
        video_prefix = simple_video_names[0] if simple_video_names else ''  # Extraer el primer elemento como prefijo para ylabel

        model_name = 'AlexNet'
        if metricas[model_name] and intervalos[model_name]:
            if len(metricas[model_name]) == len(suffix_video_names) and len(intervalos[model_name]) == len(suffix_video_names):
                color = 'blue' if ylabel == "PSNR" else 'red'
                ax.bar(positions, metricas[model_name], yerr=intervalos[model_name], capsize=5, color=color, align='center')
                ax.set_title(titulo, fontsize=16)
                #ax.set_xlabel('Videos', fontsize=16)
                ax.set_ylabel(f'{ylabel} {video_prefix}', fontsize=12)  # Personalizar ylabel con el nombre del video
                ax.set_xticks(positions)
                ax.set_xticklabels(suffix_video_names, rotation=45)  # Usar sufijos de nombres como etiquetas
            else:
                print("Error: La longitud de los datos de métricas o intervalos no coincide con la cantidad de videos.")
        else:
            print(f"Datos faltantes para el modelo {model_name}, no se graficará.")

    def accion_evaluacion_subjetiva(self):
    # Comprueba si hay valores de evaluación subjetiva disponibles
        if not self.ranking or all(value is None for value in self.ranking.values()):
            messagebox.showinfo("Información", "No se han evaluado subjetivamente los videos.")
        else:
            self.evaluacion_subjetiva(self.ax4)  # Llamar a la función evaluacion_subjetiva con el subplot apropiado
            self.canvas.draw()  # Redibujar el canvas para mostrar los cambios
            print("Evaluación subjetiva añadida al gráfico.")

    def evaluacion_subjetiva(self, ax):
        positions = np.arange(len(self.distorted_videos))
        ylabel = "Evaluación Subjetiva"
        titulo = "Calificación Por Video"
        ax.clear()
        suffix_video_names = self.get_suffix_video_names()  # Obtener sufijos de nombres de videos
        simple_video_names = self.get_simple_video_names()
        video_prefix = simple_video_names[0] if simple_video_names else ''
        ratings = [self.ranking.get(video) for video in self.distorted_videos]  # Extrae valores de ranking para cada video
        ax.bar(positions, ratings, capsize=5, color='green', align='center')
        ax.set_title(titulo, fontsize=18)
        ax.set_ylabel(f'{ylabel} {video_prefix}', fontsize=16)
        ax.set_xticks(positions)
        ax.set_xticklabels(suffix_video_names, rotation=45)

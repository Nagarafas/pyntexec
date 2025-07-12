import customtkinter as ctk
import platform
from tkinter import PhotoImage

class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, msg: str = "", titleText: str = "Alert", version = "1.0.0", width = 300, height = 125, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = msg
        self.title(titleText)
        
        if platform == "Windows":
            self.iconbitmap(r"assets\pyntexec.ico")
            self.font = r"assets\Cascadia Code.ttf"
        else:
            self.iconphoto(False, PhotoImage(file = "assets/pyntexec.png"))
            self.font = "assets/Cascadia Code.ttf"
        
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)

        self.label = ctk.CTkLabel(self, text= self.message, font=("Arial", 16), wraplength=250)
        self.okButton = ctk.CTkButton(self, text="OK", command=self.destroy)
        if titleText == "About":
            from PIL import Image
            self.message = f"Version: {version}\n\nPyntexec is a simple GUI for PyInstaller to build Python scripts into executables.\n\nCreated by Nagarafas_MC"
            self.label.configure(text=self.message)
            my_image = ctk.CTkImage(light_image=Image.open("assets/pyntexec.png"),
                                            dark_image=Image.open("assets/pyntexec.png"),
                                            size=(100, 100))

            image_label = ctk.CTkLabel(self, image=my_image, text="")  # display image with a CTkLabel
            image_label.pack(pady=10)
        self.label.pack(padx=5, pady=10)
        self.okButton.pack(pady=5)
        
            
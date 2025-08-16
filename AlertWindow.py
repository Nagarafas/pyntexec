import customtkinter as ctk
from platform import system
from tkinter import PhotoImage
from os import path
from PIL import Image
OPERATING_SYSTEM = system()

class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, msg: str = "", titleText: str = "Alert", version = "1.0.0", width = 300, height = 125, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = msg
        self.title(titleText)
        
        if OPERATING_SYSTEM == "Windows":
            self.after(201, lambda: self.iconbitmap(path.join(path.dirname(__file__),"assets","pyntexec.ico")))
        else:
            self.iconphoto(False, PhotoImage(file= path.join(path.dirname(__file__),"assets","pyntexec.png")))
            
        self.spec_path = path.join(path.dirname(__file__),"build")
        print(self.spec_path)
        self.font = path.join(path.dirname(__file__),"assets","Cascadia Code.ttf")
        
        # self.geometry(f"{width}x{height}")
        self.resizable(False, False)

        self.label = ctk.CTkLabel(self, text= self.message, font=("Arial", 16), wraplength=width-50)
        self.okButton = ctk.CTkButton(self, text="OK", command=self.destroy)
        if titleText == "About":
            self.message = f"Version: {version}\n\nPyntexec is a simple GUI for PyInstaller to build Python scripts into executables.\n\nCreated by Nagarafas_MC"
            self.label.configure(text=self.message)
            my_image = ctk.CTkImage(light_image=Image.open(path.join(path.dirname(__file__),"assets","pyntexec.png")),
                                            dark_image=Image.open(path.join(path.dirname(__file__),"assets","pyntexec.png")),
                                            size=(100, 100))

            image_label = ctk.CTkLabel(self, image=my_image, text="")  # display image with a CTkLabel
            image_label.pack(pady=10)
        self.label.pack(padx=5, pady=10)
        self.okButton.pack(pady=5)
        
            
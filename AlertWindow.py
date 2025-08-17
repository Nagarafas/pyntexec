import customtkinter as ctk
from platform import system
from tkinter import PhotoImage
from os import path
from PIL import Image

OPERATING_SYSTEM = system()

class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, msg: str = "", titleText: str = "Alert", version = "1.0.0", overide_wraplength = 200, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = msg
        self.title(titleText)
        self.font_size = 18
        
        if OPERATING_SYSTEM == "Windows":
            self.after(201, lambda: self.iconbitmap(path.join(path.dirname(__file__),"assets","pyntexec.ico")))
        else:
            self.iconphoto(False, PhotoImage(file= path.join(path.dirname(__file__),"assets","pyntexec.png")))
            
        self.spec_path = path.join(path.dirname(__file__),"build")
        print(self.spec_path)

        self.resizable(False, False)
        self.frame = ctk.CTkFrame(self)
        self.frame.pack_propagate(True)
        self.frame.pack(padx=10, pady=10)
        
        self.label = ctk.CTkLabel(self.frame, text= self.message, font=("Arial", self.font_size_percent(20)), wraplength=overide_wraplength, justify="center")
        self.okButton = ctk.CTkButton(self.frame, text="OK", command=self.destroy, width=75, font=("Arial", self.font_size_percent(30)), fg_color="#008800", hover_color="#005200", height=20)
        
        if titleText == "About":
            self.message = f"Version: {version}\n\nPyntexec is a simple GUI for PyInstaller & Nuitka to build Python scripts into executables.\n\nCreated by Nagarafas_MC"
            self.label.configure(text=self.message)
            my_image = ctk.CTkImage(light_image=Image.open(path.join(path.dirname(__file__),"assets","pyntexec.png")),
                                            dark_image=Image.open(path.join(path.dirname(__file__),"assets","pyntexec.png")),
                                            size=(100, 100))

            image_label = ctk.CTkLabel(self.frame, image=my_image, text="")  # display image with a CTkLabel
            image_label.pack(pady=10)
            
        self.label.pack(padx=25, pady=5, anchor="center")
        self.okButton.pack(pady=10, anchor="center", side="bottom")
        
        self.focus_set()
        self.grab_set()
        
    def font_size_percent(self, percent: int) -> int:
        return int(self.font_size -  self.font_size*(percent / 100))
        
            
import customtkinter as ctk
from platform import system
from os import path
from tkinter import PhotoImage
OPERATING_SYSTEM = system()

class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, msg: str, command, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = msg
        self.command = command
        self.title("Confirmation")
        
        self.geometry("325x125")
        self.resizable(False, False)
        
        if OPERATING_SYSTEM == "Windows":
            self.after(201, lambda: self.iconbitmap(path.join(path.dirname(__file__),"assets","pyntexec.ico")))
        else:
            self.iconphoto(False, PhotoImage(file= path.join(path.dirname(__file__),"assets","pyntexec.png")))
            
        self.spec_path = path.join(path.dirname(__file__),"build")
        self.font = path.join(path.dirname(__file__),"assets","Cascadia Code.ttf")
        
        self.initUI()
    
    def initUI(self):
        self.label = ctk.CTkLabel(self, text=self.message, font=("Arial", 16), wraplength=200)
        self.label.grid(row=0, column = 0, columnspan = 3, padx=5, pady=10)
        
        self.okButton = ctk.CTkButton(self, text="YES", command=self.exeCommand, fg_color="#008800", hover_color="#005200")
        self.okButton.grid(row = 1, column = 0, pady=5, padx=10, sticky="e")
        
        self.cancelButton = ctk.CTkButton(self, text="NO", command=self.destroy, fg_color="#770011", hover_color="#440011")
        self.cancelButton.grid(row = 1, column = 2, pady=5, padx=10, sticky="w")
    
    def exeCommand(self):
        if self.command:
            self.command()
        self.destroy()
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
        
        self.resizable(False, False)
        
        if OPERATING_SYSTEM == "Windows":
            self.after(201, lambda: self.iconbitmap(path.join(path.dirname(__file__),"assets","pyntexec.ico")))
        else:
            self.iconphoto(False, PhotoImage(file= path.join(path.dirname(__file__),"assets","pyntexec.png")))
            
        self.spec_path = path.join(path.dirname(__file__),"build")
        self.font_size = 18
         
        
        self.initUI()
        self.focus_set()
        self.grab_set()
    
    def font_size_percent(self, percent: int) -> int:
        return int(self.font_size -  self.font_size*(percent / 100))
    
    def initUI(self):
        self.frame = ctk.CTkFrame(self)
        self.frame.pack_propagate(False)  # Prevent the frame from resizing to fit its contents
        self.frame.pack(padx=10, pady=10)
        
        self.label = ctk.CTkLabel(self.frame, text=self.message, font=("Arial", self.font_size_percent(20)), wraplength=200)
        self.label.grid(row=0, column = 0, columnspan = 3, padx=10, pady=5)
        
        self.okButton = ctk.CTkButton(self.frame, text="YES", command=self.exeCommand, fg_color="#008800", hover_color="#005200", font=("Arial", self.font_size_percent(30)), width=75, height=20)
        self.okButton.grid(row = 1, column = 0, pady=5, padx=(10, 0), sticky="e")
        
        self.cancelButton = ctk.CTkButton(self.frame, text="NO", command=self.destroy, fg_color="#770011", hover_color="#440011", font=("Arial", self.font_size_percent(30)), width=75, height=20)
        self.cancelButton.grid(row = 1, column = 2, pady=(5, 10), padx=10, sticky="w")
    
    def exeCommand(self):
        if self.command:
            self.command()
        self.destroy()
from shutil import rmtree
from threading import Thread
from subprocess import Popen, PIPE, check_output
from os import path
from platform import system as operating_system
import customtkinter as ctk
from tkinter import PhotoImage
from PIL import Image
import AlertWindow
import confirmationWindow as confw
from os import getcwd
from sys import version_info, executable
VERSION_INFO = version_info 
OPERATING_SYSTEM= operating_system()

import crossfiledialog
from tkinter import filedialog # fallback for crossfiledialog

# Backends: False = PyInstaller, True = Nuitka 

class Application(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = "2.0.1"
        
        self.grid_x = 20
        self.grid_y = 25
    
        self.frame_grid_x = 20
        self.frame_grid_y = 20
        
        self.main_frame = ctk.CTkFrame(master=self)
                
        self.is_dark = bool(ctk.AppearanceModeTracker.detect_appearance_mode())
        self.is_expanded = False
        
        self.backend = ctk.BooleanVar(value=False)
        self.exclude_bootlocale = ctk.BooleanVar(value=False)
        self.is_onefile = ctk.BooleanVar(value=False)
        self.nuitka_onefile = ctk.StringVar(value="--standalone")
        self.is_terminal_visible = ctk.BooleanVar(value=False)
        self.keep_build = ctk.BooleanVar(value=False)
        self.data: list = []
        self.ico_file = None
        self.file = None
        self.splash_file = None
        self.tkinter_flag = ctk.BooleanVar(value=False)
        self.isolated_flag = ctk.BooleanVar(value=False)
         
        # list of all the nuitka onefile options
        self.onefile_values = ["standalone", "onefile", "onefile-no-compression", "onefile-as-archive", "onefile-no-dll"]
        if OPERATING_SYSTEM == "Linux": self.onefile_values = self.onefile_values[:-1]  # remove "onefile-no-dll" for Linux
        
        self.working_dir_bin = path.dirname(__file__)
        self.working_dir = getcwd()
        self.output_dir = self.working_dir
        # set the default python path to use the already installed python for when app is run as script
        self.selected_python: str = executable
        print(f"Selected Python exec: {executable}")
        self.pythons_dict: dict = {}
        
        if OPERATING_SYSTEM == "Windows":
            self.wm_iconbitmap(path.join(path.dirname(__file__),"assets","pyntexec.ico"))
        else:
            self.iconphoto(False, PhotoImage(file= path.join(path.dirname(__file__),"assets","pyntexec.png")))
            
        self.spec_path = path.join(path.dirname(__file__),"build")
        self.font = ("Noto Sans", 16)
        
        self.window_init()
        self.grid_init()
        self.main()
        
    def grid_init(self) -> None:
        # Initialize the grid layout for the main window
        for x in range(self.grid_x):
            self.grid_columnconfigure(x, weight=1)
        
        for y in range(self.grid_y):
            self.grid_rowconfigure(y, weight=1)
        
        # Initialize the grid layout for the main frame
        for x in range(self.frame_grid_x):
            self.main_frame.grid_rowconfigure(x, weight=1)
            
        for y in range(self.frame_grid_y):
            self.main_frame.grid_columnconfigure(y, weight=1)
    
    def window_init(self) -> None:
        ctk.set_appearance_mode("system")
        
        ctk.set_default_color_theme("dark-blue")
        # self.geometry("1024x425")
        self.geometry("875x325")
        # self.minsize(width=1000, height=425)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
        self.title("Pyntexec")
        
        self.main_frame.grid(row=1, column=0, columnspan=20, rowspan=18, sticky="nsew", padx=(10,10), pady=(3,0))
    
    def pick_output(self) -> None:
        try:
            self.output_dir = crossfiledialog.choose_folder(title="Select Output Directory")
        except:
            self.output_dir = filedialog.askdirectory(title="Select Output Directory", initialdir=self.output_dir)
        
        if not self.output_dir:
            AlertWindow.ToplevelWindow("No output directory selected")
            return
    
    def choose_file(self) -> None:
        try:
            self.file = crossfiledialog.open_file(title="Select a Python File", filter={"Python files (.py .pyw)":["*.py", "*.pyw"]}, start_dir=self.working_dir)
        except:
            self.file = filedialog.askopenfilename(title="Select a Python File", filetypes=[("Python files (.py .pyw)", "*.py *.pyw")], initialdir=self.working_dir)
            
        self.file_entry.delete(first_index=0, last_index='end')
        self.file_entry.insert(0, string=self.file)
        
    def choose_ico_file(self) -> None:
        window_title = "Select a .ico File" if OPERATING_SYSTEM == "Windows" else "Select a .png File"
        try:
            self.ico_file = crossfiledialog.open_file(title=window_title, filter={"icons (.ico .exe)":["*.ico", "*.exe"]} if OPERATING_SYSTEM == "Windows" else {"png files":"*.png"}, start_dir=self.working_dir)
        except:
            self.ico_file = filedialog.askopenfilename(title=window_title, filetypes=[("ico files", "*.ico")] if OPERATING_SYSTEM == "Windows" else [("png files", "*.png")], initialdir=self.working_dir)
        
        self.ico = ctk.CTkImage(light_image=Image.open(self.ico_file),
                                dark_image=Image.open(self.ico_file),
                                size=(115, 115))
        self.ico_button.destroy()
        self.ico_button = ctk.CTkButton(master=self.main_frame, image=self.ico, text="", font=self.font, command=self.choose_ico_file, fg_color=("#ffffff", "#333333"), hover_color=("#ebebeb", "#242424"), text_color=("#121212", "#ebebeb"))
        self.ico_button.grid(row=3, column=10, rowspan=15, columnspan=5, pady=(3,0), padx=(5,0), sticky="nswe")
        
    def choose_splash_file(self) -> None:
        try:
            self.splash_file = crossfiledialog.open_file(title="Select a .png File", filter={"Images (png jpg jpeg)":["*.png", "*.jpg", "*.jpeg"]}, start_dir=self.working_dir)
        except:
            self.splash_file = filedialog.askopenfilename(title="Select a .png File", filetypes=[("Images", "*.png *.jpg *.jpeg")], initialdir=self.working_dir)
        
        self.splash = ctk.CTkImage(light_image=Image.open(self.splash_file),
                                dark_image=Image.open(self.splash_file),
                                size=(115, 115))
        self.splash_button.destroy()
        self.splash_button = ctk.CTkButton(master=self.main_frame, image=self.splash,text="", font=self.font, command=self.choose_splash_file, fg_color=("#ffffff", "#333333"), hover_color=("#ebebeb", "#242424"), text_color=("#121212", "#ebebeb"))
        self.splash_button.grid(row=3, column=15, rowspan=15, columnspan=5, pady=(3,0), padx=(5,10), sticky="nswe")
            
    def change_theme(self) -> None:
        if self.is_dark:
            self.theme_button.configure(text="🌙", font=(self.font[0], 12))
            ctk.set_appearance_mode("light")
            self.is_dark = False
        else:
            self.theme_button.configure(text="🔆", font=(self.font[0], 12))
            ctk.set_appearance_mode("Dark")
            self.is_dark = True
    
    def find_supported_python(self):
        #find all python installations and add them to a combobox
        if OPERATING_SYSTEM == "Windows":
            #windows implementation
            try:
                out = check_output(["py", "-0p"], text=True)
            except Exception:
                AlertWindow.ToplevelWindow("No Python installation found\nplease install python 3.12 or older\n\nyou can download python here:\nhttps://www.python.org/downloads/", overide_wraplength=250)
                return
    
            for line in out.splitlines():
                if not line.strip():
                    continue
                parts = line.split()
                tag = parts[0].removeprefix("-V:")
                python_path = parts[-1]
                if not "*" in tag:
                    self.pythons_dict["python"+tag] = python_path
                else:
                    self.pythons_dict[".venv"] = python_path
            
            self.python_picker_entry.configure(values=self.pythons_dict)
            self.python_picker_entry.set(f"{next(iter(self.pythons_dict))}")
            
            if len(self.pythons_dict) == 1 and "python3.13" in self.pythons_dict:
                AlertWindow.ToplevelWindow("limited functionality\nNuitka does not support python 3.13\nplease install python 3.12.X or older")
                
            elif VERSION_INFO.major <= 3 and VERSION_INFO.minor <=12 and path.isfile(path.join(self.working_dir,"pyntexec.pyw")):
                return
            elif "python3.12" in self.pythons_dict:
                self.python_picker_entry.set("python3.12")
                self.selected_python = self.pythons_dict[self.python_picker_entry.get()]
                print(self.selected_python)
            else:
                self.python_picker_entry.set(iter(self.pythons_dict))
                self.selected_python = self.python_picker_entry.get()
                print(f"Changed selected python to: {self.selected_python}")
                
        else:
            # linux implementation
            python_paths:list = [".*/bin/python", "/usr/bin/python?.*[0-9]", "/usr/local/bin/python?.*[0-9]"]
            out:str = "" # initialize a out variable
            for bin_path in python_paths:
                try: # try every path that could lead to a python binary and add the path at the end of the 'out' variable
                    out += check_output(f"ls -a {path.abspath(bin_path)}", text=True, shell=True) + "\n"    
                except:
                    print(f"no python in location: {path.abspath(bin_path)}")
    
            for line in out.splitlines():
                if not line.strip():
                    continue
                if self.working_dir in line: # check if the binary is inside the apps directory, if so, it is a virtual env and will be tagged accordingly
                    tag = f"venv({line})"
                    env_tag = tag+""
                else:
                    tag = line.split("/")[-1]
                    
                python_path = line
                
                self.pythons_dict[tag] = python_path
                    
            self.python_picker_entry.configure(values=self.pythons_dict)
            
            # prefer env
            try:
                self.python_picker_entry.set(env_tag)
            except:
                self.python_picker_entry.set(f"{next(iter(self.pythons_dict))}")
                
            self.selected_python = self.pythons_dict[self.python_picker_entry.get()]
            
            print(f"Selected Python: {self.selected_python}")
                
                
    def check_installed_modules(self) -> bool:
        out = check_output([self.selected_python,"-m", "pip",  "list"], text = True)
        modules: list = []
        for line in out.splitlines():
            if not line.strip():
                continue
            if not "Package" in line.split()[0] and not "-------------------------" in line.split()[0]:
                modules.append(line.split()[0].lower())
        
        # print("\n".join(modules))
        if not ("pyinstaller" in modules) and not(self.backend.get()):
            confw.ToplevelWindow("PyInstaller not installed\nwould you like to install it now?", command=lambda: Thread(target = self.run_process, args=(f"{self.selected_python} -m pip install pyinstaller", "install_backend"), daemon = True).start())
            return False
        elif not ("nuitka" in modules) and self.backend.get():
            confw.ToplevelWindow("Nuitka not installed\nwould you like to install it now?",  command=lambda: Thread(target = self.run_process, args=(f"{self.selected_python} -m pip install nuitka", "install_backend"), daemon = True).start())
            return False
        
        selected_modules:list = self.modules_entry.get().lower().split(" ")
        to_install:list = list() 
        for module in selected_modules:
            if not (module in modules):
                to_install.append(module)
                
        to_install = " ".join(to_install)
        if len(to_install):
            confw.ToplevelWindow(f"Sellected modules: ({to_install})\nare not installed or don't exist,\ndo you want to try and install them?", command= lambda: Thread(target = self.run_process, args=(f"{self.selected_python} -m pip install {to_install}", "install_backend"), daemon = True).start())
            return False
        
        return True
    
    def set_current_python(self, value = None):
        if not value:
            value = self.python_picker_entry.get()
        if value in self.pythons_dict:
            self.selected_python = self.pythons_dict[value]
        elif path.isfile(value):
            self.selected_python = value
        print(self.selected_python)
      
    def get_command(self) -> list:
        working_dir =  self.output_dir if len(self.output_dir) > 0 else self.working_dir
        if not self.backend.get():
            options = []
            if not(self.exclude_bootlocale):
                options.append('--exclude-module=_bootlocale')
                
            if self.is_onefile.get():
                options.append("--onefile")
            else:
                options.append("--onedir")
                options.append("--contents-directory=.")
            
            if self.ico_file:
                options.append(f'--icon="{self.ico_file}"')
            
            if self.name_entry.get():
                options.append(f'--name="{self.name_entry.get()}"')
                
            if self.is_terminal_visible.get():
                options.append("--console")
            else:
                options.append("--windowed")
            
            if self.splash_file:
                options.append(f'--splash="{self.splash_file}"')
            
            try:
                if self.data:
                    for data in self.data:
                        if path.isfile(data):
                            if path.dirname(data) == path.dirname(self.file_entry.get()):
                                options.append(f'--add-data="{data}:."')
                            elif path.dirname(self.file_entry.get()) in path.dirname(data):
                                split_path = "".join(path.abspath(data).split(path.dirname(self.file_entry.get())))
                                options.append(f'--add-data="{data}:{split_path}"')
                            else:
                                options.append(f'--add-data="{data}:."')
                        else:
                            options.append(f'--add-data="{data}:{path.basename(data)}"')
            except:
                AlertWindow.ToplevelWindow("no python file selected")
                return []
            
            if self.modules_entry.get():
                modules = self.modules_entry.get().split(",") if "," in self.modules_entry.get() else self.modules_entry.get().split(" ")
                for module in modules:
                    options.append(f'--hidden-import="{module.strip()}"')
            
            if len(self.output_dir) > 0:
                options.append(f'--distpath="{working_dir}/dist"')
            
            options.append("--clean")
            
            return [f'{self.selected_python} -m PyInstaller "{self.file_entry.get()}"', f'--specpath="{self.spec_path}"'] + options
            
        else:
            options = [self.nuitka_onefile.get() if not "onefile-" in self.nuitka_onefile.get() else "--onefile "+self.nuitka_onefile.get(), "--deployment"]
            options.append("--assume-yes-for-download")
            
            if self.is_terminal_visible.get():
                options.append("--windows-console-mode=force")
            else:
                options.append("--windows-console-mode=disable")
                
            if self.keep_build.get():
                options.append("--remove-output")
            
            if self.name_entry.get():
                options.append(f'--output-filename="{self.name_entry.get()}"')
                options.append(f'--output-dir="{working_dir}/dist/{path.basename(self.name_entry.get())}"')
                
            elif options[0] == "--standalone":
                options.append(f'--output-dir="{working_dir}/dist"')
            else:
                options.append(f'--output-dir="{working_dir}/dist/{path.basename(self.file_entry.get()).split(".")[0]}"')
                
            if self.ico_file:
                if OPERATING_SYSTEM == "Windows":
                    if self.ico_file.endswith(".ico"):
                        options.append(f'--windows-icon-from-ico="{self.ico_file}"')
                    else:
                        options.append(f'--windows-icon-template-exe="{self.ico_file}"')
                elif OPERATING_SYSTEM == "Linux":
                    options.append(f'--linux-icon="{self.ico_file}"')
            
            if self.splash_file:
                options.append(f'--onefile-windows-splash-screen-image="{self.splash_file}"')
            try:
                if self.data:
                    for data in self.data:
                        if path.isfile(data):
                            if path.dirname(data) == path.dirname(self.file_entry.get()):
                                options.append(f'--include-data-files="{data}=."')
                            elif path.dirname(self.file_entry.get()) in path.dirname(data):
                                split_path = "".join(path.abspath(data).split(path.dirname(self.file_entry.get())))
                                options.append(f'--include-data-files="{data}={split_path}"')
                            else:
                                options.append(f'--include-data-files="{data}=."')
                        else:
                            options.append(f'--include-data-dir="{data}"="{path.basename(data)}"')
            except:
                AlertWindow.ToplevelWindow("no python file selected")
                return []
            
            if self.modules_entry.get():
                modules = self.modules_entry.get().split(",") if "," in self.modules_entry.get() else self.modules_entry.get().split(" ")
                for module in modules:
                    options.append(f'--include-package-data="{module.strip()}"')
            
            if self.tkinter_flag.get():
                options.append("--enable-plugin=tk-inter")
                
            if self.isolated_flag.get():
                options.append("--python-flag=isolated")
                                        
            return [f'{self.selected_python} -m nuitka --main="{self.file_entry.get()}"'] + options
            
    def add_data(self, datatype : str) -> None:
        if datatype == "folder":
            try:
                temp_data = crossfiledialog.choose_folder(title="Select a folder")
            except:
                temp_data = filedialog.askdirectory(title="Select a folder")
            
            if temp_data and (temp_data not in self.data):
                self.data.append(temp_data)

            self.update_text_box(text="\n".join(self.data))
 
        elif datatype == "files":
            try:
                temp_data = crossfiledialog.open_multiple(title="Select files")
            except:
                temp_data = filedialog.askopenfilenames(title="Select files")
                
            for data in temp_data if len(temp_data) > 0 else []:
                if data not in self.data:
                    self.data.append(data)
    
            print (f"Data list: {self.data}")
            self.update_text_box(text="\n".join(self.data))
                
    def run_process(self, command, status_mode = "build") -> None:
        self.build_button.configure(state="disabled")
        
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, text=True)
        if status_mode == "build":
            self.status_label.configure(text="Status: Building...")
            
        elif status_mode == "install_backend":
            self.status_label.configure(text="Status: Installing backend...")
            
        self.progress_bar.start()

        stdout_thread = Thread(target=self.read_output, args=(process.stdout,), daemon=True)
        stderr_thread = Thread(target=self.read_output, args=(process.stderr,), daemon=True)

        stdout_thread.start()
        stderr_thread.start()

        process.wait()
        stdout_thread.join()
        stderr_thread.join()

        if status_mode == "install_backend":
            self.status_label.configure(text="Status: Backend installed successfully")
            self.build_button.configure(state="normal")
            self.progress_bar.stop()
            self.progress_bar.set(1)
            self.after(2000, self.after_build)

        else:
            self.status_label.configure(text="Status: Finished")
            self.build_button.configure(state="normal")
            self.progress_bar.stop()
            self.progress_bar.set(1)
            self.after(2000, self.after_build)
            Popen(f'explorer "{self.output_dir}\\dist"' if OPERATING_SYSTEM == "Windows" else f'xdg-open "{self.output_dir}/dist"', shell=True)
        AlertWindow.ToplevelWindow("Operation Finished")
                
    def build(self) -> None:
        if not self.check_installed_modules():
            return
        self.clear_console()
        self.set_current_python()
        
        if self.file_entry.get():
            the_command = " ".join(self.get_command())
            print(f"Running command: {the_command}")
            Thread(target=self.run_process, args=(the_command,), daemon=True).start()
        else:
            AlertWindow.ToplevelWindow("Please select a Python file to build")
            self.status_label.configure(text="Status: Idle")
            self.build_button.configure(state="normal")
            self.progress_bar.set(1)
            self.progress_bar.stop()
       
    def after_build(self) -> None:
        self.progress_bar.set(1)
        self.status_label.configure(text="Status: Idle")
        self.update()
        
    def read_output(self, stream) -> None:
        for line in iter(stream.readline, ''):
            if line:
                self.after(0, self.update_console, line)
        stream.close()
                
    def update_text_box(self, text: str) -> None:
        self.data_text_box.configure(state="normal")
        self.data_text_box.delete('1.0', 'end')
        self.data_text_box.insert('0.0', text)
        self.data_text_box.configure(state="disabled")   

    def remove_build_conf(self) -> None:
        rm_build = Thread(target=self.remove_build, daemon=True)
        confw.ToplevelWindow("Are you sure you want to delete the \"Build\" directory?", command=rm_build.start)
            
    def remove_build(self) -> None:
        try:
            rmtree(self.spec_path)
        except:
            AlertWindow.ToplevelWindow("Failed to delete \"Build\" directory or the directory doesn't exist")
        else:
            AlertWindow.ToplevelWindow("Successfully deleted \"Build\" directory")
            
    def clear_data(self) -> None:
        self.data = []
        AlertWindow.ToplevelWindow("Data list cleared")
        self.update_text_box("")
    
    def data_empty(self) -> None:
        if self.data:
            confw.ToplevelWindow("Are you sure you want to clear the data list?", command=self.clear_data)
        else:
            AlertWindow.ToplevelWindow("Data list is already empty")
    
    def clear_ico(self) -> None:
        self.ico_file = None
        self.ico_button.grid_forget()
        self.ico_button.configure(text = "🖼️", image = None)
        self.ico_button.grid(row=3, column=10, rowspan=15, columnspan=5, pady=(3,0), padx=(5,0), sticky="nswe")
        self.disable_os_specific_elements(bknd=self.backend.get())
        
    def clear_splash(self) -> None:
        self.splash_file = None
        self.splash_button.grid_forget()
        self.splash_button.configure(text="🔳", image = None)
        self.splash_button.grid(row=3, column=15, rowspan=15, columnspan=5, pady=(3,0), padx=(5,10), sticky="nsew")
        self.disable_os_specific_elements(bknd=self.backend.get())
        
    def update_console(self, text: str) -> None:
        self.console.configure(state="normal")
        self.console.insert('end', text + '\n')
        self.console.configure(state="disabled")
        self.console.see('end')
        
    def clear_console(self) -> None:
        self.console.configure(state="normal")
        self.console.delete('1.0', 'end')
        self.console.configure(state="disabled")
        
    def expand(self) -> None:
        if not self.is_expanded:
            self.expand_button.configure(text="↑")
            self.is_expanded = True
            self.geometry("875x525")
            self.console.grid(row=21, column=0, columnspan=20, rowspan=4, pady=(3,3), padx=(10, 10), sticky="nsew")
        else:
            self.expand_button.configure(text="↓")
            self.is_expanded = False
            self.geometry("875x325")
            self.console.grid_forget()
    
    def disable_os_specific_elements(self, bknd: bool) -> None:
        if OPERATING_SYSTEM == "Linux":
            if not bknd:
                self.ico_button.configure(state="disabled")
                self.splash_button.configure(state="normal")
                self.terminal_check.configure(state="disabled")
            else:
                self.ico_button.configure(state="normal")
                self.splash_button.configure(state="disabled")
                self.terminal_check.configure(state="disabled")
     
    def font_size_percent(self, percent: int) -> None:
        return int(self.font[1] - self.font[1] * (percent / 100))  
                
    def backend_specific_ui_switch(self, bknd: bool) -> None:
        # Switch between PyInstaller and Nuitka specific UI elements
        # PyInstaller specific UI elements
        previous_value = self.nuitka_onefile.get().replace("--", "")
        if not bknd:
            # Uninitialize the nuitka specific UI elements
            try:
                self.one_file_dropdown.destroy()
                self.rm_build_check.grid_forget()
                self.tkinter_check.grid_forget()
                self.isolated_check.grid_forget()
            except:
                print("Nuitka specific UI elements not initialized, skipping destruction")
                try:
                    self.one_file_check.destroy()
                    self.excl_bootl_check.destroy()
                    self.remove_build_button.destroy()
                except:
                    print("nothing to destroy on first initialization")
            
            self.backend.set(bknd)
            
            # Element Gridding
            self.one_file_check.grid(row=1, column=0, columnspan=2, pady=(3,0), padx=(10, 0), sticky="w")
            self.terminal_check.grid(row=1, column=2, columnspan=2, pady=(3,0), padx=(5, 0), sticky="w")
            self.excl_bootl_check.grid(row=1, column=3, columnspan=2, pady=(3,0), padx=(125, 0), sticky="w")
            self.name_entry.grid(row=1, column=6, columnspan=7, pady=(3,0), padx=(5, 0), sticky="ew")
            self.remove_build_button.grid(row=1, column=13, columnspan=2, pady=(3,0), padx=(5,0), sticky="ew")
            
        # nuitka specific UI elements
        else:
            try:
                # Uninitialize the PyInstaller specific UI elements
                self.one_file_check.grid_forget()
                self.excl_bootl_check.grid_forget()
                self.remove_build_button.grid_forget()
            except:
                print("PyInstaller specific UI elements not initialized, skipping destruction")
                
            self.backend.set(bknd)
            
            # Element Gridding
            # self.one_file_dropdown.grid(row=1, column=0, columnspan=1, pady=(3,0), padx=(10, 0), sticky="w")
            self.terminal_check.grid(row=1, column=1, columnspan=2, pady=(3,0), padx=(5, 0), sticky="w")
            self.rm_build_check.grid(row=1, column=3, columnspan=2, pady=(3,0), padx=(5, 0), sticky="w")
            self.tkinter_check.grid(row=1, column=5, columnspan=2, pady=(3,0), padx=(5, 0), sticky="w")
            self.isolated_check.grid(row=1, column=7, columnspan=1, pady=(3,0), padx=(5, 0), sticky="w")
            self.name_entry.grid(row=1, column=7, columnspan=8, pady=(3,0), padx=(95, 0), sticky="ew")
            
            self.one_file_dropdown = ctk.CTkOptionMenu(master=self.main_frame, values=self.onefile_values, font=(self.font[0], self.font_size_percent(20)), width=100, dynamic_resizing=False, command=lambda x: self.nuitka_onefile.set("--"+x))
            self.one_file_dropdown.set(previous_value)
            self.one_file_dropdown.grid(row=1, column=0, columnspan=1, pady=(3,0), padx=(10, 0), sticky="w")
            
        self.disable_os_specific_elements(bknd)
    
    def main(self) -> None:
    # Static UI elements initialization
        self.theme_button = ctk.CTkButton(master=self, width=6, font=(self.font[0], self.font_size_percent(40)), command=self.change_theme)
        if self.is_dark:
            self.theme_button.configure(text="🔆")
        else:
            self.theme_button.configure(text="🌙")
        
        self.title_label = ctk.CTkLabel(master=self, text="PYNTEXEC", font=(self.font[0], self.font_size_percent(10)))
        self.about_button = ctk.CTkButton(master=self, text="About", font=(self.font[0], self.font_size_percent(40)), command=lambda: AlertWindow.ToplevelWindow(titleText="About", version=self.version), width = 50, height=25)
        self.file_entry = ctk.CTkEntry(master=self.main_frame, placeholder_text="Choose a python file", font=self.font)
        self.file_button = ctk.CTkButton(master=self.main_frame, text="🔍", font=self.font, command=self.choose_file, width=25)
        self.terminal_check = ctk.CTkCheckBox(master=self.main_frame, text="Console", width=70, font=self.font, variable=self.is_terminal_visible, onvalue=True, offvalue=False, checkbox_height= 20, checkbox_width= 20, border_width=2)
        self.name_entry = ctk.CTkEntry(master=self.main_frame, placeholder_text="App Name", font=self.font)
        self.pick_output_dir = ctk.CTkButton(master=self.main_frame, text="output dir", font=self.font, command=self.pick_output)
        self.data_text_box_label = ctk.CTkLabel(master=self.main_frame, text="Data List:", font=self.font)
        self.add_folder_button = ctk.CTkButton(master=self.main_frame, text="Folder", font=self.font, command=lambda: self.add_data(datatype="folder"))
        self.add_files_button = ctk.CTkButton(master=self.main_frame, text="Files", font=self.font, command=lambda: self.add_data(datatype="files"))
        self.clear_data_button = ctk.CTkButton(master=self.main_frame, text="Clear", font=self.font, command=self.data_empty, fg_color="#770011", hover_color="#440011")
        self.ico_btn_label = ctk.CTkLabel(master=self.main_frame, text="App Icon:", font=self.font)
        self.splash_btn_label = ctk.CTkLabel(master=self.main_frame, text="!Splash Image!:", font=self.font)
        self.ico_button = ctk.CTkButton(master=self.main_frame, text="🖼️", font=self.font, command=self.choose_ico_file, fg_color=("#ffffff", "#333333"), hover_color=("#ebebeb", "#242424"), text_color=("#121212", "#ebebeb"))
        self.splash_button = ctk.CTkButton(master=self.main_frame, text="🔳", font=self.font, command=self.choose_splash_file, fg_color=("#ffffff", "#333333"), hover_color=("#ebebeb", "#242424"), text_color=("#121212", "#ebebeb"))
        self.ico_clear_button = ctk.CTkButton(master=self.main_frame, text="🗑️", font=self.font, command=self.clear_ico, fg_color="#770011", hover_color="#440011")
        self.splash_clear_button = ctk.CTkButton(master=self.main_frame, text="🗑️", font=self.font, command=self.clear_splash, fg_color="#770011", hover_color="#440011")
        self.data_text_box = ctk.CTkTextbox(master=self.main_frame, font=(self.font[0], self.font_size_percent(20)), width=300, wrap = "word", state = "disabled")
        self.modules_entry = ctk.CTkEntry(master=self.main_frame, placeholder_text="Additional Modules", font=(self.font[0], self.font_size_percent(20)), width=300)
        self.python_picker_entry = ctk.CTkComboBox(master=self.main_frame,font=(self.font[0], self.font_size_percent(20)), command=lambda x:self.set_current_python(x))
        self.build_button = ctk.CTkButton(master=self, text="Start", width=150, font=self.font, command=lambda: Thread(target=self.build, daemon=True).start(), fg_color="#008800", hover_color="#005200")
        self.show_command_button = ctk.CTkButton(master=self, text="?", font=(self.font[0], self.font_size_percent(10)), width=25, command=lambda: AlertWindow.ToplevelWindow(titleText="Command", msg=" ".join(self.get_command()), overide_wraplength=500))
        self.status_label = ctk.CTkLabel(master=self, text="Status: Idle", font=self.font)
        self.backend_radio_PyInstaller = ctk.CTkRadioButton(master=self, text="PyInstaller", variable=self.backend, value=False, command=lambda: self.backend_specific_ui_switch(bknd=False), font=(self.font[0], self.font_size_percent(10)), width=115)
        self.backend_radio_Nuitka = ctk.CTkRadioButton(master=self, text="Nuitka", variable=self.backend, value=True, command=lambda: self.backend_specific_ui_switch(bknd=True), font=(self.font[0], self.font_size_percent(10)))
        self.expand_button = ctk.CTkButton(master=self, text="↓", font=(self.font[0], self.font_size_percent(10)), command=self.expand, width=25)
        self.progress_bar = ctk.CTkProgressBar(master=self, mode="indeterminate", width=512, progress_color="#228822", height=8)
        self.console = ctk.CTkTextbox(master=self, font=(self.font[0], self.font_size_percent(20)), width=300, wrap="word", state="disabled")
        
        # Element gridding
        self.theme_button.grid(row=0, column=0, columnspan=1, pady=(3,0), padx=(10, 0), sticky="w")
        self.title_label.grid(row=0, column=0, columnspan=20)
        self.about_button.grid(row=0, column=19, columnspan=2, pady=(3,0), padx=(5, 10), sticky ="e")
        self.file_entry.grid(row=0, column=0, columnspan=19, pady=(3,0), padx=(10, 0), sticky="nsew")
        self.file_button.grid(row=0, column=19, columnspan=1, pady=(3,0), padx=(5,10), sticky="ew")
        self.pick_output_dir.grid(row=1, column=15, columnspan=5, pady=(3,0), padx=(5, 10), sticky="ew")
        self.data_text_box_label.grid(row=2, column=0, columnspan=2, pady=(3,0), padx=(10, 0), sticky="w")
        self.add_folder_button.grid(row=2, column=2, columnspan=2, pady=(3,0), padx=(5, 0), sticky="ew")
        self.add_files_button.grid(row=2, column=4, columnspan=2, pady=(3,0), padx=(5, 0), sticky="ew")
        self.clear_data_button.grid(row=2, column=6, columnspan=2, pady=(3,0), padx=(5, 0), sticky="ew")
        self.splash_btn_label.grid(row=2, column=15, columnspan=5, pady=(3,0), padx=(5, 10), sticky="nseww")
        self.ico_btn_label.grid(row=2, column=10, columnspan=5, pady=(3,0), padx=(5, 0), sticky="nsew")
        self.ico_button.grid(row=3, column=10, rowspan=15, columnspan=5, pady=(3,0), padx=(5,0), sticky="nswe")
        self.splash_button.grid(row=3, column=15, rowspan=15, columnspan=5, pady=(3,0), padx=(5,10), sticky="nsew")
        self.ico_clear_button.grid(row=18, column=10, rowspan=1, columnspan=5, pady=(3,3), padx=(5,0), sticky="ew")
        self.splash_clear_button.grid(row=18, column=15, rowspan=1, columnspan=5, pady=(3,3), padx=(5,10), sticky="ew")
        self.data_text_box.grid(row=3, column=0, rowspan=15, columnspan=10, pady=(3,0), padx=(10, 0), sticky="nsew")
        self.modules_entry.grid(row=18, column=0, columnspan=7, pady=(3,3), padx=(10, 0), sticky="ew")
        self.python_picker_entry.grid(row=18, column=7, columnspan=3, pady=(3,3), padx=(5, 0), sticky="ew")
        self.build_button.grid(row=19, column=0, columnspan=2, pady=(3,0), padx=(10,0), sticky="we")
        self.status_label.grid(row=19, column=0, columnspan=20, pady=(3,0), padx=(0,0))
        self.show_command_button.grid(row=19, column=2, columnspan=1, pady=(3,0), padx=(5,0), sticky="w")
        self.backend_radio_PyInstaller.grid(row=19, column=16, columnspan=2, pady=(3,0), padx=(5, 0), sticky="e")
        self.backend_radio_Nuitka.grid(row=19, column=18, columnspan=2, pady=(3,0), padx=(5, 10), sticky="e")
        self.expand_button.grid(row=20, column=0, columnspan=1, pady=(3,3), padx=(10, 0), sticky="w")
        self.progress_bar.grid(row=20, column=0, columnspan=20, pady=(3,3), padx=(50, 10), sticky="ew")
    
        # Initialize PyInstaller specific UI elements
        self.one_file_check = ctk.CTkCheckBox(master=self.main_frame, text="--onefile", width=100, font=self.font, variable=self.is_onefile, onvalue=True, offvalue=False, checkbox_height= 20, checkbox_width= 20, border_width=2)
        self.excl_bootl_check = ctk.CTkCheckBox(master=self.main_frame, text="no _bootlocale", width=185, font=self.font, variable=self.exclude_bootlocale, onvalue=True, offvalue=False, checkbox_height= 20, checkbox_width= 20, border_width=2)        
        self.remove_build_button = ctk.CTkButton(master=self.main_frame, text="rm Build dir", font=self.font, command=lambda: Thread(target=self.remove_build_conf, daemon=True).start(), fg_color="#770011", hover_color="#440011")    

        # Initialize nuitka specific UI elements
        
        self.one_file_dropdown = ctk.CTkOptionMenu(master=self.main_frame, values=self.onefile_values, font=(self.font[0], self.font_size_percent(20)), width=100, dynamic_resizing=False, command=lambda x: self.nuitka_onefile.set("--"+x))
        self.one_file_dropdown.set("standalone")
        self.rm_build_check = ctk.CTkCheckBox(master=self.main_frame, text="no build 📂", width=125, font=self.font, variable=self.keep_build, onvalue=True, offvalue=False, checkbox_height= 20, checkbox_width= 20, border_width=2)
        self.tkinter_check = ctk.CTkCheckBox(master=self.main_frame, text="tk-inter", width=70, font=self.font, variable=self.tkinter_flag, onvalue=True, offvalue=False, checkbox_height= 20, checkbox_width= 20, border_width=2)
        self.isolated_check = ctk.CTkCheckBox(master=self.main_frame, text="isolated", width=70, font=self.font, variable=self.isolated_flag, onvalue=True, offvalue=False, checkbox_height= 20, checkbox_width= 20, border_width=2)

        self.backend_specific_ui_switch(self.backend.get())
        
        self.find_supported_python()


if __name__ == "__main__":
    app = Application()
    app.mainloop()
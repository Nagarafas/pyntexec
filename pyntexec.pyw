from shutil import rmtree
from threading import Thread
from subprocess import Popen, PIPE
from os import path
from platform import system as operating_system
import customtkinter as ctk
from tkinter import PhotoImage
from PIL import Image
import AlertWindow
import confirmationWindow as confw
from importlib.util import find_spec
OPERATING_SYSTEM= operating_system()

try:
    import crossfiledialog
except ImportError:
    from tkinter import filedialog

# Backends: False = PyInstaller, True = Nuitka 

class Application(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = "2.0.0-alpha"
        
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
        
        self.working_dir = path.dirname(__file__)
        
        if OPERATING_SYSTEM == "Windows":
            self.wm_iconbitmap(path.join(path.dirname(__file__),"assets","pyntexec.ico"))
        else:
            self.iconphoto(False, PhotoImage(file= path.join(path.dirname(__file__),"assets","pyntexec.png")))
            
        self.spec_path = path.join(path.dirname(__file__),"build")
        self.font = "Noto Sans"
        
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
        self.geometry("1024x425")
        self.minsize(width=1000, height=425)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
        self.title("Pyntexec")
        
        self.main_frame.grid(row=1, column=0, columnspan=20, rowspan=18, sticky="nsew", padx=(10,10), pady=(3,0))
    
    def choose_file(self) -> None:
        try:
            self.file = crossfiledialog.open_file(title="Select a Python File", filter={"Python files (.py .pyw)":["*.py", "*.pyw"]}, start_dir=self.working_dir)
        except:
            self.file = filedialog.askopenfilename(title="Select a Python File", filetypes=[("Python files (.py .pyw)", "*.py *.pyw")], initialdir=self.working_dir)
            
        self.file_entry.delete(first_index=0, last_index=100000)
        self.file_entry.insert(0, string=self.file)
        
    def choose_ico_file(self) -> None:
        window_title = "Select a .ico File" if OPERATING_SYSTEM == "Windows" else "Select a .png File"
        try:
            self.ico_file = crossfiledialog.open_file(title=window_title, filter={"ico files":"*.ico"} if OPERATING_SYSTEM == "Windows" else {"png files":"*.png"}, start_dir=self.working_dir)
        except:
            self.ico_file = filedialog.askopenfilename(title=window_title, filetypes=[("ico files", "*.ico")] if OPERATING_SYSTEM == "Windows" else [("png files", "*.png")], initialdir=self.working_dir)
        
        self.ico = ctk.CTkImage(light_image=Image.open(self.ico_file),
                                dark_image=Image.open(self.ico_file),
                                size=(115, 115))
        self.ico_button.destroy()
        self.ico_button = ctk.CTkButton(master=self.main_frame, image=self.ico, text="", font=(self.font, 20), command=self.choose_ico_file, fg_color="#333333", hover_color="#242424")
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
        self.splash_button = ctk.CTkButton(master=self.main_frame, image=self.splash, text="", font=(self.font, 20), command=self.choose_ico_file, fg_color="#333333", hover_color="#242424")
        self.splash_button.grid(row=3, column=15, rowspan=15, columnspan=5, pady=(3,0), padx=(5,10), sticky="nswe")
            
    def change_theme(self) -> None:
        if self.is_dark:
            self.theme_button.configure(text="🌙", font=(self.font, 12))
            ctk.set_appearance_mode("light")
            self.is_dark = False
        else:
            self.theme_button.configure(text="🔆", font=(self.font, 12))
            ctk.set_appearance_mode("Dark")
            self.is_dark = True
    
    def get_command(self) -> list:
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
                AlertWindow.ToplevelWindow("no python file selected", width=300, height=100)
                return []
            
            if self.modules_entry.get():
                modules = self.modules_entry.get().split(",") if "," in self.modules_entry.get() else self.modules_entry.get().split(" ")
                for module in modules:
                    options.append(f'--hidden-import="{module.strip()}"')
            
            options.append("--clean")
            
            return [f'python -m PyInstaller "{self.file_entry.get()}"', f'--specpath="{self.spec_path}"'] + options
            
        else:
            options = [self.nuitka_onefile.get() if not "onefile-" in self.nuitka_onefile.get() else "--onefile "+self.nuitka_onefile.get(), "--deployment"]
            
            if self.is_terminal_visible.get():
                options.append("--windows-console-mode=force")
            else:
                options.append("--windows-console-mode=disable")
                
            if self.keep_build.get():
                options.append("--remove-output")
            
            if self.name_entry.get():
                options.append(f'--output-filename="{self.name_entry.get()}"')
                options.append(f'--output-dir="{self.working_dir}/dist/{path.basename(self.name_entry.get())}"')
            elif options[0] == "--standalone":
                options.append(f'--output-dir="{self.working_dir}/dist"')
            else:
                options.append(f'--output-dir="{self.working_dir}/dist/{path.basename(self.file_entry.get()).split(".")[0]}"')
                
            if self.ico_file:
                if OPERATING_SYSTEM == "windows":
                    options.append(f'--windows-icon-from-ico="{self.ico_file}"')
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
                AlertWindow.ToplevelWindow("no python file selected", width=300, height=100)
                return []
            
            if self.modules_entry.get():
                modules = self.modules_entry.get().split(",") if "," in self.modules_entry.get() else self.modules_entry.get().split(" ")
                for module in modules:
                    options.append(f'--include-package-data="{module.strip()}"')
                                        
            return [f'python -m nuitka --main="{self.file_entry.get()}"'] + options
            
    def backend_module_check(self) -> bool:
        backend_name = "PyInstaller" if not self.backend.get() else "nuitka"
        if not find_spec(backend_name):
            confw.ToplevelWindow(f"{backend_name} module not found, install it using 'pip install {backend_name.lower()}'?", command=lambda: Thread(target=self.run_process, args=("pip install " + backend_name.lower(), "install_backend"), daemon=True).start())
        else:
            return True
    
    def add_data(self, datatype : str) -> None:
        if datatype == "folder":
            try:
                temp_data = crossfiledialog.choose_folder(title="Select a folder")
            except:
                temp_data = filedialog.askdirectory(title="Select a folder")
            
            if temp_data and (temp_data not in self.data):
                self.data.append(temp_data)

            self.update_text_box(text="".join(self.data))
 
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
            AlertWindow.ToplevelWindow("backend module successfully installed", width=325, height=125)

        else:
            self.status_label.configure(text="Status: Finished")
            self.build_button.configure(state="normal")
            self.progress_bar.stop()
            self.progress_bar.set(1)
            self.after(2000, self.after_build)
            AlertWindow.ToplevelWindow("Build completed successfully", width=325, height=125)
                
    def build(self) -> None:
        if not self.backend_module_check():
            return
        self.clear_console()
        
        if self.file_entry.get():
            the_command = " ".join(self.get_command())
            print(f"Running command: {the_command}")
            Thread(target=self.run_process, args=(the_command,), daemon=True).start()
        else:
            AlertWindow.ToplevelWindow("Please select a Python file to build", width=300, height=100)
            self.status_label.configure(text="Status: Idle")
            self.build_button.configure(state="normal")
            self.progress_bar.set(1)
            self.progress_bar.stop()
    
    def read_output(self, stream) -> None:
        for line in iter(stream.readline, ''):
            if line:
                self.after(0, self.update_console, line)
        stream.close()
       
    def after_build(self) -> None:
        self.progress_bar.set(1)
        self.status_label.configure(text="Status: Idle")
        Popen(f'explorer "{self.working_dir}\\dist"' if OPERATING_SYSTEM == "Windows" else f'xdg-open "{self.working_dir}/dist"', shell=True)
        self.update()
                
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
        self.ico_button.destroy()
        self.ico_button = ctk.CTkButton(master=self.main_frame, text="🖼️", font=(self.font, 20), command=self.choose_ico_file, fg_color="#333333", hover_color="#242424")
        self.ico_button.grid(row=3, column=10, rowspan=15, columnspan=5, pady=(3,0), padx=(5,0), sticky="nswe")
        self.disable_os_specific_elements(bknd=self.backend.get())
        
    def clear_splash(self) -> None:
        self.splash_file = None
        self.splash_button.destroy()
        self.splash_button = ctk.CTkButton(master=self.main_frame, text="🔳", font=(self.font, 20), command=self.choose_splash_file, fg_color="#333333", hover_color="#242424")
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
            self.geometry("1024x625")
            self.console.grid(row=21, column=0, columnspan=20, rowspan=4, pady=(3,3), padx=(10, 10), sticky="nsew")
        else:
            self.expand_button.configure(text="↓")
            self.is_expanded = False
            self.geometry("1024x425")
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
                
    def backend_specific_ui_switch(self, bknd: bool) -> None:
        # Switch between PyInstaller and Nuitka specific UI elements
        # PyInstaller specific UI elements
        if not bknd:
            # Uninitialize the nuitka specific UI elements
            try:
                self.one_file_dropdown.destroy()
                self.rm_build_check.destroy()
            except:
                print("Nuitka specific UI elements not initialized, skipping destruction")
                try:
                    self.one_file_check.destroy()
                    self.excl_bootl_check.destroy()
                    self.remove_build_button.destroy()
                except:
                    print("nothing to destroy on first initialization")
            
            self.backend.set(bknd)
            
            # Initialize PyInstaller specific UI elements
            self.one_file_check = ctk.CTkCheckBox(master=self.main_frame, text="--onefile", width=100, font=(self.font, 20), variable=self.is_onefile, onvalue=True, offvalue=False)
            self.excl_bootl_check = ctk.CTkCheckBox(master=self.main_frame, text="no _bootlocale", width=185, font=(self.font, 20), variable=self.exclude_bootlocale, onvalue=True, offvalue=False)        
            self.remove_build_button = ctk.CTkButton(master=self.main_frame, text="rm Build dir", font=(self.font, 20), command=lambda: Thread(target=self.remove_build_conf, daemon=True).start(), fg_color="#770011", hover_color="#440011")
            
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
                self.one_file_check.destroy()
                self.excl_bootl_check.destroy()
                self.remove_build_button.destroy()
            except:
                print("PyInstaller specific UI elements not initialized, skipping destruction")
                try:
                    self.one_file_dropdown.destroy()
                    self.rm_build_check.destroy()
                except:
                    print("nothing to destroy on first initialization")
                
            self.backend.set(bknd)
            
            # list of all the nuitka onefile options
            values = ["standalone", "onefile", "onefile-no-compression", "onefile-as-archive", "onefile-no-dll"]
            if OPERATING_SYSTEM == "Linux": values = values[:-1]  # remove "onefile-no-dll" for Linux
            
            # Initialize nuitka specific UI elements
            self.one_file_dropdown = ctk.CTkOptionMenu(master=self.main_frame, values=values, font=(self.font, 12), width=100, dynamic_resizing=False, command=lambda x: self.nuitka_onefile.set("--"+x))
            self.one_file_dropdown.set("standalone")
            self.rm_build_check = ctk.CTkCheckBox(master=self.main_frame, text="rm Build dir", width=185, font=(self.font, 20), variable=self.keep_build, onvalue=True, offvalue=False)
            
            # Element Gridding
            self.one_file_dropdown.grid(row=1, column=0, columnspan=2, pady=(3,0), padx=(10, 0), sticky="w")
            self.terminal_check.grid(row=1, column=2, columnspan=2, pady=(3,0), padx=(5, 0), sticky="w")
            self.rm_build_check.grid(row=1, column=3, columnspan=2, pady=(3,0), padx=(115, 0), sticky="w")
            self.name_entry.grid(row=1, column=6, columnspan=9, pady=(3,0), padx=(5, 0), sticky="ew")
            
        self.disable_os_specific_elements(bknd)
    
    def main(self) -> None:
    # Static UI elements initialization
        self.theme_button = ctk.CTkButton(master=self, width=6, font=(self.font, 12), command=self.change_theme)
        if self.is_dark:
            self.theme_button.configure(text="🔆")
        else:
            self.theme_button.configure(text="🌙")
        
        self.title_label = ctk.CTkLabel(master=self, text="PYNTEXEC", font=(self.font, 18))
        self.about_button = ctk.CTkButton(master=self, text="About", font=(self.font, 12), command=lambda: AlertWindow.ToplevelWindow(titleText="About", version=self.version, width=325, height=325), width=75)
        self.file_entry = ctk.CTkEntry(master=self.main_frame, placeholder_text="Choose a python file", font=(self.font, 20))
        self.file_button = ctk.CTkButton(master=self.main_frame, text="🔍", font=(self.font, 20), command=self.choose_file, width=25)
        self.terminal_check = ctk.CTkCheckBox(master=self.main_frame, text="Console", width=70, font=(self.font, 20), variable=self.is_terminal_visible, onvalue=True, offvalue=False)
        self.name_entry = ctk.CTkEntry(master=self.main_frame, placeholder_text="App Name", font=(self.font, 20))
        self.open_dist_dir = ctk.CTkButton(master=self.main_frame, text="App dir", font=(self.font, 20), command=lambda: Popen(f'explorer "{self.working_dir}\\dist"' if OPERATING_SYSTEM == "Windows" else f'xdg-open "{self.working_dir}/dist"', shell=True))
        self.data_text_box_label = ctk.CTkLabel(master=self.main_frame, text="Data List:", font=(self.font, 20))
        self.add_folder_button = ctk.CTkButton(master=self.main_frame, text="Folder", font=(self.font, 20), command=lambda: self.add_data(datatype="folder"))
        self.add_files_button = ctk.CTkButton(master=self.main_frame, text="Files", font=(self.font, 20), command=lambda: self.add_data(datatype="files"))
        self.clear_data_button = ctk.CTkButton(master=self.main_frame, text="Clear", font=(self.font, 20), command=self.data_empty, fg_color="#770011", hover_color="#440011")
        self.ico_btn_label = ctk.CTkLabel(master=self.main_frame, text="App Icon:", font=(self.font, 20))
        self.splash_btn_label = ctk.CTkLabel(master=self.main_frame, text="!Splash Image!:", font=(self.font, 20))
        self.ico_button = ctk.CTkButton(master=self.main_frame, text="🖼️", font=(self.font, 20), command=self.choose_ico_file, fg_color=("#ffffff", "#333333"), hover_color=("#ebebeb", "#242424"), text_color=("#121212", "#ebebeb"))
        self.splash_button = ctk.CTkButton(master=self.main_frame, text="🔳", font=(self.font, 20), command=self.choose_splash_file, fg_color=("#ffffff", "#333333"), hover_color=("#ebebeb", "#242424"), text_color=("#121212", "#ebebeb"))
        self.ico_clear_button = ctk.CTkButton(master=self.main_frame, text="🗑️", font=(self.font, 20), command=self.clear_ico, fg_color="#770011", hover_color="#440011")
        self.splash_clear_button = ctk.CTkButton(master=self.main_frame, text="🗑️", font=(self.font, 20), command=self.clear_splash, fg_color="#770011", hover_color="#440011")
        self.data_text_box = ctk.CTkTextbox(master=self.main_frame, font=(self.font, 12), width=300, wrap = "word", state = "disabled")
        self.modules_entry = ctk.CTkEntry(master=self.main_frame, placeholder_text="Additional Modules", font=(self.font, 16))
        self.build_button = ctk.CTkButton(master=self, text="Build", width=200, font=(self.font, 20), command=lambda: Thread(target=self.build, daemon=True).start(), fg_color="#008800", hover_color="#005200")
        self.show_command_button = ctk.CTkButton(master=self, text="?", font=(self.font, 18), width=25, command=lambda: AlertWindow.ToplevelWindow(titleText="Command", msg=" ".join(self.get_command()), width=600))
        self.status_label = ctk.CTkLabel(master=self, text="Status: Idle", font=(self.font, 20))
        # self.backend_dropdown = ctk.CTkOptionMenu(master=self, values=["PyInstaller", "Nuitka"], font=(self.font, 18), width=175, command= lambda x: self.backend_specific_ui_switch(bknd=True if x == "Nuitka" else False))
        self.backend_radio_PyInstaller = ctk.CTkRadioButton(master=self, text="PyInstaller", variable=self.backend, value=False, command=lambda: self.backend_specific_ui_switch(bknd=False), font=(self.font, 18))
        self.backend_radio_Nuitka = ctk.CTkRadioButton(master=self, text="Nuitka", variable=self.backend, value=True, command=lambda: self.backend_specific_ui_switch(bknd=True), font=(self.font, 18))
        self.expand_button = ctk.CTkButton(master=self, text="↓", font=(self.font, 18), command=self.expand, width=25)
        self.progress_bar = ctk.CTkProgressBar(master=self, mode="indeterminate", width=512, progress_color="#228822", height=8)
        self.console = ctk.CTkTextbox(master=self, font=(self.font, 16), wrap="word", state="disabled")
        
        # Element gridding
        self.theme_button.grid(row=0, column=0, columnspan=1, pady=(3,0), padx=(10, 0), sticky="w")
        self.title_label.grid(row=0, column=0, columnspan=20)
        self.about_button.grid(row=0, column=19, columnspan=2, pady=(3,0), padx=(5, 10), sticky ="e")
        self.file_entry.grid(row=0, column=0, columnspan=19, pady=(3,0), padx=(10, 0), sticky="nsew")
        self.file_button.grid(row=0, column=19, columnspan=1, pady=(3,0), padx=(5,10), sticky="ew")
        self.open_dist_dir.grid(row=1, column=15, columnspan=5, pady=(3,0), padx=(5, 10), sticky="ew")
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
        self.modules_entry.grid(row=18, column=0, columnspan=10, pady=(3,3), padx=(10, 0), sticky="ew")
        self.build_button.grid(row=19, column=0, columnspan=2, pady=(3,0), padx=(10,0), sticky="we")
        self.status_label.grid(row=19, column=0, columnspan=20, pady=(3,0), padx=(0,0))
        self.show_command_button.grid(row=19, column=2, columnspan=1, pady=(3,0), padx=(5,0), sticky="w")
        # self.backend_dropdown.grid(row=19, column=17, columnspan=3, pady=(3,0), padx=(5,10), sticky="w")
        self.backend_radio_PyInstaller.grid(row=19, column=17, columnspan=2, pady=(3,0), padx=(5, 5), sticky="e")
        self.backend_radio_Nuitka.grid(row=19, column=18, columnspan=2, pady=(3,0), padx=(5, 0), sticky="e")
        self.expand_button.grid(row=20, column=0, columnspan=1, pady=(3,3), padx=(10, 0), sticky="w")
        self.progress_bar.grid(row=20, column=0, columnspan=20, pady=(3,3), padx=(50, 10), sticky="ew")
    
        self.backend_specific_ui_switch(self.backend.get())


if __name__ == "__main__":
    app = Application()
    app.mainloop()
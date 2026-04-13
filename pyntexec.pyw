import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, QTimer, pyqtSignal
import qdarktheme

from shutil import rmtree
from threading import Thread
from subprocess import Popen, PIPE, check_output
from os import path
from platform import system as operating_system
import AlertWindow
import confirmationWindow as confw
from os import getcwd
from sys import version_info, executable

VERSION_INFO = version_info 
OPERATING_SYSTEM= operating_system()

import crossfiledialog

# Backends: False = PyInstaller, True = Nuitka 

class Application(QtWidgets.QMainWindow):
    sig_console = pyqtSignal(str)
    sig_status = pyqtSignal(str)
    sig_finish = pyqtSignal(str)
    sig_ui_enable = pyqtSignal(bool)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = "3.0.0 - Qt - Experimental"
        
        self.is_expanded = False
        
        self.backend = False
        self.data: list = []
        self.ico_file = None
        self.file = None
        self.splash_file = None
         
        # list of all the nuitka onefile options
        self.onefile_values = ["standalone", "onefile", "onefile-no-compression", "onefile-as-archive", "onefile-no-dll"]
        if not OPERATING_SYSTEM == "Windows": self.onefile_values = self.onefile_values[:-1]  # remove "onefile-no-dll" for Linux
        
        self.working_dir_bin = path.dirname(__file__)
        self.working_dir = getcwd()
        self.output_dir = self.working_dir
        
        # set the default python path to use the already installed python for when app is run as script
        self.selected_python: str = executable
        print(f"Selected Python exec: {executable}")
        self.pythons_dict: dict = {}
        
        if OPERATING_SYSTEM == "Windows":
            self.window_icon = QIcon(path.join(path.dirname(__file__),"assets","pyntexec.ico"))
        else:
            self.window_icon = QIcon(path.join(path.dirname(__file__),"assets","pyntexec.png"))
            
        self.spec_path = path.join(path.dirname(__file__),"build")
        self.font = ("Noto Sans", 16)
        
        self.window_init()
    
    def window_init(self) -> None:
        uic.loadUi(path.join(self.working_dir_bin,"pyntexec.ui"), self)
        self.setWindowTitle("Pyntexec")
        self.setWindowIcon(self.window_icon)
        self.window_height = self.height()
        
        # signals
        self.sig_console.connect(self.update_console)
        self.sig_status.connect(self.status_label.setText)
        self.sig_finish.connect(self.handle_build_finished)
        self.sig_ui_enable.connect(self.build_button.setEnabled)
        
        self.disable_os_specific_elements(self.backend)
        self.one_file_dropdown.clear()
        self.one_file_dropdown.addItems(self.onefile_values)
        self.one_file_dropdown.setCurrentIndex(0)        
        
        app = QtWidgets.QApplication.instance()
        
        self.actionOpen.triggered.connect(self.choose_file)
        self.actionExit.triggered.connect(lambda: exit())
        
        # 1. SNAPSHOT THE NATIVE STYLE ENGINE NAME (e.g., 'kvantum', 'breeze')
        self.native_style_name = app.style().objectName()
        
        # 2. SNAPSHOT THE NATIVE PALETTE (Colors)
        self.native_palette = app.palette()
                
        self.actionLight.triggered.connect(lambda: self.change_theme("light"))
        self.actionDark.triggered.connect(lambda: self.change_theme("dark"))
        self.actionSystem.triggered.connect(lambda: self.change_theme("system"))
        self.actionBreeze.triggered.connect(lambda: self.change_theme("breeze"))
        
        self.actionAbout.triggered.connect(lambda: AlertWindow.AlertWindow(titleText="About", version=self.version).exec())
        
        self.file_button.pressed.connect(self.choose_file)
        self.pick_output_dir.pressed.connect(self.pick_output)
        
        self.remove_build_button.pressed.connect(self.remove_build_conf)
        self.add_folder_button.pressed.connect(lambda: self.add_data(datatype="folder"))
        self.add_files_button.pressed.connect(lambda: self.add_data(datatype="files"))
        self.clear_data_button.pressed.connect(self.data_empty)
        
        self.ico_button.pressed.connect(self.choose_ico_file)
        self.splash_button.pressed.connect(self.choose_splash_file)
        
        self.ico_clear_button.pressed.connect(self.clear_ico)
    
        self.backend_radio_PyInstaller.clicked.connect(lambda: self.switch_backend(False))
        self.backend_radio_Nuitka.clicked.connect(lambda: self.switch_backend(True))
        self.backend_stacked_widget.setCurrentIndex(0)
        
        self.expand_button.clicked.connect(self.toggle_console)
        self.show_command_button.pressed.connect(self.show_command)
        
        self.python_picker_entry.currentTextChanged.connect(self.set_current_python)
        
        self.build_button.pressed.connect(self.build)
        
        self.find_supported_python()
    
    def choose_file(self) -> None:
        try:
            self.file = crossfiledialog.open_file(title="Select a Python File", filter={"Python files (.py .pyw)":["*.py", "*.pyw"]}, start_dir=self.working_dir)
        except:
            print("fail")
        
        self.file_entry.setText(self.file)
        
    def pick_output(self) -> None:
        try:
            self.output_dir = crossfiledialog.choose_folder(title="Select Output Directory")
        except:
            print("fail")
        
        if not self.output_dir:
            AlertWindow.AlertWindow("No output directory selected")
            return

        self.output_dir_entry.setText(self.output_dir)
        
    def choose_ico_file(self) -> None:
        window_title = "Select a .ico File" if OPERATING_SYSTEM == "Windows" else "Select a .png File"
        try:
            self.ico_file = crossfiledialog.open_file(title=window_title, filter={"icons (.ico .exe)":["*.ico", "*.exe"]} if OPERATING_SYSTEM == "Windows" else {"png files":"*.png"}, start_dir=self.working_dir)
        except:
            print("fail")
        
        self.ico_button.setText("")
        self.ico_button.setIcon(QIcon(self.ico_file))
        self.ico_button.setIconSize(QSize(110, 110))
        
    def choose_splash_file(self) -> None:
        try:
            self.splash_file = crossfiledialog.open_file(title="Select a .png File", filter={"Images (png jpg jpeg)":["*.png", "*.jpg", "*.jpeg"]}, start_dir=self.working_dir)
        except:
            print("fail")
        
        self.splash_button.setText("")
        self.splash_button.setIcon(QIcon(self.splash_file))
        self.splash_button.setIconSize(QSize(110, 110))
            
    def change_theme(self, theme:str) -> None:
        app = QtWidgets.QApplication.instance()
        
        print(f"Theme Changed to {theme}")
        if theme == "light":
            app.setStyleSheet(qdarktheme.load_stylesheet("light"))
            
            self.actionLight.setChecked(True)
            self.actionDark.setChecked(False)
            self.actionSystem.setChecked(False)
            self.actionBreeze.setChecked(False)
            
        elif theme == "dark":
            app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
            
            self.actionLight.setChecked(False)
            self.actionDark.setChecked(True)
            self.actionSystem.setChecked(False)
            self.actionBreeze.setChecked(False)
            
        elif theme == "breeze":
            app.setStyleSheet("")
            app.setStyle(theme)
            
            self.actionLight.setChecked(False)
            self.actionDark.setChecked(False)
            self.actionSystem.setChecked(False)
            self.actionBreeze.setChecked(True)
            
        else:
            app.setStyleSheet("")
            app.setStyle(self.native_style_name)
            app.setPalette(self.native_palette)
            
            self.actionLight.setChecked(False)
            self.actionDark.setChecked(False)
            self.actionSystem.setChecked(True)
            self.actionBreeze.setChecked(False)
            
    def find_supported_python(self):
        #find all python installations and add them to a combobox
        if OPERATING_SYSTEM == "Windows":
            #windows implementation
            try:
                out = check_output(["py", "-0p"], text=True)
            except Exception:
                AlertWindow.AlertWindow("No Python installation found\nplease install python 3.12 or older\n\nyou can download python here:\nhttps://www.python.org/downloads/", overide_wraplength=250).exec()
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
            
            self.python_picker_entry.addItems(self.pythons_dict)
            self.python_picker_entry.setCurrentIndex(0)
            
            if len(self.pythons_dict) == 1 and "python3.13" in self.pythons_dict:
                AlertWindow.AlertWindow("limited functionality\nNuitka does not support python 3.13\nplease install python 3.12.X or older").exec()
                
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
                    
            self.python_picker_entry.addItems(self.pythons_dict)
            
            # prefer env
            try:
                self.python_picker_entry.setCurrentValue(env_tag)
            except:
                self.python_picker_entry.setCurrentText(f"{next(iter(self.pythons_dict))}")
                
            self.selected_python = self.pythons_dict[self.python_picker_entry.currentText()]
            
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
        if not ("pyinstaller" in modules) and not(self.backend):
            if confw.ConfirmationDialog("PyInstaller not installed\nwould you like to install it now?"):
                Thread(target = self.run_process, args=(f"{self.selected_python} -m pip install pyinstaller", "install_backend"), daemon = True).start()
            return False
        elif not ("nuitka" in modules) and self.backend:
            if confw.ConfirmationDialog("Nuitka not installed\nwould you like to install it now?"):
                Thread(target = self.run_process, args=(f"{self.selected_python} -m pip install nuitka", "install_backend"), daemon = True).start()
            return False
        
        selected_modules:list = self.modules_entry.text().lower().split(" ")
        to_install:list = list() 
        for module in selected_modules:
            if not (module in modules):
                to_install.append(module)
                
        to_install = " ".join(to_install)
        if len(to_install):
            if confw.ConfirmationDialog(f"Sellected modules: ({to_install})\nare not installed or don't exist,\ndo you want to try and install them?"):
                Thread(target = self.run_process, args=(f"{self.selected_python} -m pip install {to_install}", "install_backend"), daemon = True).start()
            return False
        
        return True
    
    def set_current_python(self, value = None):
        if not value:
            value = self.python_picker_entry.currentText()
        if value in self.pythons_dict:
            self.selected_python = self.pythons_dict[value]
        elif path.isfile(value):
            self.selected_python = value
        print(self.selected_python)
      
    def show_command(self):
        AlertWindow.AlertWindow("".join(self.get_command())).exec()
      
    def get_command(self) -> list:
        working_dir =  self.output_dir_entry.text() if len(self.output_dir_entry.text()) > 0 else self.working_dir
        if not self.backend:
            options = []
            if self.excl_bootl_check.isChecked():
                options.append('--exclude-module=_bootlocale')
                
            if self.one_file_check.isChecked():
                options.append("--onefile")
            else:
                options.append("--onedir")
                options.append("--contents-directory=.")
            
            if self.ico_file:
                options.append(f'--icon="{self.ico_file}"')
            
            if self.name_entry.text():
                options.append(f'--name="{self.name_entry.text()}"')
                
            if self.terminal_check.isChecked():
                options.append("--console")
            else:
                options.append("--windowed")
            
            if self.splash_file:
                options.append(f'--splash="{self.splash_file}"')
            
            try:
                if self.data:
                    for data in self.data:
                        if path.isfile(data):
                            if path.dirname(data) == path.dirname(self.file_entry.text()):
                                options.append(f'--add-data="{data}:."')
                            elif path.dirname(self.file_entry.text()) in path.dirname(data):
                                split_path = "".join(path.abspath(data).split(path.dirname(self.file_entry.text())))
                                options.append(f'--add-data="{data}:{split_path}"')
                            else:
                                options.append(f'--add-data="{data}:."')
                        else:
                            options.append(f'--add-data="{data}:{path.basename(data)}"')
            except:
                AlertWindow.AlertWindow("no python file selected").exec()
                return []
            
            
            mdl_entry_text = self.modules_entry.text() 
            if mdl_entry_text:
                modules = mdl_entry_text.split(",") if "," in mdl_entry_text else mdl_entry_text.split(" ")
                for module in modules:
                    options.append(f'--hidden-import="{module.strip()}"')
            
            excl_entry_text = self.exclusion_entry.text()
            if excl_entry_text:
                exclusions = excl_entry_text.slpit(",") if "," in excl_entry_text else excl_entry_text.split(" ")
                for exclusion in exclusions:
                    options.append(f'--exclude-module="{exclusion.strip()}"')
            
            if len(self.output_dir_entry.text()) > 0:
                options.append(f'--distpath="{working_dir}/dist"')
            
            options.append("--clean")
            
            return [f'{self.selected_python} -m PyInstaller "{self.file_entry.text()}"', f'--specpath="{self.spec_path}"'] + options
            
        else:
            options = [f"--{self.one_file_dropdown.currentText()}" if not "onefile-" in self.one_file_dropdown.currentText() else f"--onefile --{self.one_file_dropdown.currentText()} --deployment"]
            options.append("--assume-yes-for-download")
            
            if self.terminal_check.isChecked():
                options.append("--windows-console-mode=force")
            else:
                options.append("--windows-console-mode=disable")
                
            if self.rm_build_check.isChecked():
                options.append("--remove-output")
            
            if self.name_entry.text():
                options.append(f'--output-filename="{self.name_entry.text()}"')
                options.append(f'--output-dir="{working_dir}/dist/{path.basename(self.name_entry.text())}"')
                
            elif options[0] == "--standalone":
                options.append(f'--output-dir="{working_dir}/dist"')
            else:
                options.append(f'--output-dir="{working_dir}/dist/{path.basename(self.file_entry.text()).split(".")[0]}"')
                
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
                            if path.dirname(data) == path.dirname(self.file_entry.text()):
                                options.append(f'--include-data-files="{data}=."')
                            elif path.dirname(self.file_entry.text()) in path.dirname(data):
                                split_path = "".join(path.abspath(data).split(path.dirname(self.file_entry.text())))
                                options.append(f'--include-data-files="{data}={split_path}"')
                            else:
                                options.append(f'--include-data-files="{data}=."')
                        else:
                            options.append(f'--include-data-dir="{data}"="{path.basename(data)}"')
            except:
                AlertWindow.AlertWindow("no python file selected").exec()
                return []
            
            mdl_entry_text = self.modules_entry.text()
            if mdl_entry_text:
                modules = mdl_entry_text.split(",") if "," in mdl_entry_text else mdl_entry_text.split(" ")
                for module in modules:
                    options.append(f'--include-package-data="{module.strip()}"')
                    
            excl_entry_text = self.exclusion_entry.text()
            if excl_entry_text:
                exclusions = excl_entry_text.slpit(",") if "," in excl_entry_text else excl_entry_text.split(" ")
                for exclusion in exclusions:
                    options.append(f'--nofollow-import-to="{exclusion.strip()}"')
            
            if self.tkinter_check.isChecked():
                options.append("--enable-plugin=tk-inter")
                
            if self.isolated_check.isChecked():
                options.append("--python-flag=isolated")
                                        
            return [f'{self.selected_python} -m nuitka --main="{self.file_entry.text()}"'] + options
            
    def add_data(self, datatype : str) -> None:
        if datatype == "folder":
            try:
                temp_data = crossfiledialog.choose_folder(title="Select a folder")
            except:
                print("Failed")
            
            if temp_data and (temp_data not in self.data):
                self.data.append(temp_data)

            self.update_text_box(text="\n".join(self.data))
 
        elif datatype == "files":
            try:
                temp_data = crossfiledialog.open_multiple(title="Select files")
            except:
                print("Failed")
                
            for data in temp_data if len(temp_data) > 0 else []:
                if data not in self.data and data != "":
                    self.data.append(data)
    
            print (f"Data list: {self.data}")
            self.update_text_box(text="\n".join(self.data))
                
    def run_process(self, command, status_mode = "build") -> None:
        # self.build_button.setEnabled(False)
        self.sig_ui_enable.emit(False)
        
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, text=True)
        
        if status_mode == "build":
            self.sig_status.emit("Status: Building...")
        elif status_mode == "install_backend":
            self.sig_status.emit("Status: Installing backend...")
            
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.current_line_count = 0

        stdout_thread = Thread(target=self.read_output, args=(process.stdout,), daemon=True)
        stderr_thread = Thread(target=self.read_output, args=(process.stderr,), daemon=True)

        stdout_thread.start()
        stderr_thread.start()

        process.wait()
        stdout_thread.join()
        stderr_thread.join()
        self.sig_finish.emit(status_mode)
    
    def handle_build_finished(self, status_mode: str):
        if status_mode == "install_backend":
            self.status_label.setText("Status: Backend installed successfully")
            self.build_button.setEnabled(True)
            self.progress_bar.setRange(0, 0)
            QTimer.singleShot(2000, self.after_build)

        else:
            self.status_label.setText("Status: Finished")
            self.build_button.setEnabled(True)
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            QTimer.singleShot(2000, self.after_build)
            Popen(f'explorer "{self.output_dir}\\dist"' if OPERATING_SYSTEM == "Windows" else f'xdg-open "{self.output_dir}/dist"', shell=True)
        AlertWindow.AlertWindow("Operation Finished").exec()
                
    def build(self) -> None:
        if not self.check_installed_modules():
            return
        self.clear_console()
        self.set_current_python()
        
        if self.file_entry.text():
            the_command = " ".join(self.get_command())
            print(f"Running command: {the_command}")
            Thread(target=self.run_process, args=(the_command,), daemon=True).start()
        else:
            AlertWindow.AlertWindow("Please select a Python file to build").exec()
            self.status_label.setText("Status: Idle")
            self.build_button.setEnabled(True)
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
       
    def after_build(self) -> None:
        self.progress_bar.setValue(0)
        self.status_label.setText("Status: Idle")
        self.update()
        
    def read_output(self, stream) -> None:
        for line in iter(stream.readline, ''):
            if line:
                self.sig_console.emit(line)
        stream.close()
                
    def update_text_box(self, text: str) -> None:
        self.data_text_box.setPlainText(text) 

    def remove_build_conf(self) -> None:
        # rm_build = Thread(target=self.remove_build, daemon=True)
        if confw.ConfirmationDialog("Are you sure you want to delete the \"Build\" directory?").exec():
            # rm_build.start()
            self.remove_build()
        else:
            print("Operation canceled")
            
    def remove_build(self) -> None:
        try:
            rmtree(self.spec_path)
        except:
            AlertWindow.AlertWindow("Failed to delete \"Build\" directory or the directory doesn't exist").exec()
        else:
            AlertWindow.AlertWindow("Successfully deleted \"Build\" directory").exec()
            
    def clear_data(self) -> None:
        self.data = []
        AlertWindow.AlertWindow("Data list cleared").exec()
        self.update_text_box("")
    
    def data_empty(self) -> None:
        if self.data:
            if confw.ConfirmationDialog("Are you sure you want to clear the data list?").exec():
                self.clear_data()
        else:
            AlertWindow.AlertWindow("Data list is already empty").exec()
    
    def clear_ico(self) -> None:
        self.ico_button.setText("Select Icon")
        self.ico_file = ""
        self.disable_os_specific_elements(bknd=self.backend)
        
    def clear_splash(self) -> None:
        self.splash_file.setText("Select Splash")
        self.splash_file = ""
        self.disable_os_specific_elements(bknd=self.backend)
        
    def update_console(self, text: str) -> None:
        self.console.insertPlainText(text)
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())
        
        if self.current_line_count < 95:
            self.current_line_count += 1
            self.progress_bar.setValue(self.current_line_count)
        
    def clear_console(self) -> None:
        self.console.setPlainText("")
        
    def toggle_console(self):
        if self.is_expanded:
            # --- COLLAPSE ---
            self.console.setVisible(False)
            self.expand_button.setText("▼")
            self.is_expanded = False
            
            # Force the window to the exact collapsed dimensions
            self.resize(self.width(), self.height()-200) 
            
        else:
            # --- EXPAND ---
            self.console.setVisible(True)
            self.expand_button.setText("▲")
            self.is_expanded = True
            
            # Force the window to the exact expanded dimensions
            self.resize(self.width(), self.height()+200)
         
    def disable_os_specific_elements(self, bknd: bool) -> None:
        if OPERATING_SYSTEM == "Linux":
            if not bknd:
                self.ico_button.setEnabled(False)
                self.splash_button.setEnabled(True)
                self.terminal_check.setEnabled(False)
            else:
                self.ico_button.setEnabled(True)
                self.splash_button.setEnabled(False)
                self.terminal_check.setEnabled(False)
                
    def switch_backend(self, bknd: bool) -> None:
        # Switch between PyInstaller and Nuitka specific UI elements
        if not bknd:
            self.backend_stacked_widget.setCurrentIndex(0)
            self.backend = False
        else:
            self.backend_stacked_widget.setCurrentIndex(1)
            self.backend = True

        self.disable_os_specific_elements(self.backend)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    window = Application()
    window.show()
    sys.exit(app.exec())
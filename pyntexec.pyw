from shutil import rmtree
import threading as th
import subprocess as sp
import os
from platform import system as operatingSystem
import customtkinter as ctk
from tkinter import PhotoImage
from PIL import Image

if operatingSystem() == "Windows":
    from tkinter import filedialog
else:
    import crossfiledialog
    
import AlertWindow
import confirmationWindow as confw

class application(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = "1.1.0"
        
        self.gridX = 20
        self.gridY = 25
    
        self.frameGridX = 20
        self.frameGridY = 20
        
        self.mainFrame = ctk.CTkFrame(master = self)
                
        self.isDark = bool(ctk.AppearanceModeTracker.detect_appearance_mode())
        self.isExpanded = False
        
        # self.hasIcon = ctk.BooleanVar(value=False)
        self.excludeBootlocale = ctk.BooleanVar(value=False)
        self.isOnefile = ctk.BooleanVar(value=False)
        self.isTerminalVisible = ctk.BooleanVar(value=False)
        self.keepBuild = ctk.BooleanVar(value= False)
        self.data = []
        self.dataIsFolder = False
        self.icoFile = None
        self.file = None
        self.splashFile = None
        
        self.workingDir = os.getcwd()
        self.platform = operatingSystem()
        
        if self.platform == "Windows":
            self.specPath = self.workingDir + "\\build"
            self.iconbitmap(r"assets\pyntexec.ico")
            self.font = r"assets\Cascadia Code.ttf"
        else:
            self.specPath = self.workingDir + "/build"
            self.iconphoto(False, PhotoImage(file = "assets/pyntexec.png"))
            self.font = "assets/Cascadia Code.ttf"
            
        self.windowInit()
        self.gridInit()
        self.main()
        
    def gridInit(self):
        # Initialize the grid layout for the main window
        for x in range(self.gridX):
            self.grid_rowconfigure(x, weight = 1)
        
        for y in range(self.gridY):
            self.grid_columnconfigure(y, weight = 1)
        
        # Initialize the grid layout for the main frame
        for x in range(self.frameGridX):
            self.mainFrame.grid_rowconfigure(x, weight = 1)
            
        for y in range(self.frameGridY):
            self.mainFrame.grid_columnconfigure(y, weight = 1)
    
    def windowInit(self):
        ctk.set_appearance_mode("system")
        
        ctk.set_default_color_theme("dark-blue")
        self.geometry("1024x425")
        self.minsize(width = 1000, height = 425)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
        self.title("Pyntexec")
        
        self.mainFrame.grid(row = 1, column = 1, columnspan=int(self.gridX-2), rowspan= int(self.gridY-7), sticky = "nsew", padx = (10,10))
    
    def chooseFile(self):
        try:
            self.file = crossfiledialog.open_file(title="Select a Python File", filter={"Python files (.py .pyw)":"*.py *.pyw"}, start_dir = self.workingDir)
        except:
            self.file = filedialog.askopenfilename(title="Select a Python File", filetypes=[("Python files (.py .pyw)", "*.py *.pyw")], initialdir=self.workingDir)
            
        self.fileEntry.delete(first_index= 0, last_index= 100000)
        self.fileEntry.insert(0, string = self.file)
        
    def chooseIcoFile(self):
        try:
            self.icoFile = crossfiledialog.open_file(title="Select a .ico File", filter={"ico files":"*.ico"}, start_dir = self.workingDir)
        except:
            self.icoFile = filedialog.askopenfilename(title="Select a .ico File", filetypes=[("ico files", "*.ico")], initialdir=self.workingDir)
        
        self.ico = ctk.CTkImage(light_image=Image.open(self.icoFile),
                                dark_image=Image.open(self.icoFile),
                                size=(115, 115))
        self.icoButton.destroy()
        self.icoButton = ctk.CTkButton(master = self.mainFrame, image=self.ico, text = "",font=(self.font, 20), command=self.chooseIcoFile, fg_color="#333333", hover_color="#242424")
        self.icoButton.grid(row = 4, column = 10, rowspan= 15, columnspan = 5, pady= (3,0), padx = (5,0), sticky = "nswe")
        
    def chooseSplashFile(self):
        try:
            self.splashFile = crossfiledialog.open_file(title="Select a .png File", filter={"Images":"*.png *.jpg *.jpeg"}, start_dir = self.workingDir)
        except:
            self.splashFile = filedialog.askopenfilename(title="Select a .png File", filetypes=[("Images", "*.png *.jpg *.jpeg")], initialdir=self.workingDir)
        
        self.splash = ctk.CTkImage(light_image=Image.open(self.splashFile),
                                dark_image=Image.open(self.splashFile),
                                size=(115, 115))
        self.splashButton.destroy()
        self.splashButton = ctk.CTkButton(master = self.mainFrame, image=self.splash, text = "",font=(self.font, 20), command=self.chooseIcoFile, fg_color="#333333", hover_color="#242424")
        self.splashButton.grid(row = 4, column = 15, rowspan= 15, columnspan = 5, pady= (3,0), padx = (5,10), sticky = "nswe")
            
    def changeTheme(self):
        if self.isDark:
            self.themeButton.configure(text = "🌙", font = (self.font, 12))
            ctk.set_appearance_mode("light")
            self.isDark = False
        else:
            self.themeButton.configure(text = "🔆", font = (self.font, 12))
            ctk.set_appearance_mode("Dark")
            self.isDark = True
    
    def getCommand(self):
        options = []
        if not(self.excludeBootlocale):
            options.append('--exclude-module=_bootlocale')
            
        if self.isOnefile.get():
            options.append("--onefile")
        else:
            options.append("--onedir")
            options.append("--contents-directory=.")
        
        if self.icoFile:
            options.append(f'--icon="{self.icoFile}"')
        
        if self.nameEntry.get():
            options.append(f'--name="{self.nameEntry.get()}"')
            
        if self.isTerminalVisible.get():
            options.append("--console")
        else:
            options.append("--windowed")
        
        if self.splashFile:
            options.append(f'--splash="{self.splashFile}"')
        
            
        if self.data:
            if self.dataIsFolder:
                options.append(f'--add-data="{self.data}":"./{os.path.basename(self.data)}"')
                # print(f'--add-data="{self.data}":./"{os.path.basename(self.data)}"')
            else:
                options.append(f'--add-data="{",".join(self.data)}:."')
        options.append("--clean")
        
        # buildCommand = f'pyinstaller -y --exclude-module _bootlocale {" ".join(options)} "{self.fileEntry.get()}" --specpath "{self.specPath}"'
        buildCommand = [f'"{self.fileEntry.get()}"', f'--specpath="{self.specPath}"'] + options
        return buildCommand
    
    def addData(self, datatype):
        if datatype == "folder":
            try:
                self.data = crossfiledialog.choose_folder(title = "Select a folder")
            except:
                self.data = filedialog.askdirectory(title = "Select a folder")
                
            self.dataIsFolder = True
            self.updateTextBox(text="".join(self.data))

            
        elif datatype == "file":
            try:
                self.data = crossfiledialog.open_file(title = "Select a file")
            except:
                self.data = filedialog.askopenfilename(title = "Select a file")
                
            self.dataIsFolder = False
            self.updateTextBox(text="".join(self.data))
 
            
        elif datatype == "files":
            try:
                self.data = crossfiledialog.open_multiple(title = "Select files")
            except:
                self.data = filedialog.askopenfilenames(title = "Select files")
            self.dataIsFolder = False
            self.updateTextBox(text="\n".join(self.data))
            
        print(self.data)
                
    def build(self):
        # ConsoleWindow.makeWindow(directory = self.workingDir, command = self.getCommand()).main()
        self.clearConsole()
        def process():
            self.buildButton.configure(state="disabled")
            
            if self.fileEntry.get():
                # pyinstaller.run(self.getCommand())
                command = self.getCommand()
                
                process = sp.Popen("pyinstaller "+" ".join(command), shell=True, stdout=sp.PIPE, stderr=sp.PIPE, text=True)
                self.statusLabel.configure(text = "Status: Building...")
                self.progressBar.start()

                # Create threads for reading stdout and stderr
                stdoutThread = th.Thread(target=self.read_output, args=(process.stdout,), daemon = True)
                stderrThread = th.Thread(target=self.read_output, args=(process.stderr,), daemon =True)

                stdoutThread.start()
                stderrThread.start()

                # Wait for the process to finish
                process.wait()
                stdoutThread.join()
                stderrThread.join()


                self.statusLabel.configure(text="Status: Finished")
                self.buildButton.configure(state="normal")
                self.progressBar.stop()
                self.progressBar.set(1)
                self.after(2000, self.afterBuild)
                
                AlertWindow.ToplevelWindow("Build completed successfully", width=325, height=125)
                
            else:
                AlertWindow.ToplevelWindow("Please select a Python file to build", width=300, height=100)
                self.statusLabel.configure(text="Status: Idle")
                self.buildButton.configure(state="normal")
                self.progressBar.set(1)
                self.progressBar.stop()
            
            
        th.Thread(target= process, daemon=True).start()
    
    def read_output(self, stream):
        # Read output from stdout or stderr stream
        for line in iter(stream.readline, ''):
            if line:
                self.after(0, self.updateConsole, line)
        stream.close()
       
    def afterBuild(self):
        self.progressBar.set(1)
        self.statusLabel.configure(text="Status: Idle")
        sp.Popen(f'explorer "{self.workingDir}\\dist"' if self.platform == "Windows" else f'xdg-open "{self.workingDir}/dist"', shell=True)
        self.update()
                
    def updateTextBox(self, text):
        self.dataTextBox.configure(state="normal")
        self.dataTextBox.delete('1.0', 'end')  # Clear the entire content of the dataTextBox
        self.dataTextBox.insert('0.0', text)
        self.dataTextBox.configure(state="disabled")   

    
    def removeBuildConf(self):
        rmBuild = th.Thread(target = self.removeBuild, daemon = True)
        confw.ToplevelWindow("Are you sure you want to delete the \"Build\" directory?", command = rmBuild.start)
            
    def removeBuild(self):
        try:
            rmtree(self.specPath)
        except:
            AlertWindow.ToplevelWindow("Failed to delete \"Build\" directory or the directory doesn't exist")
        else:
            AlertWindow.ToplevelWindow("Successfully deleted \"Build\" directory")
            
    def clearData(self):
        self.data=[]
        print(self.data)
        AlertWindow.ToplevelWindow("Data list cleared")
        self.updateTextBox("")
    
    def dataEmpty(self):
        if self.data:
            confw.ToplevelWindow("Are you sure you want to clear the data list?", command=self.clearData)
        else:
            AlertWindow.ToplevelWindow("Data list is already empty")
    
    def clearIco(self):
        self.icoFile = None
        self.icoButton.destroy()
        self.icoButton = ctk.CTkButton(master = self.mainFrame, text = "🖼️",font=(self.font, 20), command=self.chooseIcoFile, fg_color="#333333", hover_color="#242424")
        self.icoButton.grid(row = 4, column = 10, rowspan= 15, columnspan = 5, pady= (3,0), padx = (5,0), sticky = "nswe")
        
    def clearSplash(self):
        self.splashFile = None
        self.splashButton.destroy()
        self.splashButton = ctk.CTkButton(master = self.mainFrame, text = "🔳", font=(self.font, 20), command=self.chooseSplashFile, fg_color="#333333", hover_color="#242424")
        self.splashButton.grid(row = 4, column = 15, rowspan= 15, columnspan = 5, pady= (3,0), padx = (5,10), sticky = "nswe")
        
    def updateConsole(self, text):
        self.console.configure(state="normal")
        self.console.insert('end', text + '\n')
        self.console.configure(state="disabled")
        self.console.see('end')
        
    def clearConsole(self):
        self.console.configure(state="normal")
        self.console.delete('1.0', 'end')
        self.console.configure(state="disabled")
        
    def expand(self):
        if not self.isExpanded:
            self.expandButton.configure(text = "↑")
            self.isExpanded = True
            self.geometry("1024x625")
            self.console.grid(row = 21, column = 0, columnspan = 20, rowspan = 4, pady= (3,3), padx = (10, 10), sticky = "nsew")
        else:
            self.expandButton.configure(text = "↓")
            self.isExpanded = False
            self.geometry("1024x425")
            self.console.grid_forget()
    
    def main(self):
        #button and label initialization and grid placement
        
        self.themeButton = ctk.CTkButton(master = self, width=6, font = (self.font, 12), command=self.changeTheme)
        if self.isDark:
            self.themeButton.configure(text = "🔆")
        else: self.themeButton.configure(text = "🌙")
        
        self.themeButton.grid(row = 0, column = 1,  columnspan = 1, pady= (3,0), padx = (10, 0), sticky = "w")
        
        self.titleLabel = ctk.CTkLabel(master = self, text = "PYNTEXEC", font = (self.font, 18))
        self.titleLabel.grid(row = 0, column = 0, columnspan = 20)
        
        self.aboutButton = ctk.CTkButton(master = self, text = "About", font = (self.font, 12), command=lambda:AlertWindow.ToplevelWindow(titleText="About", version = self.version, width=325, height=325), width=75)
        self.aboutButton.grid(row = 0, column = 18, columnspan = 2, pady= (3,0), padx = (5, 10))
        
        self.fileEntry = ctk.CTkEntry(master = self.mainFrame, placeholder_text="Choose a python file", font = (self.font, 20))
        self.fileEntry.grid(row = 0, column = 0, columnspan = 19, pady= (3,0), padx = (10, 0), sticky = "ew")
        
        self.fileButton = ctk.CTkButton(master = self.mainFrame, text = "🔍", font=(self.font, 20), command=self.chooseFile, width=25)
        self.fileButton.grid(row = 0, column = 19, columnspan = 1, pady= (3,0), padx = (5,10), sticky = "ew")
        
        
        self.oneFileCheck = ctk.CTkCheckBox(master = self.mainFrame, text = "--onefile", width = 100, font=(self.font, 20), variable=self.isOnefile, onvalue=True, offvalue=False)
        self.terminalCheck = ctk.CTkCheckBox(master = self.mainFrame, text = "--console", width = 70, font=(self.font, 20), variable=self.isTerminalVisible, onvalue=True, offvalue=False)
        self.exclBootlCheck = ctk.CTkCheckBox(master = self.mainFrame, text = "no _bootlocale", width = 185, font = (self.font, 20), variable = self.excludeBootlocale, onvalue=True, offvalue=False)        
        
        self.oneFileCheck.grid(row = 1, column = 0, columnspan = 2, pady= (3,0), padx = (10, 0), sticky = "w",)
        self.terminalCheck.grid(row = 1, column = 2, columnspan = 2, pady= (3,0), padx = (5, 0), sticky = "w")
        self.exclBootlCheck.grid(row = 1, column = 3, columnspan = 2, pady= (3,0), padx = (125, 0), sticky = "w")
        
        self.nameEntry = ctk.CTkEntry(master = self.mainFrame, placeholder_text="App Name", font = (self.font, 20))
        self.nameEntry.grid(row = 1, column = 5, columnspan = 5, pady= (3,0), padx = (5, 0), sticky = "ew")
        
        self.openDistDir = ctk.CTkButton(master = self.mainFrame, text="App dir", font=(self.font, 20), command=lambda:sp.Popen(f'explorer "{self.workingDir}\\dist"' if self.platform == "Windows" else f'xdg-open "{self.workingDir}/dist"', shell=True))
        self.openDistDir.grid(row = 1, column = 13, columnspan = 7, pady= (3,0), padx = (5, 10), sticky = "ew" )
        
        self.removeBuildButton = ctk.CTkButton(master = self.mainFrame, text="rm Build dir", font=(self.font, 20), command = lambda :th.Thread(target = self.removeBuildConf, daemon = True).start(), fg_color="#770011", hover_color="#440011")
        self.removeBuildButton.grid(row = 1, column = 11, columnspan = 2, pady= (3,0), padx = (5,0), sticky = "ew" )
        
        self.dataLabel = ctk.CTkLabel(master = self.mainFrame, text="Add Data:", font=(self.font, 20))
        self.dataLabel.grid(row = 2, column = 0, columnspan = 2, pady= (3,0), padx = (10, 0), sticky = "w")
        
        self.addFolderButton = ctk.CTkButton(master = self.mainFrame, text="Folder", font=(self.font, 20), command=lambda: self.addData(datatype="folder"))
        self.addFolderButton.grid(row = 2, column = 2, columnspan = 2, pady= (3,0), padx = (5, 0), sticky = "ew")
        
        self.addFileButton = ctk.CTkButton(master = self.mainFrame, text="File", font=(self.font, 20), command=lambda: self.addData(datatype="file"))
        self.addFileButton.grid(row = 2, column = 4, columnspan = 2, pady= (3,0), padx = (5, 0), sticky = "ew")
        
        self.addFilesButton = ctk.CTkButton(master = self.mainFrame, text="Files", font=(self.font, 20), command=lambda: self.addData(datatype="files"))
        self.addFilesButton.grid(row = 2, column = 6, columnspan = 2, pady= (3,0), padx = (5, 0), sticky = "ew")
        
        self.clearDataButton = ctk.CTkButton(master = self.mainFrame, text="Clear", font=(self.font, 20), command=self.dataEmpty, fg_color="#770011", hover_color="#440011")
        self.clearDataButton.grid(row = 2, column = 8, columnspan = 2, pady= (3,0), padx = (5, 0), sticky = "ew")

        self.dataTextBoxLabel = ctk.CTkLabel(master = self.mainFrame, text="Data List:", font=(self.font, 20))
        self.dataTextBoxLabel.grid(row = 3, column = 0, columnspan = 2, pady= (3,0), padx = (10, 0), sticky = "w")

        self.icoBtnLabel = ctk.CTkLabel(master = self.mainFrame, text="App Icon:", font=(self.font, 20))
        self.icoBtnLabel.grid(row = 3, column = 10, columnspan = 5, pady= (3,0), padx = (5, 0), sticky = "nsew")
        
        self.splashBtnLabel = ctk.CTkLabel(master = self.mainFrame, text="!Splash Image!:", font=(self.font, 20))
        self.splashBtnLabel.grid(row = 3, column = 15, columnspan = 5, pady= (3,0), padx = (5, 10), sticky = "nseww")

        self.icoButton = ctk.CTkButton(master = self.mainFrame, text = "🖼️",font=(self.font, 20), command=self.chooseIcoFile, fg_color=("#ffffff", "#333333"), hover_color=("#ebebeb", "#242424"), text_color=("#121212", "#ebebeb"))
        self.icoButton.grid(row = 4, column = 10, rowspan= 15, columnspan = 5, pady= (3,0), padx = (5,0), sticky = "nswe")
        
        self.splashButton = ctk.CTkButton(master = self.mainFrame, text = "🔳", font=(self.font, 20), command=self.chooseSplashFile, fg_color=("#ffffff", "#333333"), hover_color=("#ebebeb", "#242424"), text_color=("#121212", "#ebebeb"))
        self.splashButton.grid(row = 4, column = 15, rowspan= 15, columnspan = 5, pady= (3,0), padx = (5,10), sticky = "nsew")
        
        self.icoClearButton = ctk.CTkButton(master = self.mainFrame, text = "🗑️", font=(self.font, 20), command=self.clearIco, fg_color="#770011", hover_color="#440011")
        self.icoClearButton.grid(row = 19, column = 10, rowspan= 1, columnspan = 5, pady= (3,3), padx = (5,0), sticky = "we")
        
        self.splashClearButton = ctk.CTkButton(master = self.mainFrame, text = "🗑️", font=(self.font, 20), command=self.clearSplash, fg_color="#770011", hover_color="#440011")
        self.splashClearButton.grid(row = 19, column = 15, rowspan= 15, columnspan = 5, pady= (3,3), padx = (5,10), sticky = "we")

        self.dataTextBox = ctk.CTkTextbox(master = self.mainFrame, font=(self.font, 12), width = 300)
        self.dataTextBox.grid(row = 4, column = 0, rowspan = 16, columnspan = 10, pady= (3,3), padx = (10, 0), sticky = "nsew")
        self.dataTextBox.configure(state="disabled")  # Initially disable the textbox
        
        
        self.buildButton = ctk.CTkButton(master = self, text = "Build", width = 200, font=(self.font, 20), command=lambda:th.Thread(target = self.build, daemon = True).start(), fg_color="#008800", hover_color="#005200")
        self.buildButton.grid(row = 19, column = 0, columnspan = 3, pady= (3,0), padx = (10,0))
        
        self.showCommandButton = ctk.CTkButton(master = self, text = "?", font=(self.font, 18), width=25, command=lambda: AlertWindow.ToplevelWindow(titleText="Command", msg="pyinstaller "+" ".join(self.getCommand()), width=600, height=200))
        self.showCommandButton.grid(row = 19, column = 3, columnspan = 1, pady= (3,0), padx = (5,5), sticky = "w")
        
        self.statusLabel = ctk.CTkLabel(master = self, text = "Status: Idle", font=(self.font, 20))
        self.statusLabel.grid(row = 19, column = 16, columnspan = 5, pady= (3,0), padx = (5,10), sticky = "w")
        
        self.expandButton = ctk.CTkButton(master = self, text = "↓", font=(self.font, 18), command=self.expand, width = 25)
        self.expandButton.grid(row = 20, column = 0, columnspan = 2, pady= (3,3), padx = (10, 0), sticky = "w")
        
        self.progressBar = ctk.CTkProgressBar(master = self, mode="indeterminate", width=512, progress_color="#228822", height=8)
        self.progressBar.set(0)  # Initialize progress bar to 0
        self.progressBar.grid(row = 20, column = 1, columnspan = 19, pady= (3,3), padx = (50, 10), sticky = "ew")
        
        self.console = ctk.CTkTextbox(master = self, font=(self.font, 16), wrap="word", state="disabled")
        # self.console.grid(row = 21, column = 0, columnspan = 20, rowspan = 4, pady= (3,3), padx = (10, 10), sticky = "nsew")
        
if __name__ == "__main__":
    app = application()
    app.mainloop()
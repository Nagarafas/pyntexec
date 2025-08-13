# Pyntexec

**Pyntexec** is a graphical user interface (GUI) tool built with [CustomTkinter](https://customtkinter.tomschimansky.com/) that helps you easily package Python scripts into standalone executables using [PyInstaller](https://pyinstaller.org/) or [nuitka](https://nuitka.net). It is designed to simplify the process of building distributable applications from your Python code, providing options for one-file or one-folder builds, icon selection, and more.

![Screenshot-of-app](assets/Pyntexec.png)

## Features

- Simple and intuitive CustomTkinter-based GUI
- Select Python scripts to compile
- Choose between one-file or one-folder output
- Add custom icons to your executables (windows support only, nuitka allows for icon on linux however i have not seen it work)
- Add a splash image (you must unload the image manually from within your script, check **Unloading Splash Images**)
- Include additional data files or folders
- Inlcude extra modules that your script uses but are not imported directly
- Toggle console/terminal window visibility (needed if your script has no GUI and runs in the terminal)
- View build progress and status
- Open the output directory after build
- Cross-platform support (Windows, Linux)

## Requirements

- Python 3.7+ (should be fine even though i've only tested it with 3.13.5)
- [CustomTkinter](https://customtkinter.tomschimansky.com/), installed with (`pip install customtkinter`)
- [PyInstaller](https://pyinstaller.org/) installed on your system (`pip install pyinstaller`)
- [nuitka](https://nuitka.net) installed on your system (`pip install nuitka`)
- [GCC Compiler](https://gcc.gnu.org/install/) installed on your system for nuitka to work

> **Note:**  
> This app uses system/env installed modules to bundle/compile python scripts
> Due to PyInstaller limitations, Pyntexec cannot bundle PyInstaller itself.

## Installation

Clone this repository or download the source code:

```sh
git clone https://github.com/Nagarafas/pyntexec.git
cd pyntexec
```

Install dependencies (if needed):
>pyinstaller and nuitka are installed through the gui if they were not already installed when build is pressed
```sh
pip install customtkinter pyinstaller nuitka
```

## Usage

Run the app:

```sh
python pyntexec.pyw
```

1. Select the Python script you want to compile.
2. Choose build options (onefile / onedir, icon, data, etc.).
3. Pick a backend (PyInstaller / nuitka)
4. Click **Build**.
5. After the build completes, the output folder will open automatically, if not there is a button for it.

## Unloading Splash Images

add this block in your script:

### Pyinstaller
>ensure that Pyi is installed (pip install pyi)
```python
try:
    import pyi_splash
    pyi_splash.update_text('UI Loaded ...')
    pyi_splash.close()
except:
    print("PyInstaller splash screen not available, continuing without it.")
``` 
### nuitka (windows only)
```python
if "NUITKA_ONEFILE_PARENT" in os.environ:
   splash_filename = os.path.join(
      tempfile.gettempdir(),
      "onefile_%d_splash_feedback.tmp" % int(os.environ["NUITKA_ONEFILE_PARENT"]),
   )

   if os.path.exists(splash_filename):
      os.unlink(splash_filename)
```

## Limitations

- Pyntexec requires CustomTkinter, PyInstaller & nuitka to be installed on the system.
- Building executables from within a frozen Pyntexec app is not supported and thus no binaries will be shipped.
- many advanced PyInstaller/nuitka options are not be exposed in the GUI, I might add a textbox later for extra options.

## License

MIT License

## Credits

- [CustomTkinter](https://customtkinter.tomschimansky.com/)
- [PyInstaller](https://pyinstaller.org/)
- [nuitka](https://nuitka.net)

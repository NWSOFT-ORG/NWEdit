run: install-packages; poetry run python3 main.py
install-packages: ; poetry install 
init-ubuntu: ; sudo apt-get update && \
    sudo apt-get upgrade -y && \
    sudo apt install software-properties-common -y && \
    sudo add-apt-repository ppa:deadsnakes/ppa -y && \
    sudo apt-get install -y python3.10-tk python3.10-distutils libvips && \
    python3 -m pip install poetry && \
    poetry env use /usr/bin/python3.10 && \
    poetry install
build-mac: install-packages; @printf "[Compiling via PyInstaller...]\n"
							.venv/bin/pyinstaller --noconfirm --onedir --windowed --icon "src/Images/NWEdit-1024.icns" \
							--hidden-import "art" \
							--hidden-import "pyvips" \
							--hidden-import "Foundation" \
							--hidden-import "json" \
							--hidden-import "json5rw"\
							--hidden-import "ttkthemes" \
							--hidden-import "mistune" \
							--hidden-import "pygments" \
							--hidden-import "PyTouchBar" \
							--hidden-import "send2trash" \
							--hidden-import "tkhtmlview" \
							--hidden-import "tkinter" \
							--hidden-import "tkinter.font" --hidden-import "tkinter.ttk" \
							--hidden-import "tkterminal" \
							--add-data "src:src/" \
							--add-data "docs:docs/" \
							--name "NWEdit" \
							--additional-hooks-dir=. \
							"./main.py" \
						    --clean > /dev/null
							rm -rf build NWEdit.spec
							@printf "\033[36m[Build complete] \033[0m\n"

build-linux: install-packages; @printf "[Compiling via PyInstaller...]\n"
							   poetry run pyinstaller --noconfirm --onefile --windowed --icon "src/Images/NWEdit.ico" \
							   --hidden-import "art" \
							   --hidden-import "pyvips" \
							   --hidden-import "json" \
							   --hidden-import "json5rw" \
							   --hidden-import "mistune" \
							   --hidden-import "pygments" \
							   --hidden-import "send2trash" \
							   --hidden-import "tkhtmlview" \
							   --hidden-import "tkinter.ttk" \
						 	   --hidden-import "tkinter" \
					 		   --hidden-import "tkinter.font" \
					 		   --hidden-import "ttkthemes" \
						 	   --add-data "src:src/" \
						 	   --hidden-import "tkterminal" \
							   --name "NWEdit" \
							   --additional-hooks-dir=. \
					 	 	   "./main.py" \
						 	   --clean > /dev/null
							   rm -rf build NWEdit.spec
							   @printf "\033[36m[Build complete] \033[0m"

build-windows: install-packages; @echo "[Compiling via PyInstaller...]"
							   poetry run pyinstaller --noconfirm --onefile --windowed --icon "src/Images/NWEdit.ico" \
							   --hidden-import "art" \
							   --hidden-import "pyvips" \
							   --hidden-import "json" \
							   --hidden-import "json5rw" \
							   --hidden-import "mistune" \
							   --hidden-import "pygments" \
							   --hidden-import "send2trash" \
							   --hidden-import "tkhtmlview" \
							   --hidden-import "tkinter" \
							   --hidden-import "tkinter.font" \
							   --hidden-import "tkinter.ttk" \
							   --hidden-import "tkterminal" \
							   --hidden-import "ttkthemes" \
							   --add-data "src:src/" \
							   --name "NWEdit" \
							   --additional-hooks-dir=. \
							   "./main.py" \
							   --clean > NUL
							   del NWEdit.spec
							   rmdir build
							   @echo "[Build complete]"

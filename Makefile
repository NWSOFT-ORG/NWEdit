run: install-packages; poetry run python3 main.py
install-packages: ; poetry install 
build-mac: install-packages; @printf "[Compiling via PyInstaller...]\n"
							.venv/bin/pyinstaller --noconfirm --onedir --windowed --icon "src/Images/NWEdit-1024.icns" \
							--hidden-import "art" \
							--hidden-import "cairosvg" \
							--hidden-import "Foundation" \
							--hidden-import "json" \
							--hidden-import "pyjson5" --hidden-import "ttkthemes" \
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
							--additional-hooks-dir=.
							"./main.py" \
						    --clean > /dev/null
							rm -rf build NWEdit.spec
							@printf "\033[36m[Build complete] \033[0m\n"

build-linux: install-packages; @printf "[Compiling via PyInstaller...]\n"
							   poetry run pyinstaller --noconfirm --onefile --windowed --icon "src/Images/NWEdit.ico" \
							   --hidden-import "art" \
							   --hidden-import "cairosvg" \
							   --hidden-import "json" \
							   --hidden-import "pyjson5" \
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
							   --additional-hooks-dir=.
					 	 	   "./main.py" \
						 	   --clean > /dev/null
							   rm -rf build NWEdit.spec
							   @printf "\033[36m[Build complete] \033[0m"

build-windows: install-packages; @echo "[Compiling via PyInstaller...]"
							   poetry run pyinstaller --noconfirm --onefile --windowed --icon "src/Images/NWEdit.ico" \
							   --hidden-import "art" \
							   --hidden-import "cairosvg" \
							   --hidden-import "json" \
							   --hidden-import "pyjson5" \
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
							   --additional-hooks-dir=.
							   "./main.py" \
							   --clean > NUL
							   del NWEdit.spec
							   rmdir build
							   @echo "[Build complete]"

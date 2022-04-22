run: install-packages; python3 main.py
install-packages: ; pip install -r requirements.txt
build-mac: install-packages; @printf "[Compiling via PyInstaller...]\n"
							pyinstaller --noconfirm --onefile --windowed --icon "src/Images/pyplus.ico" \
							--hidden-import "tkinter" --add-data "src:src/" \
							--hidden-import "tkinter.font" --hidden-import "tkinter.ttk" \
							--hidden-import "json5" --hidden-import "ttkthemes" \
							--hidden-import "pygments" \
							--hidden-import "pywebview" \
							--hidden-import "art" \
							--hidden-import "send2trash" \
							--hidden-import "PyTouchBar" \
							--hidden-import "pyobjc" \
							--hidden-import "json" \
							 "./main.py" \
							 --target-architecture "universal2" \
							 --clean > /dev/null
							 rm -rf build main.spec
							 @printf "\033[36m[Build complete] \033[0m\n"

build-linux-win: install-packages; @printf "[Compiling via PyInstaller...]\n"
							pyinstaller --noconfirm --onefile --windowed --icon "src/Images/pyplus.ico" \
							--hidden-import "tkinter" --add-data "src:src/" \
							--hidden-import "tkinter.font" --hidden-import "tkinter.ttk" \
							--hidden-import "json5" --hidden-import "ttkthemes" \
							--hidden-import "pygments" \
							--hidden-import "art" \
							--hidden-import "send2trash" \
							--hidden-import "json" \
							 "./main.py" \
							 --clean > /dev/null
							 rm -rf build main.spec
							 @printf "\033[36m[Build complete] \033[0m"

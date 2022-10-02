run: install-packages; poetry run python3 main.py
install-packages: ; poetry install 
build-mac: install-packages; @printf "[Compiling via PyInstaller...]\n"
							pyinstaller --noconfirm --onefile --windowed --icon "src/Images/pyplus.ico" \
							--hidden-import "art" \
							--hidden-import "Foundation" \
							--hidden-import "json" \
							--hidden-import "json5" --hidden-import "ttkthemes" \
							--hidden-import "pygments" \
							--hidden-import "PyTouchBar" \
							--hidden-import "send2trash" \
							--hidden-import "tkinter.font" --hidden-import "tkinter.ttk" \
							--hidden-import "tkinter" --add-data "src:src/" \
							--hidden-import "tkterminal" \
							 "./main.py" \
							 --clean > /dev/null
							 rm -rf build main.spec
							 @printf "\033[36m[Build complete] \033[0m\n"

build-linux-win: install-packages; @printf "[Compiling via PyInstaller...]\n"
							pyinstaller --noconfirm --onefile --windowed --icon "src/Images/pyplus.ico" \
							--hidden-import "art" \
							--hidden-import "json" \
							--hidden-import "json5" --hidden-import "ttkthemes" \
							--hidden-import "pygments" \
							--hidden-import "send2trash" \
							--hidden-import "tkinter.font" --hidden-import "tkinter.ttk" \
							--hidden-import "tkinter" --add-data "src:src/" \
							--hidden-import "tkterminal" \
							 "./main.py" \
							 --clean > /dev/null
							 rm -rf build main.spec
							 @printf "\033[36m[Build complete] \033[0m"

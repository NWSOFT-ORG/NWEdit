run: install-packages; python3 main.py
activate-virtualenv
install-packages: ; pip install -r requirements.txt
build-mac: install-packages; python3 scripts/build_mac.py py2app -A
build-pyinstaller-linux: install-packages; @printf "[Compiling via PyInstaller...]\n"
							pyinstaller --noconfirm --onedir --windowed --icon "src/Images/pyplus.ico" \
							--hidden-import "tkinter" --add-data "src:src/" \
							--hidden-import "tkinter.font" --hidden-import "tkinter.ttk" \
							--hidden-import "json5" --hidden-import "ttkthemes" \
							--hidden-import "pygments" \
							--hidden-import "art" \
							 "./main.py" \
							 --clean > /dev/null
							 rm -rf build main.spec
							 mv dist/main /usr/local/bin/PyPlus
							 rm -rf dist
							 @printf "\033[36m[Build complete] \033[0m: dist directory moved to $(HOME)/main\n"

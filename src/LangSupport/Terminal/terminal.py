import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')

from gi.repository import Gtk
from gi.repository import WebKit2

window = Gtk.Window()
window.connect('destroy', Gtk.main_quit)

webview = WebKit2.WebView()
window.add(webview)

webview.show()
window.show()

Gtk.main()

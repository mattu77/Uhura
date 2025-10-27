import sys
import os

from path import path

from PyQt6 import QtGui, QtCore
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QUrl
from PyQt6.QtNetwork import QNetworkCookie
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QLineEdit, QFileDialog
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout
from PyQt6.QtWidgets import QWidget, QFileDialog, QSystemTrayIcon, QMenu
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage


class Widgets(QMainWindow):

    __messengerUrl = 'https://www.facebook.com/messages'

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Uhura")
        self.setWindowIcon(QtGui.QIcon('Facebook_Messenger.png'))
        self.resize(1280, 960)
        self.widget = QWidget(self)

        # Where the webpage is rendered.
        self.webview = QWebEngineView()
        self.webview.urlChanged.connect(self.url_changed)
        self.webview.loadStarted.connect(self.loadStarted)
        self.webview.loadFinished.connect(self.loadFinished)

        self.profile = QWebEngineProfile('MyProfile')
        self.profile.setPersistentStoragePath(path('profile/storage'))
        self.profile.setCachePath(path('profile/cache'))
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        self.profile.downloadRequested.connect(self.download)
        self.webpage = QWebEnginePage(self.profile, self.webview)
        self.webpage.navigationRequested.connect(self.navigationRequest)
        self.webview.setPage(self.webpage)

        #self.webview.page().profile().cookieStore().cookieAdded.connect(self.addCookie)
        #self.webview.page().profile().setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        #self.webview.page().profile().setPersistentStoragePath('/storage')

        # Navigation buttons.
        #self.back_button = QPushButton("<")
        #self.back_button.clicked.connect(self.webview.back)
        #self.forward_button = QPushButton(">")
        #self.forward_button.clicked.connect(self.webview.forward)
        #self.refresh_button = QPushButton("Refresh")
        #self.refresh_button.clicked.connect(self.webview.reload)

        # URL address bar.
        #self.url_text = QLineEdit()

        # Button to load the current page.
        #self.go_button = QPushButton("Go")
        #self.go_button.clicked.connect(self.url_set)

        self.toplayout = QHBoxLayout()
        #self.toplayout.addWidget(self.back_button)
        #self.toplayout.addWidget(self.forward_button)
        #self.toplayout.addWidget(self.refresh_button)
        #self.toplayout.addWidget(self.url_text)
        #self.toplayout.addWidget(self.go_button)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.toplayout)
        self.layout.addWidget(self.webview)

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.webview.load(QUrl(self.__messengerUrl))

    def url_changed(self, url):
        pass
        """Refresh the address bar"""
        if not (url.toString().startswith(self.__messengerUrl) or url.toString().startswith('https://www.facebook.com/auth_platform')):
            self.webview.load(QUrl(self.__messengerUrl))
        #self.url_text.setText(url.toString())

    def url_set(self):
        """Load the new URL"""
        #self.webview.setUrl(QUrl(self.url_text.text()))

    def loadStarted(self):
        #self.setCursor(QtCore.Qt.CursorShape.WaitCursor)
        QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)

    def loadFinished(self):
        #self.setCursor(QtCore.Qt.CursorShape.WaitCursor)
        QApplication.restoreOverrideCursor()

    def download(self, item):
        fname, _ = QFileDialog.getSaveFileName(self, 'Save as', item.downloadFileName(), 'All Files (*)')
        if fname:
            item.setDownloadDirectory(os.path.dirname(fname))
            item.setDownloadFileName(os.path.basename(fname))
            item.accept()

    def navigationRequest(self, request):
        #url = request.url().toString()
        #if not (url.startswith(self.__messengerUrl) or url.startswith('https://www.facebook.com/auth_platform')):
        #    request.reject()
        #else:
            request.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = Widgets()

    icon = QtGui.QIcon('Facebook_Messenger.png')

    # Create the tray
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)

    # Create the menu
    menu = QMenu()
    show = QAction("Show")
    #show.triggered(window.show)
    menu.addAction(show)

    # Add a Quit option to the menu.
    quit = QAction("Quit")
    quit.triggered.connect(app.quit)
    menu.addAction(quit)

    # Add the menu to the tray
    tray.setContextMenu(menu)

    window.show()
    try:
        sys.exit(app.exec_())
    except AttributeError:
        sys.exit(app.exec())
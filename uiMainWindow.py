import os

from platformdirs import user_config_dir

from path import path
import webbrowser
import platformdirs

from PyQt6 import QtCore
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QHBoxLayout
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout
from PyQt6.QtWidgets import QWidget, QFileDialog, QSystemTrayIcon, QMenu
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage


class MainWindow(QMainWindow):

    __messengerUrl = 'https://www.messenger.com'

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Uhura")
        self.setWindowIcon(QIcon(path('ui/icon.png')))
        self.resize(1280, 960)
        self.widget = QWidget(self)

        # Where the webpage is rendered.
        self.webview = QWebEngineView()
        self.webview.urlChanged.connect(self.urlChanged)
        self.webview.loadStarted.connect(self.loadStarted)
        self.webview.loadFinished.connect(self.loadFinished)

        self.profile = QWebEngineProfile('MyProfile')
        self.profile.setPersistentStoragePath(user_config_dir() + '/uhura/storage')
        self.profile.setCachePath(path(user_config_dir() + '/uhura/cache'))
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        self.profile.downloadRequested.connect(self.download)
        self.webpage = QWebEnginePage(self.profile, self.webview)
        self.webpage.navigationRequested.connect(self.navigationRequest)
        self.webview.setPage(self.webpage)

        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon(path('ui/icon.png')))

        # Add a context menu to the tray icon
        self.tray_menu = QMenu()

        # Create quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        self.tray_menu.addAction(quit_action)

        # Add menu to tray
        self.tray.setContextMenu(self.tray_menu)
        self.tray.setVisible(True)

        # Connect the tray icon activation event
        self.tray.activated.connect(self.trayClicked)

        #self.webview.page().profile().cookieStore().cookieAdded.connect(self.addCookie)

        self.toplayout = QHBoxLayout()

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.toplayout)
        self.layout.addWidget(self.webview)

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.webview.load(QUrl(self.__messengerUrl))

    def urlChanged(self, url):
        pass
        """Refresh the address bar"""
        if not (url.toString().startswith(self.__messengerUrl) or url.toString().startswith('https://www.facebook.com/auth_platform')):
            self.webview.load(QUrl(self.__messengerUrl))
            webbrowser.open(url.toString(), new=0, autoraise=True)
        #self.url_text.setText(url.toString())

    def urlSet(self):
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

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def trayClicked(self, reason):
        if self.isVisible():
            self.hide()
        else:
            self.show()
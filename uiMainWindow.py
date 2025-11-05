import os
from platformdirs import user_config_dir
from path import path
import webbrowser

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
        self.setStyleSheet('QMainWindow {background: "black";}')
        self.setContentsMargins(0, 0, 0, 0)
        #self.setStyleSheet('QLabel#label {border: 0px; border-radius: 0px; padding: 0px;}')
        self.widget = QWidget(self)
        self.widget.setContentsMargins(0, 0, 0, 0)

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
        self.profile.setNotificationPresenter(self.presentNotification)
        self.webpage = QWebEnginePage(self.profile, self.webview)
        self.webpage.navigationRequested.connect(self.navigationRequest)
        self.webview.setPage(self.webpage)
        self.webview.page().featurePermissionRequested.connect(self.setFeaturePermission)

        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon(path('ui/icon.png')))
        self.tray.setToolTip('Uhura')

        # Add a context menu to the tray icon
        self.trayMenu = QMenu()

        # Create quit action
        reloadAction = QAction("Reload", self)
        reloadAction.triggered.connect(self.reload)
        self.trayMenu.addAction(reloadAction)

        # Create quit action
        quitAction = QAction("Quit", self)
        quitAction.triggered.connect(QApplication.quit)
        self.trayMenu.addAction(quitAction)

        # Add menu to tray
        self.tray.setContextMenu(self.trayMenu)
        self.tray.setVisible(True)

        # Connect the tray icon activation event
        self.tray.activated.connect(self.trayClicked)

        #self.webview.page().profile().cookieStore().cookieAdded.connect(self.addCookie)

        self.toplayout = QHBoxLayout()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.toplayout)
        self.layout.addWidget(self.webview)

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.webview.load(QUrl(self.__messengerUrl))

    def setFeaturePermission(self, origin: QUrl, feature: QWebEnginePage.Feature):
        if feature != QWebEnginePage.Feature.Notifications:
            return

        self.webview.page().setFeaturePermission(origin, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)

    def presentNotification(self, notification):
        print(notification)

    def urlChanged(self, url):
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

    def reload(self):
        self.webview.reload()

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def trayClicked(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.widget.activateWindow()
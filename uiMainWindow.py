import os
from platformdirs import user_config_dir
from path import path
import webbrowser

from PyQt6 import QtCore
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QUrl, QMimeDatabase
from PyQt6.QtWidgets import QApplication, QHBoxLayout
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout
from PyQt6.QtWidgets import QWidget, QFileDialog, QSystemTrayIcon, QMenu
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEnginePermission, QWebEngineNewWindowRequest


class MainWindow(QMainWindow):

    def __init__(self, name, serviceUrl):
        QMainWindow.__init__(self)
        self.__name = name
        self.__mainUrl = serviceUrl
        self.setWindowTitle(self.__name)
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
        self.profile.setPersistentStoragePath(user_config_dir() + '/'+ self.__name +'/storage')
        self.profile.setCachePath(path(user_config_dir() + '/'+ self.__name +'/cache'))
        self.profile.setHttpUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36')
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        self.profile.downloadRequested.connect(self.download)
        self.profile.setNotificationPresenter(self.presentNotification)
        self.webpage = QWebEnginePage(self.profile, self.webview)
        self.webpage.navigationRequested.connect(self.navigationRequest)
        self.webview.setPage(self.webpage)
        self.webview.page().featurePermissionRequested.connect(self.setFeaturePermission)
        self.webview.page().permissionRequested.connect(self.setPermission)
        self.webview.page().newWindowRequested.connect(self.newWindow)

        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon(path('ui/icon.png')))
        self.tray.setToolTip(self.__name)

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

        self.webview.load(QUrl(self.__mainUrl))

    def setFeaturePermission(self, origin: QUrl, feature: QWebEnginePage.Feature):
        print(feature)
        if feature != QWebEnginePage.Feature.Notifications:
            return

        self.webview.page().setFeaturePermission(origin, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)

    def setPermission(self, permission: QWebEnginePermission):
        print(permission.origin())
        print(permission.permissionType())

    def newWindow(self, request: QWebEngineNewWindowRequest):
        print(request.requestedUrl())
        webbrowser.open(request.requestedUrl().toString(), new=0, autoraise=True)

    def presentNotification(self, notification):
        self.tray.showMessage(notification.title(), notification.message())

    def urlChanged(self, url):
        print(url)
        if not (url.toString().startswith(self.__mainUrl)):
            self.webview.load(QUrl(self.__mainUrl))
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
        #print(item.mimeType())
        mtdb = QMimeDatabase()
        mt = mtdb.mimeTypeForName(item.mimeType())
        fname, _ = QFileDialog.getSaveFileName(self, 'Save as', item.downloadFileName(), mt.filterString())
        if fname:
            item.setDownloadDirectory(os.path.dirname(fname))
            item.setDownloadFileName(os.path.basename(fname))
            item.accept()

    def navigationRequest(self, request):
        print(request.url())
        #url = request.url().toString()
        #if not (url.startswith(self.__mainUrl) or url.startswith('https://www.facebook.com/auth_platform')):
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
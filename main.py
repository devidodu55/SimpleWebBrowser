import sys
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QStatusBar, QToolBar, QAction, QLineEdit, QShortcut

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, *args, **kwargs):
        super(CustomWebEnginePage, self).__init__(*args, **kwargs)

    def acceptNavigationRequest(self, url, type, isMainFrame):
        if type == QWebEnginePage.NavigationTypeLinkClicked:
            self.view().parent().add_new_tab(url, "New Tab")
            return False
        return super().acceptNavigationRequest(url, type, isMainFrame)

class BrowserTab(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super(BrowserTab, self).__init__(*args, **kwargs)
        self.setPage(CustomWebEnginePage(self))

class Window(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.navigation_bar = QToolBar('Navigation Toolbar')
        self.addToolBar(self.navigation_bar)

        back_button = QAction("Back", self)
        back_button.setStatusTip('Go to the previous page you visited')
        back_button.triggered.connect(lambda: self.tabs.currentWidget().back() if self.tabs.currentWidget() else None)
        self.navigation_bar.addAction(back_button)

        refresh_button = QAction("Refresh", self)
        refresh_button.setStatusTip('Refresh this page')
        refresh_button.triggered.connect(lambda: self.tabs.currentWidget().reload() if self.tabs.currentWidget() else None)
        self.navigation_bar.addAction(refresh_button)

        next_button = QAction("Next", self)
        next_button.setStatusTip('Go to the next page')
        next_button.triggered.connect(lambda: self.tabs.currentWidget().forward() if self.tabs.currentWidget() else None)
        self.navigation_bar.addAction(next_button)

        home_button = QAction("Home", self)
        home_button.setStatusTip('Go to the home page (Google page)')
        home_button.triggered.connect(self.go_to_home)
        self.navigation_bar.addAction(home_button)

        new_tab_button = QAction("New Tab", self)
        new_tab_button.setStatusTip('Open a new tab')
        new_tab_button.triggered.connect(lambda: self.add_new_tab(QUrl('https://www.google.com'), 'New Tab'))
        self.navigation_bar.addAction(new_tab_button)

        self.navigation_bar.addSeparator()

        self.URLBar = QLineEdit()
        self.URLBar.returnPressed.connect(self.navigate_to_url)
        self.navigation_bar.addWidget(self.URLBar)

        self.addToolBarBreak()

        # Adding another toolbar which contains bookmarks
        bookmarks_toolbar = QToolBar('Bookmarks', self)
        self.addToolBar(bookmarks_toolbar)

        pythongeeks = QAction("PythonGeeks", self)
        pythongeeks.setStatusTip("Go to the PythonGeeks website")
        pythongeeks.triggered.connect(lambda: self.go_to_URL(QUrl("https://pythongeeks.org")))
        bookmarks_toolbar.addAction(pythongeeks)

        facebook = QAction("Facebook", self)
        facebook.setStatusTip("Go to Facebook")
        facebook.triggered.connect(lambda: self.go_to_URL(QUrl("https://www.facebook.com")))
        bookmarks_toolbar.addAction(facebook)

        linkedin = QAction("LinkedIn", self)
        linkedin.setStatusTip("Go to LinkedIn")
        linkedin.triggered.connect(lambda: self.go_to_URL(QUrl("https://in.linkedin.com")))
        bookmarks_toolbar.addAction(linkedin)

        instagram = QAction("Instagram", self)
        instagram.setStatusTip("Go to Instagram")
        instagram.triggered.connect(lambda: self.go_to_URL(QUrl("https://www.instagram.com")))
        bookmarks_toolbar.addAction(instagram)

        twitter = QAction("Twitter", self)
        twitter.setStatusTip('Go to Twitter')
        twitter.triggered.connect(lambda: self.go_to_URL(QUrl("https://www.twitter.com")))
        bookmarks_toolbar.addAction(twitter)

        self.add_new_tab(QUrl('https://www.google.com'), 'Homepage')

        # Adding keyboard shortcuts
        self.shortcut_new_tab = QShortcut(Qt.CTRL + Qt.Key_T, self)
        self.shortcut_new_tab.activated.connect(lambda: self.add_new_tab(QUrl('https://www.google.com'), 'New Tab'))

        self.shortcut_close_tab = QShortcut(Qt.CTRL + Qt.Key_W, self)
        self.shortcut_close_tab.activated.connect(lambda: self.close_current_tab(self.tabs.currentIndex()))

        self.show()

    def add_new_tab(self, qurl=None, label="Blank"):
        if qurl is None:
            qurl = QUrl('https://www.google.com')  # Default URL

        browser = BrowserTab()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        if self.tabs.count() == 0:
            return
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return

        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle(f"{title} - Simple Web Browser")

    def navigate_to_url(self):
        q = QUrl(self.URLBar.text())
        if q.scheme() == "":
            q.setScheme("http")

        self.tabs.currentWidget().setUrl(q)

    def update_urlbar(self, qurl, browser=None):
        if browser != self.tabs.currentWidget():
            return

        self.URLBar.setText(qurl.toString())
        self.URLBar.setCursorPosition(0)

    def go_to_home(self):
        self.tabs.currentWidget().setUrl(QUrl('https://www.google.com/'))

    def go_to_URL(self, url: QUrl):
        if url.scheme() == '':
            url.setScheme('https://')
        self.tabs.currentWidget().setUrl(url)
        self.update_urlbar(url, self.tabs.currentWidget())


app = QApplication(sys.argv)
app.setApplicationName('Simple Web Browser')

window = Window()
app.exec_()

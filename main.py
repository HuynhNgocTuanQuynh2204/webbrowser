from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWebEngineWidgets import *
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.browser_tabs = QTabWidget()
        self.browser_tabs.setTabsClosable(True)
        self.browser_tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.browser_tabs)
        self.add_new_tab(QUrl("http://www.google.com"), "Home")
        self.showMaximized()

        # Navbar
        navbar = QToolBar()
        self.addToolBar(navbar)

        # Logo
        logo = QLabel()
        logo.setPixmap(QPixmap("path/to/logo.png").scaled(30, 30, Qt.KeepAspectRatio))
        navbar.addWidget(logo)

        back_btn = QAction('Back', self)
        back_btn.triggered.connect(lambda: self.current_browser().back())
        navbar.addAction(back_btn)

        forward_btn = QAction('Forward', self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        navbar.addAction(forward_btn)

        reload_btn = QAction('Reload', self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        navbar.addAction(reload_btn)

        home_btn = QAction('Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        # Translate button with dropdown
        self.current_language = 'en'
        translate_btn = QToolButton()
        translate_btn.setText('Translate')
        translate_menu = QMenu(self)
        self.languages = {
            'English': 'en',
            'Vietnamese': 'vi',
            'French': 'fr',
            'Spanish': 'es'
        }
        for lang, code in self.languages.items():
            action = QAction(lang, self)
            action.triggered.connect(lambda checked, code=code: self.translate_page(code))
            translate_menu.addAction(action)
        translate_btn.setMenu(translate_menu)
        translate_btn.setPopupMode(QToolButton.InstantPopup)
        navbar.addWidget(translate_btn)

        # Bookmark button
        bookmark_btn = QAction('Bookmark', self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        navbar.addAction(bookmark_btn)

        self.browser_tabs.currentChanged.connect(self.update_url_bar)

        show_html_btn = QAction('Show HTML', self)
        show_html_btn.triggered.connect(self.show_html)
        navbar.addAction(show_html_btn)

        # New tab button
        new_tab_btn = QAction('New Tab', self)
        new_tab_btn.triggered.connect(lambda: self.add_new_tab(QUrl("http://www.google.com"), "New Tab"))
        navbar.addAction(new_tab_btn)

        # More button with dropdown
        more_btn = QToolButton()
        more_btn.setText('...')
        more_menu = QMenu(self)
        history_action = QAction('Lịch sử', self)
        history_action.triggered.connect(self.view_history)
        more_menu.addAction(history_action)
        more_btn.setMenu(more_menu)
        more_btn.setPopupMode(QToolButton.InstantPopup)
        navbar.addWidget(more_btn)

        # Bookmark toolbar
        self.bookmark_toolbar = QToolBar("Bookmarks")
        self.addToolBar(Qt.BottomToolBarArea, self.bookmark_toolbar)
        self.bookmarks = {}

        # Hidden bookmarks folder
        self.hidden_bookmarks_menu = QMenu("Hidden Bookmarks", self)
        hidden_bookmarks_action = QAction("Hidden Bookmarks", self)
        hidden_bookmarks_action.setMenu(self.hidden_bookmarks_menu)
        self.bookmark_toolbar.addAction(hidden_bookmarks_action)

        # History
        self.history = []

    def add_new_tab(self, qurl=None, label="Blank"):
        if qurl is None:
            qurl = QUrl("http://www.google.com")

        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.browser_tabs.addTab(browser, label)
        self.browser_tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_tab_title(browser))
        browser.urlChanged.connect(lambda qurl: self.add_to_history(qurl))

    def current_browser(self):
        return self.browser_tabs.currentWidget()

    def close_current_tab(self, i):
        if self.browser_tabs.count() < 2:
            return
        self.browser_tabs.removeTab(i)

    def navigate_home(self):
        self.current_browser().setUrl(QUrl("http://www.google.com"))

    def navigate_to_url(self):
        url = self.url_bar.text()
        if ".com" in url:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url
        else:
            url = f"https://www.google.com/search?q={url}"
        self.current_browser().setUrl(QUrl(url))

    def update_url_bar(self, i):
        qurl = self.current_browser().url()
        self.url_bar.setText(qurl.toString())

    def update_tab_title(self, browser):
        i = self.browser_tabs.indexOf(browser)
        self.browser_tabs.setTabText(i, browser.title())

    def show_html(self):
        self.current_browser().page().toHtml(self.display_html)

    def display_html(self, html):
        html_window = QMainWindow(self)
        html_window.setWindowTitle("Page HTML")
        html_window.resize(800, 600)
        text_edit = QTextEdit()
        text_edit.setPlainText(html)
        html_window.setCentralWidget(text_edit)
        html_window.show()

    def translate_page(self, lang_code):
        self.current_language = lang_code
        current_url = self.current_browser().url().toString()
        translate_url = f"https://translate.google.com/translate?hl={lang_code}&sl=auto&tl={lang_code}&u={current_url}"
        self.current_browser().setUrl(QUrl(translate_url))

    def add_bookmark(self):
        current_url = self.current_browser().url().toString()
        if current_url in self.bookmarks:
            del self.bookmarks[current_url]
            for action in self.bookmark_toolbar.actions():
                if action.data() == current_url:
                    self.bookmark_toolbar.removeAction(action)
                    break
            for action in self.hidden_bookmarks_menu.actions():
                if action.data() == current_url:
                    self.hidden_bookmarks_menu.removeAction(action)
                    break
        else:
            dialog = QDialog(self)
            dialog.setWindowTitle("Add Bookmark")
            layout = QVBoxLayout()

            name_label = QLabel("Enter name for the bookmark:")
            layout.addWidget(name_label)
            name_input = QLineEdit()
            layout.addWidget(name_input)

            show_on_toolbar = QCheckBox("Show on toolbar")
            layout.addWidget(show_on_toolbar)

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            dialog.setLayout(layout)
            if dialog.exec_() == QDialog.Accepted:
                name = name_input.text()
                show = show_on_toolbar.isChecked()
                if name:
                    favicon = self.current_browser().icon()
                    self.bookmarks[current_url] = (name, favicon)
                    action = QAction(favicon, name, self)
                    action.setData(current_url)
                    action.triggered.connect(lambda checked, url=current_url: self.current_browser().setUrl(QUrl(url)))
                    if show:
                        self.bookmark_toolbar.addAction(action)
                    else:
                        self.hidden_bookmarks_menu.addAction(action)

    def add_to_history(self, qurl):
        self.history.append(qurl.toString())

    def view_history(self):
        history_window = QMainWindow(self)
        history_window.setWindowTitle("Browsing History")
        history_window.resize(800, 600)
        layout = QVBoxLayout()

        history_list = QListWidget()
        for url in self.history:
            item = QListWidgetItem(url)
            history_list.addItem(item)
        layout.addWidget(history_list)

        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(lambda: self.delete_history(history_list))
        layout.addWidget(delete_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        history_window.setCentralWidget(central_widget)
        history_window.show()

    def delete_history(self, history_list):
        for item in history_list.selectedItems():
            self.history.remove(item.text())
            history_list.takeItem(history_list.row(item))

app = QApplication(sys.argv)
QApplication.setApplicationName("Simplicodes browser")
window = MainWindow()
app.exec_()
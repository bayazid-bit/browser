import sys
import json
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QCursor ,QPixmap , QPainter, QBrush
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QLineEdit, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import QInputDialog


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bayazid's Browser")
        self.setGeometry(100, 100, 1024, 768)
        self.setWindowIcon(QIcon("data/main_icon.png"))

        # Initialize history and bookmarks lists
        self.history = []
        self.bookmarks = []

        # Load history and bookmarks from file
        self.load_history()
        self.load_bookmarks()

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet(
            """
            border-radius:20px ; 
            """
        )
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)

        navbar = QToolBar()
        self.addToolBar(navbar)
        navbar.setStyleSheet(
            """
            QToolBar {
            padding:10px ; 
            }
            """
        )

        # Add toolbar buttons and actions (Back, Forward, Reload, etc.)
        self.add_toolbar_buttons(navbar)

        self.add_new_tab(QUrl('https://www.google.com'), 'Home')

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.apply_gray_theme()

    def apply_gray_theme(self):

        """ Apply gray and light gray theme for the UI """
        self.setStyleSheet("""
            QMainWindow {
                background-color: lightgray;  /* Light gray background for the window */
                color: darkgray;  /* Dark gray text color */
            }
            QToolBar {
                background-color: lightgray;  /* Light gray toolbar */
                border: none;
            }
            QStatusBar {
                background-color: lightgray;
                color: darkgray;  /* Dark gray text in the status bar */
            }
            QLabel {
                color: darkgray;  /* Dark gray text color */
            }
            QLineEdit {
                background-color: lightgray;  /* Light gray input fields */
                color: black;  /* Black text */
                border: 1px solid gray; 
                border-radius: 50%;  /* Light gray border */
            }
            QTabWidget::pane {
                background-color: lightgray;  /* Light gray tab pane */
                border: 2px solid gray;  /* Light gray border for tabs */
            }
            QTabBar::tab {
                background-color: lightgray;  /* Light gray background for tabs */
                color: black;
                padding: 10px;
                border-top-left-radius: 10px;
                border-top-right-radius: 20px;
                height: 15px;
                margin-right: 5px;
                transition: background-color 0.3s, color 0.3s;  /* Smooth transitions */
            }
            QTabBar::tab:selected {
                background-color: darkgray;  /* Dark gray background for selected tab */
                color: white;  /* White text for active tab */
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);  /* Light shadow for active tab */
            }
            QTabBar::tab:hover {
                background-color: #d3d3d3;  /* Slightly darker gray on hover */
            }
            QTabBar::tab:!selected {
                background-color: lightgray;  /* Light gray background for unselected tabs */
                color: darkgray;  /* Dark gray text for inactive tabs */
            }
        """)

    def add_toolbar_buttons(self, navbar):
        """ Add all toolbar buttons like Back, Forward, Reload, etc. """

        back_button = QAction('Back', self)
        back_button.setIcon(QIcon("data/backward.png"))
        back_button.triggered.connect(lambda: self.tabs.currentWidget().back())
        navbar.addAction(back_button)

        forward_button = QAction('Forward', self)
        forward_button.setIcon(QIcon("data/forward.png"))
        forward_button.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navbar.addAction(forward_button)

        reload_button = QAction('Reload', self)
        reload_button.setIcon(QIcon("data/reload.png"))
        reload_button.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navbar.addAction(reload_button)

        home_button = QAction('Home', self)
        home_button.setIcon(QIcon("data/home.png"))
        home_button.triggered.connect(self.navigate_home)
        navbar.addAction(home_button)

        # Status indicator
        self.loading_status = QLabel("Ready")  # Default status text
        self.loading_status.setStyleSheet("color: darkgray; font-size: 14px; padding: 0 10px;")
        navbar.addWidget(self.loading_status)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setStyleSheet("""
            QLineEdit {
                border-radius: 10px;
                border: 1px solid gray;
                padding: 8px;
                font-size: 14px;
                margin-left: 10px;
                margin-right: 10px;
                background-color: lightgray;
                color: black;
                width: 300px;
            }
        """)
        self.url_bar.returnPressed.connect(self.load_url_from_address_bar)
        navbar.addWidget(self.url_bar)

        # Bookmarks button
        bookmark_button = QAction('Bookmark', self)
        bookmark_button.setIcon(QIcon("data/bookmark.png"))
        bookmark_button.triggered.connect(self.add_bookmark)
        navbar.addAction(bookmark_button)

        #new tab button
        new_tab_button = QAction('New Tab', self)
        new_tab_button.setIcon(QIcon("data/n_tab.png"))
        new_tab_button.triggered.connect(self.add_new_tab)
        navbar.addAction(new_tab_button)

        # "More" menu button
        more_button = QAction('...', self)
        more_button.setIcon(QIcon("data/menu_icon.png"))
        more_button.triggered.connect(self.show_more_menu)
        navbar.addAction(more_button)

    def tab_open_doubleclick(self, i):
        """ Open new tab on double click """
        if i == -1:
            self.add_new_tab()

    def add_bookmark(self):
        """ Add current page URL to bookmarks """

        current_url = self.tabs.currentWidget().url().toString()
        if current_url not in self.bookmarks:
            self.bookmarks.append(current_url)
            self.save_bookmarks()
            QMessageBox.information(self, "Bookmark Added", "This page has been added to your bookmarks.")
        else:
            QMessageBox.warning(self, "Bookmark Exists", "This page is already bookmarked.")

    def clear_history(self):
        """ Clear browser history """
        self.history = []
        self.save_history()
        QMessageBox.information(self, "History Cleared", "Your browsing history has been cleared.")

    def add_new_tab(self, qurl=None, label="New Tab"):
        """ Add a new tab """
        if qurl is None or not isinstance(qurl, QUrl):
            qurl = QUrl('https://www.google.com')

        browser = QWebEngineView()
        browser.setUrl(qurl)
        self.history.append(qurl.toString())
        self.save_history()

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))

        browser.loadStarted.connect(lambda: self.update_loading_status("Loading..."))
        browser.loadFinished.connect(lambda: self.update_loading_status("Completed"))
        browser.loadProgress.connect(self.update_loading_percentage)

    def show_more_menu(self):
        """ Show options menu when "..." button is clicked """
        menu = QMenu(self)
        menu.setStyleSheet(
            """
            QMenu
            {
                border-radius:50%;
                padding: 13px 10px ;
                color: gray ; 
                
            }

            QMenu:item{
            padding: 10px ;
            color: black ;
            }
            
            """
        )

        # New Tab action (at the top of the list)
        new_tab_action = QAction('New Tab', self)
        new_tab_action.setIcon(QIcon("data/n_tab.png"))
        new_tab_action.triggered.connect(self.add_new_tab)
        menu.addAction(new_tab_action)

        # New Window action
        new_window_action = QAction('New Window', self)
        new_window_action.setIcon(QIcon("data/n_window.png"))
        new_window_action.triggered.connect(self.open_new_window)
        menu.addAction(new_window_action)
        menu.addSeparator() 


        # History action
        history_action = QAction('History', self)
        history_action.setIcon(QIcon("data/history.png"))
        history_action.triggered.connect(self.show_history)
        menu.addAction(history_action)

        # Bookmarks action
        bookmarks_action = QAction('Bookmarks', self)
        bookmarks_action.setIcon(QIcon("data/bookmark1.png"))
        bookmarks_action.triggered.connect(self.show_bookmarks)
        menu.addAction(bookmarks_action)

        # Clear History action
        clear_history_action = QAction('Clear History', self)
        clear_history_action.setIcon(QIcon("data/d_history.png"))
        clear_history_action.triggered.connect(self.clear_history)
        menu.addAction(clear_history_action)

        #add settings action 
        settings_action = QAction("Settings" , self)
        settings_action.setIcon(QIcon("data/settings.png"))
        settings_action.triggered.connect(self.comming_soon)
        menu.addAction(settings_action)

        #About 
        about_action = QAction("About me.")
        about_action.setIcon(QIcon("data/about_me.png"))
        about_action.triggered.connect(self.about_me)
        menu.addAction(about_action)


        # Close action
        close_action = QAction('Exit', self)
        close_action.setIcon(QIcon("data/exit.png"))
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)
        menu.exec_(QPoint(QCursor.pos().x() -150 , QCursor.pos().y() +20 ))

    def open_new_window(self):
        """ Open a new window for the browser """
        new_window = Browser()
        new_window.show()

    def show_history(self):
        """ Show browser history in a visually improved window """
        self.history_dialog = QDialog(self)
        self.history_dialog.setWindowTitle("History")
        self.history_dialog.setWindowIcon(QIcon("data/history.png"))
        self.history_dialog.resize(800, 600)  # নির্দিষ্ট উইন্ডো সাইজ সেট

        # Layout and Style
        history_layout = QVBoxLayout()
        self.history_dialog.setStyleSheet("background-color: #ffffff; border-radius: 10px;")

        # History List
        history_list = QListWidget()
        history_list.setStyleSheet("padding: 10px; font-size: 14px;")
        for url in self.history:
            item = QListWidgetItem(url)
            item.setIcon(QIcon("data/history.png"))  
            history_list.addItem(item)

        history_list.clicked.connect(self.visit_history)

        # Buttons Layout
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.setStyleSheet("padding: 8px; font-size: 14px; background-color:rgb(120, 110, 110); color: white;")
        ok_button.clicked.connect(self.history_dialog.accept)

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("padding: 8px; font-size: 14px; background-color: rgba(115, 109, 109, 0.4); color: white;")
        cancel_button.clicked.connect(self.history_dialog.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        # Adding Widgets to Layout
        history_layout.addWidget(history_list)
        history_layout.addLayout(button_layout)
        self.history_dialog.setLayout(history_layout)

        self.history_dialog.exec_()

    def show_bookmarks(self):
        """ Show bookmarks in a visually enhanced window with Add and Close buttons """
        self.bookmarks_dialog = QDialog(self)
        self.bookmarks_dialog.setWindowTitle("Bookmarks")
        self.bookmarks_dialog.setWindowIcon(QIcon("data/bookmark1.png"))
        self.bookmarks_dialog.resize(800, 600)
        self.bookmarks_dialog.setStyleSheet("background-color: #f8f9fa; border-radius: 10px;")

        # Layout
        bookmarks_layout = QVBoxLayout()

        # Search Bar
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search bookmarks...")
        search_bar.setStyleSheet(
            "padding: 8px; font-size: 14px; border: 1px solid #ccc; border-radius: 5px; margin-bottom: 10px;"
        )

        # Bookmarks List
        bookmarks_list = QListWidget()
        bookmarks_list.setStyleSheet("font-size: 14px; padding: 10px; background-color: #ffffff;")
        font = QFont("Arial", 12)
        bookmarks_list.setFont(font)

        # Search Functionality
        def filter_bookmarks():
            search_text = search_bar.text().lower()
            for i in range(bookmarks_list.count()):
                item = bookmarks_list.item(i)
                item.setHidden(search_text not in item.text().lower())

        search_bar.textChanged.connect(filter_bookmarks)

        # Adding Bookmarks
        for bookmark in self.bookmarks:
            item = QListWidgetItem(bookmark)
            item.setIcon(QIcon("data/bookmark1.png"))  
            bookmarks_list.addItem(item)

        bookmarks_list.clicked.connect(self.visit_bookmark)

        # Buttons Layout
        button_layout = QHBoxLayout()
        
        # Add Bookmark Button
        add_button = QPushButton("Add Bookmark")
        add_button.setStyleSheet(
        """
        QPushButton {
            padding: 8px 15px; 
            font-size: 14px; 
            background-color: #e0e0e0; 
            border: 1px solid #ccc; 
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #d6d6d6;
        }
        QPushButton:pressed {
            background-color: #bfbfbf;
        }
        """
        )

        add_button.clicked.connect(lambda: self.add_bookmark_action(bookmarks_list))
        button_layout.addWidget(add_button)

        # Close Button
        close_button = QPushButton("Close")
        close_button.setStyleSheet(
        """
        QPushButton {
            padding: 8px 15px; 
            font-size: 14px; 
            background-color: #f0f0f0; 
            border: 1px solid #ccc; 
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #e6e6e6;
        }
        QPushButton:pressed {
            background-color: #cccccc;
        }
        """
        )
        close_button.clicked.connect(self.bookmarks_dialog.reject)
        button_layout.addWidget(close_button)

        # Adding Widgets to Layout
        bookmarks_layout.addWidget(search_bar)
        bookmarks_layout.addWidget(bookmarks_list)
        bookmarks_layout.addLayout(button_layout)

        self.bookmarks_dialog.setLayout(bookmarks_layout)
        self.bookmarks_dialog.exec_()


    def add_bookmark_action(self, bookmarks_list):
        """ Open a custom dialog for adding a bookmark """
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Bookmark")
        dialog.setWindowIcon(QIcon("data/bookmark1.png"))
        dialog.resize(400, 200)
        dialog.setStyleSheet(
            """
            QDialog {
                background-color: #f8f9fa; 
                border-radius: 10px; 
                padding: 20px;
            }
            QLabel {
                font-size: 14px; 
                color: #333; 
                margin-bottom: 10px;
            }
            QLineEdit {
                font-size: 14px; 
                padding: 8px; 
                border: 1px solid #ccc; 
                border-radius: 5px; 
                background-color: #ffffff;
            }
            QPushButton {
                font-size: 14px; 
                padding: 8px 15px; 
                background-color: #e0e0e0; 
                border: 1px solid #bbb; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d6d6d6;
            }
            QPushButton:pressed {
                background-color: #cccccc;
            }
            """
        )

        # Layout for dialog
        layout = QVBoxLayout()

        # Label for input prompt
        label = QLabel("Enter the URL for the bookmark:")
        layout.addWidget(label)

        # Input field for URL
        url_input = QLineEdit()
        url_input.setPlaceholderText("https://example.com")
        layout.addWidget(url_input)

        # Buttons layout
        button_layout = QHBoxLayout()

        # Add button
        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.add_bookmark_to_list(dialog, url_input, bookmarks_list))
        button_layout.addWidget(add_button)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)

        # Add layouts to dialog
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec_()

    def add_bookmark_to_list(self, dialog, url_input, bookmarks_list):
        """ Add the bookmark to the list and close the dialog """
        new_bookmark = url_input.text().strip()
        if new_bookmark:
            # Add to internal bookmarks list
            self.bookmarks.append(new_bookmark)  # Make sure self.bookmarks is initialized

            # Add to QListWidget
            item = QListWidgetItem(new_bookmark)
            item.setIcon(QIcon("data/bookmark1.png"))
            bookmarks_list.addItem(item)

            # Close dialog
            dialog.accept()

    def visit_history(self, index):
        """ Visit a URL from history """
        url = self.history[index.row()]
        self.add_new_tab(QUrl(url))
        self.history_dialog.accept()

    def visit_bookmark(self, index):
        """ Visit a bookmark """
        url = self.bookmarks[index.row()]
        self.add_new_tab(QUrl(url))
        self.bookmarks_dialog.accept() 

    def save_history(self):
        """ Save history to file """
        with open("data/history.json", "w") as f:
            json.dump(self.history, f)

    def load_history(self):
        """ Load history from file """
        try:
            with open("data/history.json", "r") as f:
                self.history = json.load(f)
        except FileNotFoundError:
            self.history = []

    def save_bookmarks(self):
        """ Save bookmarks to file """
        with open("data/bookmarks.json", "w") as f:
            json.dump(self.bookmarks, f)

    def load_bookmarks(self):
        """ Load bookmarks from file """
        try:
            with open("data/bookmarks.json", "r") as f:
                self.bookmarks = json.load(f)
        except FileNotFoundError:
            self.bookmarks = []

    def update_urlbar(self, q, browser):
        """ Update the URL bar """
        if q != browser.url():
            self.url_bar.setText(q.toString())
        self.url_bar.setCursorPosition(0)

    def load_url_from_address_bar(self):
        """ Load URL from address bar """
        qurl = QUrl(self.url_bar.text())
        if qurl.scheme() == "":
            qurl.setScheme("http")
        self.tabs.currentWidget().setUrl(qurl)

    def update_loading_status(self, status):
        """ Update the loading status in the status bar """
        self.loading_status.setText(status)

    def update_loading_percentage(self, progress):
        """ Update the loading percentage """
        self.loading_status.setText(f"Loading: {progress}%")

    def current_tab_changed(self, i):
        """ Called when the current tab is changed """
        if self.tabs.count() > 0:
            current_tab = self.tabs.currentWidget()
            self.url_bar.setText(current_tab.url().toString())

    def close_current_tab(self, index):
        """ Close the current tab """
        self.tabs.removeTab(index)

    def navigate_home(self):
        """ Navigate to the homepage (Google in this case) """
        self.add_new_tab(QUrl('https://www.google.com'), 'Home')
    
    def comming_soon(self):

        e = QMessageBox(self)
        e.setIcon(QMessageBox.Information)  
        e.setWindowTitle("Not Available")

        e.setText("Comming Soon! Thanks For Trying.")
        e.setStandardButtons(QMessageBox.Ok)
        e.setWindowIcon(QIcon("data/main_icon.png"))
        e.exec_()
        

    def about_me(self):

        dialog = QDialog(self)
        dialog.setWindowTitle("About me")
        dialog.setWindowIcon(QIcon("data/about_me.png"))
        
        label = QLabel("HI! I'm MD.Bayazid.\nA Student of SSC Batch 2025.\nI Made This Browser As My Python Practice.\nAnd I Will Take Care Of It.\nIf You Want To Update It.\nFeel Free To Do It.\nBye! :)")
        layout = QVBoxLayout()
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.exec_()

  
if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = Browser()
    browser.show()
    sys.exit(app.exec_())

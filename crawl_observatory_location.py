import os
import sys
import sqlite3
from PyQt5.QtCore import QUrl, pyqtSignal, QThread
from PyQt5.QtGui import QShowEvent, QCloseEvent, QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QTextEdit
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage


class CustomWebEnginePage(QWebEnginePage):
    sig_console_message = pyqtSignal(object, object, object, object)

    def __init__(self, parent=None):
        super().__init__(parent)

    def javaScriptConsoleMessage(self, level, message, line, source):
        self.sig_console_message.emit(level, message, line, source)


class ThreadSearch(QThread):
    sig_done = pyqtSignal(list)

    def __init__(self, page: QWebEnginePage, option_value_list: list, delay_ms: int):
        super().__init__()
        self._page = page
        self._option_value_list = option_value_list
        self._delay_ms = delay_ms
        script_path = os.path.abspath('./crawl_get_table.js')
        with open(script_path, 'r', encoding='utf-8') as fp:
            self._js_table_script = fp.read()
        self._obs_list = list()

    def run(self):
        for i, value in enumerate(self._option_value_list):
            # 콤보박스 선택하고 함수호출
            script = f"""
            $("select[id='mang_code']").val('{value}').prop("selected", true);
            $("select[id='district']").val('').prop("selected", true);
            searchInfo2();
            """
            self._page.runJavaScript(script)
            # 대기한다
            self.msleep(self._delay_ms)
            # 테이블 가져오기 스크립트를 수행한다
            self._page.runJavaScript(self._js_table_script, lambda x: self.callbackTable(x, i))
            self.msleep(100)

    def callbackTable(self, result: list, index: int):
        print(f'Thread({index}) - Table Record Count: {len(result)}')
        self._obs_list.extend(result)
        if index == len(self._option_value_list) - 1:
            self.sig_done.emit(self._obs_list)


class AirKoreaCrawlerWindow(QMainWindow):
    _first_loaded: bool = False  # 페이지 최초 로드 플래그
    _airkorea_url: str = "https://airkorea.or.kr/web/stationInfo?pMENU_NO=93"
    _thread = None

    def __init__(self):
        super().__init__()
        self._webview = QWebEngineView()
        self._category_list = []
        self._obs_list = []
        self._btnStartCrawl = QPushButton('START')
        self._btnGetResult = QPushButton('GET RESULT')
        self._editConsole = QTextEdit()
        self.initControl()
        self.initLayout()

    def initLayout(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        vbox = QVBoxLayout(widget)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)

        subwgt = QWidget()
        subwgt.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        hbox = QHBoxLayout(subwgt)
        hbox.setContentsMargins(2, 4, 2, 0)
        hbox.addWidget(self._btnStartCrawl)
        hbox.addWidget(self._btnGetResult)
        vbox.addWidget(subwgt)
        vbox.addWidget(self._webview)
        vbox.addWidget(self._editConsole)

    def initControl(self):
        self._btnStartCrawl.clicked.connect(self.startCrawl)
        self._btnGetResult.clicked.connect(self.getResult)
        webpage = CustomWebEnginePage(self._webview)
        webpage.sig_console_message.connect(self.onWebPageConsoleMessage)
        self._webview.setPage(webpage)
        self._webview.loadFinished.connect(self.onWebViewLoadFinished)
        self._editConsole.setReadOnly(True)
        self._editConsole.setFixedHeight(100)
        self._editConsole.setLineWrapColumnOrWidth(-1)
        self._editConsole.setLineWrapMode(QTextEdit.FixedPixelWidth)

    def startCrawl(self):
        self.startThread(2000)

    def startThread(self, delay_ms: int):
        if self._thread is None:
            self._obs_list.clear()
            option_value_list = [x.get('value') for x in self._category_list]
            self._thread = ThreadSearch(self._webview.page(), option_value_list, delay_ms)
            self._thread.sig_done.connect(self.onThreadDone)
            self._thread.start()

    def onThreadDone(self, obs_list: list):
        del self._thread
        self._thread = None
        print(f"Get Observatory List Count: {len(obs_list)}")
        self._obs_list.extend(obs_list)

    def getResult(self):
        dbpath = './airkorea_obs_list.db'
        if os.path.isfile(dbpath):
            os.remove(dbpath)
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE airkoreaobs( \
            고유번호 VARCHAR PRIMARY KEY,\
            이름     VARCHAR,\
            주소     VARCHAR);")
        sql = "INSERT INTO airkoreaobs values(?, ?, ?);"
        sqldata = [(x.get('id'), x.get('name'), x.get('addr')) for x in self._obs_list]
        cursor.executemany(sql, sqldata)
        conn.commit()
        conn.close()

    def showEvent(self, a0: QShowEvent) -> None:
        # 창이 show되면 URL로 웹페이지 로드
        self._webview.load(QUrl(self._airkorea_url))

    def closeEvent(self, a0: QCloseEvent) -> None:
        self._webview.close()
        self.deleteLater()

    def addTextMessage(self, message: str):
        cursor = QTextCursor(self._editConsole.textCursor())
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(message + '\n')
        vscroll = self._editConsole.verticalScrollBar()
        vscroll.setValue(vscroll.maximum())

    def onWebPageConsoleMessage(self, level, message, line, source):
        text = f'{message} (lv:{level}, line:{line})'
        self.addTextMessage(text)

    def onWebViewLoadFinished(self, result: bool):
        if not self._first_loaded:
            # 페이지 최초 로드 시 콤보박스 카테고리 option 리스트 가져오기
            self._category_list.clear()
            script_path = os.path.abspath('./crawl_get_category.js')
            with open(script_path, 'r', encoding='utf-8') as fp:
                script = fp.read()
                self._webview.page().runJavaScript(script, self.callbackCategoryList)
            self._first_loaded = True

    def callbackCategoryList(self, result: object):
        if isinstance(result, list):
            print(f'Get Category List: {result}')
            self._category_list.extend(result)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = AirKoreaCrawlerWindow()
    wnd.resize(1000, 800)
    wnd.show()
    app.exec_()

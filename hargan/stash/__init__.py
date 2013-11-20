import wx
from poe.web_api.session import PathSession, NotLoggedInException
from threading import *
import logging


logger = logging.getLogger(__name__)

ID_LOGIN_BUTTON = wx.NewId()
ID_RESULT_LOGIN = wx.NewId()


def EVENT_RESULT(window, result_id, func):
    window.Connect(-1, -1, result_id, func)


class ResultEvent(wx.PyEvent):
    def __init__(self, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(ID_RESULT_LOGIN)
        self.data = data
        logger.debug("Event data: %s" % data)


class SessionThread(Thread):
    def __init__(self, notify_window, username, password):
        Thread.__init__(self)
        self._notify_window = notify_window
        self.username = username
        self.password = password
        self.start()

    def run(self):
        wx.PostEvent(self._notify_window, ResultEvent({
            "event": "logging_in",
            "status": "Logging in...",
        }))
        self.session = PathSession()

        self.session.login(self.username, self.password)

        if not self.session.logged_in:
            wx.PostEvent(self._notify_window, ResultEvent({
                "event": "login_failed",
                "status": "Couldn't log in",
            }))

            return False

        wx.PostEvent(self._notify_window, ResultEvent({
            "event": "get_stash",
            "status": "Getting stash tabs...",
        }))

        self.session.get_stash(league="nemesis")

        wx.PostEvent(self._notify_window, ResultEvent({
            "event": "done",
            "status": "Logged in",
        }))


class StashTab(object):
    def __init__(self):
        pass


class Stash(object):
    def __init__(self):
        pass


class LoginUI(wx.Frame):
    def __init__(self, main_window, *args, **kwargs):
        super(LoginUI, self).__init__(size=(300, 150), *args, **kwargs)
        self.InitUI()
        self.Centre()
        self.Bind(wx.EVT_CLOSE, self.close)

        self.worker = None
        self.main_window = main_window

    def InitUI(self):
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        grid = wx.FlexGridSizer(2, 2, 9, 25)

        self.username = wx.TextCtrl(panel)
        self.password = wx.TextCtrl(panel, style=wx.TE_PASSWORD)

        login_button = wx.Button(panel, ID_LOGIN_BUTTON, "Login")
        self.Bind(wx.EVT_BUTTON, self.login, id=ID_LOGIN_BUTTON)
        EVENT_RESULT(self, ID_RESULT_LOGIN, self.result)

        self.status = wx.StaticText(panel, label="")

        grid.AddMany([
            wx.StaticText(panel, label="Email"),
            (self.username, 1, wx.EXPAND),
            wx.StaticText(panel, label="Password"),
            (self.password, 1, wx.EXPAND),
            (login_button, 1, wx.EXPAND),
            self.status,
        ])

        grid.AddGrowableRow(2, 1)
        grid.AddGrowableCol(1, 1)

        vbox.Add(grid, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)

        panel.SetSizer(vbox)

    def login(self, event):
        if not self.worker:
            self.worker = SessionThread(self,
                                        self.username.GetValue(),
                                        self.password.GetValue())

    def result(self, event):
        self.status.SetLabel(event.data["status"])

        if event.data["event"] == "done":
            self.main_window.Show()
            self.Destroy()

        self.worker = None

    def close(self, event):
        self.main_window.Destroy()
        self.Destroy()


class MainUI(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MainUI, self).__init__(*args, **kwargs)
        self.InitUI()
        self.InitLogin()
        self.Centre()

    def InitUI(self):
        panel = wx.Panel(self)
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        help_menu = wx.Menu()

        menubar.Append(file_menu, "&File")
        menubar.Append(help_menu, "&Help")

        self.SetMenuBar(menubar)

        self.console = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.BORDER_SUNKEN | wx.TE_READONLY)

        self.console.AppendText("TEST")
        self.console.AppendText("TEST")

    def InitLogin(self):
        self.login_window = LoginUI(self, None, title="Login")
        self.login_window.Show()


if __name__ == "__main__":
    app = wx.App(redirect=False)
    main_window = MainUI(None, title="Hargan")
    app.MainLoop()

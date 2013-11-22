import wx
from poe.web_api.session import (
    PathSession, InvalidLoginException, InvalidSessionIDException
    )
# TODO: Remove this later
from poe.config import settings
from threading import *
import logging


logger = logging.getLogger(__name__)

ID_LOGIN_BUTTON = wx.NewId()
ID_SWITCH_BUTTON = wx.NewId()
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
    def __init__(self, notify_window, use_session_id, credentials):
        Thread.__init__(self)
        self._notify_window = notify_window
        self.use_session_id = use_session_id
        self.credentials = credentials
        self.start()

    def run(self):
        wx.PostEvent(self._notify_window, ResultEvent({
            "event": "logging_in",
            "status": "Logging in with credentials: %s..." % self.credentials[0],
        }))
        self.session = PathSession()

        try:
            if self.use_session_id:
                self.session.login_session_id(self.credentials[0])
            else:
                self.session.login_normal(self.credentials[0], self.credentials[1])
        except (InvalidLoginException, InvalidSessionIDException) as e:
            wx.PostEvent(self._notify_window, ResultEvent({
                "event": "login_exception",
                "status": e.args[1],
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
        super(LoginUI, self).__init__(size=(300, 175), *args, **kwargs)
        self.use_session_id = False
        self.InitUI()
        self.Centre()
        self.Bind(wx.EVT_CLOSE, self.close)

        self.worker = None
        self.main_window = main_window

    def InitUI(self):
        panel = wx.Panel(self)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        username_sizer = wx.BoxSizer(wx.HORIZONTAL)
        password_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # options_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # TODO: Remove settings later
        self.username_text = wx.StaticText(panel, label="Email")
        self.username = wx.TextCtrl(panel, value=settings["USERNAME"])

        username_sizer.Add(self.username_text, proportion=1, flag=wx.CENTER)
        username_sizer.Add(self.username, proportion=3, flag=wx.CENTER)

        self.password = wx.TextCtrl(panel, value=settings["PASSWORD"],
                                    style=wx.TE_PASSWORD)

        self.password_text = wx.StaticText(panel, label="Password")
        password_sizer.Add(self.password_text, proportion=1, flag=wx.CENTER)
        password_sizer.Add(self.password, proportion=3, flag=wx.CENTER)

        # TODO: options_sizer

        self.login_button = wx.Button(panel, ID_LOGIN_BUTTON, "Login")
        self.Bind(wx.EVT_BUTTON, self.login, id=ID_LOGIN_BUTTON)
        EVENT_RESULT(self, ID_RESULT_LOGIN, self.result)
        self.login_button.SetFocus()

        self.switch_login_type_button = wx.Button(panel, ID_SWITCH_BUTTON,
                                                  label="Switch Login Type")
        self.Bind(wx.EVT_BUTTON, self.switch_login_type, id=ID_SWITCH_BUTTON)

        buttons_sizer.Add(self.login_button, proportion=1,
                          flag=wx.ALL | wx.EXPAND)
        buttons_sizer.Add(self.switch_login_type_button, proportion=2,
                          flag=wx.ALL | wx.EXPAND)

        main_sizer.AddMany([
            (username_sizer, 1, wx.ALL | wx.EXPAND, 20),
            (password_sizer, 1, wx.ALL | wx.EXPAND, 20),
            # (options_sizer, 1, wx.ALL | wx.EXPAND, 20),
            (buttons_sizer, 2, wx.ALL | wx.EXPAND, 15),
        ])

        panel.status = self.CreateStatusBar()
        self.status = panel.status

        self.SetMinSize(self.GetSize())
        self.SetMaxSize(self.GetSize())
        self.Centre()

        self.SetSizer(main_sizer)

    def login(self, event):
        if not self.worker:
            self.login_button.Disable()
            self.switch_login_type_button.Disable()
            if self.use_session_id:
                credentials = (self.username.GetValue(),)
            else:
                credentials = (self.username.GetValue(), self.password.GetValue())
            self.worker = SessionThread(self, self.use_session_id, credentials)
        event.Skip()

    def result(self, event):
        self.status.SetStatusText(event.data["status"])

        if event.data["event"] == "done":
            self.main_window.Show()
            self.Destroy()
        if event.data["event"] == "login_exception":
            self.login_button.Enable()
            self.switch_login_type_button.Enable()

        self.worker = None

    def close(self, event):
        self.main_window.Destroy()
        self.Destroy()
        event.Skip()

    def switch_login_type(self, event):
        self.use_session_id = not self.use_session_id
        if self.use_session_id:
            self.username_text.SetLabel("Session ID")
            self.password_text.Hide()
            self.password.Hide()
        else:
            self.username_text.SetLabel("Email")
            self.password_text.Show()
            self.password.Show()
        event.Skip()


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

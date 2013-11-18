import wx
from poe.web_api.session import PathSession, NotLoggedInException


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

        self.main_window = main_window

    def InitUI(self):
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        grid = wx.FlexGridSizer(2, 2, 9, 25)

        self.username = wx.TextCtrl(panel)
        self.password = wx.TextCtrl(panel, style=wx.TE_PASSWORD)

        grid.AddMany([
            wx.StaticText(panel, label="Email"),
            (self.username, 1, wx.EXPAND),
            wx.StaticText(panel, label="Password"),
            (self.password, 1, wx.EXPAND),
        ])

        login_button = wx.Button(panel, label="Login")
        login_button.Bind(wx.EVT_BUTTON, self.login)

        # TODO: Figure out how to make this span 2 columns
        grid.Add(login_button, 1, wx.EXPAND)

        grid.AddGrowableRow(2, 1)
        grid.AddGrowableCol(1, 1)

        vbox.Add(grid, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)

        panel.SetSizer(vbox)

    def login(self, event):
        if self.main_window.login(self.username.GetValue(),
                                  self.password.GetValue()):
            self.main_window.Show()
            self.Destroy()
        self.Show()


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

    def login(self, username, password):
        # TODO: Should move out of here and use something to thread
        self.session = PathSession()
        self.session.login(username, password)

        if not self.session.logged_in:
            self.login_window.Show()
            self.Hide()
            return False

        self.session.get_stash(league="nemesis")

        return True

if __name__ == "__main__":
    app = wx.App(redirect=False)
    main_window = MainUI(None, title="Hargan")
    app.MainLoop()

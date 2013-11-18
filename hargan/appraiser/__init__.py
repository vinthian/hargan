import wx


def get_clipboard():
    _ = wx.App(False)

    clip = wx.Clipboard()
    do = wx.TextDataObject()

    if clip.IsOpened():
        # clipboard in use, raise exception instead?
        return None
    else:
        clip.Open()
        success = clip.GetData(do)
        clip.Close()
        data = do.GetText() if success else None

    return data


print get_clipboard()
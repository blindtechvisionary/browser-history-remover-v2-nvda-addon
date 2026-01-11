import addonHandler
import globalPluginHandler
import scriptHandler
import ui
import gui
import wx
import os
import shutil
import psutil
import logging
import config
from datetime import datetime

addonHandler.initTranslation()

logging.basicConfig(level=logging.ERROR, filename='browser_history_remover.log')

ADDON_SUMMARY = "Browser History Remover"

confspec = {
    "copyHistoryBeforeDeletion": "boolean(default=False)",
    "defaultBrowser": "string(default='Google Chrome')",
}

config.conf.spec["browserHistoryRemover"] = confspec

BROWSERS = [
    "Google Chrome",
    "Microsoft Edge",
    "Firefox",
    "Opera",
    "Brave",
    "Vivaldi",
    "Chromium",
    "Waterfox",
    "Pale Moon",
    "Basilisk",
    "SeaMonkey"
]


def getBrowserPath(browser):
    user_profile = os.path.expanduser("~")
    appdata_local = os.path.join(user_profile, "AppData", "Local")
    appdata_roaming = os.path.join(user_profile, "AppData", "Roaming")

    paths = {
        "Google Chrome": os.path.join(appdata_local, "Google", "Chrome", "User Data"),
        "Microsoft Edge": os.path.join(appdata_local, "Microsoft", "Edge", "User Data"),
        "Firefox": os.path.join(appdata_roaming, "Mozilla", "Firefox", "Profiles"),
        "Opera": os.path.join(appdata_roaming, "Opera Software", "Opera Stable"),
        "Brave": os.path.join(appdata_local, "BraveSoftware", "Brave-Browser", "User Data"),
        "Vivaldi": os.path.join(appdata_local, "Vivaldi", "User Data"),
        "Chromium": os.path.join(appdata_local, "Chromium", "User Data"),
        "Waterfox": os.path.join(appdata_roaming, "Waterfox", "Profiles"),
        "Pale Moon": os.path.join(appdata_roaming, "Moonchild Productions", "Pale Moon", "Profiles"),
        "Basilisk": os.path.join(appdata_roaming, "Moonchild Productions", "Basilisk", "Profiles"),
        "SeaMonkey": os.path.join(appdata_roaming, "Mozilla", "SeaMonkey", "Profiles")
    }

    return paths.get(browser, None)


def isBrowserInstalled(browser):
    browser_path = getBrowserPath(browser)
    if browser_path and os.path.exists(browser_path):
        return True
    return False


def isBrowserRunning(browser):
    process_map = {
        "Google Chrome": ["chrome.exe"],
        "Microsoft Edge": ["msedge.exe"],
        "Firefox": ["firefox.exe"],
        "Opera": ["opera.exe"],
        "Brave": ["brave.exe"],
        "Vivaldi": ["vivaldi.exe"],
        "Chromium": ["chromium.exe"],
        "Waterfox": ["waterfox.exe"],
        "Pale Moon": ["palemoon.exe"],
        "Basilisk": ["basilisk.exe"],
        "SeaMonkey": ["seamonkey.exe"]
    }

    processes = process_map.get(browser, [])
    if not processes:
        return False

    try:
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info.get('name')
                if proc_name and proc_name.lower() in [p.lower() for p in processes]:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception:
        pass
    return False


def getBackupPath(browser):
    user_profile = os.path.expanduser("~")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(user_profile, "Downloads", "browser_history_remover", "history", browser, timestamp)
    return backup_path


def getBackupBasePath(browser):
    user_profile = os.path.expanduser("~")
    backup_path = os.path.join(user_profile, "Downloads", "browser_history_remover", "history", browser)
    return backup_path


def copyHistoryFiles(profile_path, browser):
    if not os.path.exists(profile_path):
        return False, _("Profile path does not exist.")

    backup_path = getBackupPath(browser)
    
    try:
        os.makedirs(backup_path, exist_ok=True)
    except Exception as e:
        return False, _("Failed to create backup directory: {}").format(str(e))

    file_keywords = [
        'history', 'cookies', 'webdata', 'favicons',
        'logins', 'formhistory', 'places', 'session',
        'top sites', 'shortcuts', 'visited', 'downloads'
    ]

    copied_count = 0
    failed_count = 0

    for root, dirs, files in os.walk(profile_path):
        for file in files:
            if any(keyword in file.lower() for keyword in file_keywords):
                try:
                    src_path = os.path.join(root, file)
                    relative_path = os.path.relpath(root, profile_path)
                    dest_dir = os.path.join(backup_path, relative_path)
                    os.makedirs(dest_dir, exist_ok=True)
                    dest_path = os.path.join(dest_dir, file)
                    shutil.copy2(src_path, dest_path)
                    if os.path.exists(dest_path):
                        src_size = os.path.getsize(src_path)
                        dest_size = os.path.getsize(dest_path)
                        if src_size == dest_size:
                            copied_count += 1
                        else:
                            failed_count += 1
                    else:
                        failed_count += 1
                except Exception:
                    failed_count += 1

    if copied_count == 0 and failed_count > 0:
        return False, _("Failed to copy any files.")

    return True, backup_path


def deleteHistoryFiles(profile_path):
    if not os.path.exists(profile_path):
        return False, _("Profile path does not exist.")

    file_keywords = [
        'history', 'cache', 'cookies', 'webdata', 'favicons',
        'logins', 'formhistory', 'places', 'session',
        'top sites', 'shortcuts', 'thumbnails', 'visited', 'downloads'
    ]

    dir_keywords = [
        'cache', 'storage', 'session', 'local storage',
        'sync data', 'indexeddb', 'websql', 'file system',
        'gpucache', 'code cache', 'service worker'
    ]

    deleted_files = 0
    deleted_dirs = 0

    for root, dirs, files in os.walk(profile_path):
        for file in files:
            if any(keyword in file.lower() for keyword in file_keywords):
                try:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                    deleted_files += 1
                except Exception:
                    pass

        for dir_name in dirs[:]:
            if any(keyword in dir_name.lower() for keyword in dir_keywords):
                try:
                    dir_path = os.path.join(root, dir_name)
                    shutil.rmtree(dir_path, ignore_errors=True)
                    deleted_dirs += 1
                except Exception:
                    pass

    return True, _("Deleted {} files and {} directories.").format(deleted_files, deleted_dirs)


def restoreHistoryFiles(backup_path, browser_path):
    if not os.path.exists(backup_path):
        return False, _("Selected backup path does not exist.")

    if not os.path.isdir(backup_path):
        return False, _("Selected path is not a directory.")

    has_files = False
    for root, dirs, files in os.walk(backup_path):
        if files:
            has_files = True
            break

    if not has_files:
        return False, _("Selected backup folder is empty or contains no files.")

    if not os.path.exists(browser_path):
        try:
            os.makedirs(browser_path, exist_ok=True)
        except Exception as e:
            return False, _("Failed to create browser data path: {}").format(str(e))

    file_keywords = [
        'history', 'cache', 'cookies', 'webdata', 'favicons',
        'logins', 'formhistory', 'places', 'session',
        'top sites', 'shortcuts', 'thumbnails', 'visited', 'downloads'
    ]

    dir_keywords = [
        'cache', 'storage', 'session', 'local storage',
        'sync data', 'indexeddb', 'websql', 'file system',
        'gpucache', 'code cache', 'service worker'
    ]

    try:
        for root, dirs, files in os.walk(browser_path):
            for file in files:
                if any(keyword in file.lower() for keyword in file_keywords):
                    try:
                        file_path = os.path.join(root, file)
                        os.remove(file_path)
                    except Exception:
                        pass
            for dir_name in dirs[:]:
                if any(keyword in dir_name.lower() for keyword in dir_keywords):
                    try:
                        dir_path = os.path.join(root, dir_name)
                        shutil.rmtree(dir_path, ignore_errors=True)
                    except Exception:
                        pass
    except Exception as e:
        return False, _("Failed to clean existing browser data: {}").format(str(e))

    copied_count = 0
    failed_count = 0
    failed_files = []

    try:
        for root, dirs, files in os.walk(backup_path):
            for file in files:
                try:
                    src_path = os.path.join(root, file)
                    relative_path = os.path.relpath(root, backup_path)
                    if relative_path == ".":
                        dest_dir = browser_path
                    else:
                        dest_dir = os.path.join(browser_path, relative_path)
                    os.makedirs(dest_dir, exist_ok=True)
                    dest_path = os.path.join(dest_dir, file)
                    shutil.copy2(src_path, dest_path)
                    if os.path.exists(dest_path):
                        src_size = os.path.getsize(src_path)
                        dest_size = os.path.getsize(dest_path)
                        if src_size == dest_size:
                            copied_count += 1
                        else:
                            failed_count += 1
                            failed_files.append(file)
                    else:
                        failed_count += 1
                        failed_files.append(file)
                except Exception as e:
                    failed_count += 1
                    failed_files.append(file)
    except Exception as e:
        return False, _("Failed to restore history files: {}").format(str(e))

    if copied_count == 0:
        return False, _("No files were restored. Failed files: {}").format(", ".join(failed_files[:5]))

    try:
        shutil.rmtree(backup_path, ignore_errors=True)
        parent_dir = os.path.dirname(backup_path)
        if os.path.exists(parent_dir) and not os.listdir(parent_dir):
            shutil.rmtree(parent_dir, ignore_errors=True)
    except Exception:
        pass

    if failed_count > 0:
        return True, _("{} files restored successfully. {} files failed.").format(copied_count, failed_count)

    return True, _("{} files restored successfully.").format(copied_count)


class FocusableStaticText(wx.Panel):
    def __init__(self, parent, label=""):
        super().__init__(parent, style=wx.TAB_TRAVERSAL | wx.BORDER_SIMPLE)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.textCtrl = wx.StaticText(self, label=label)
        sizer.Add(self.textCtrl, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_SET_FOCUS, self.onFocus)
        self.Bind(wx.EVT_KILL_FOCUS, self.onKillFocus)

    def onFocus(self, evt):
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
        self.textCtrl.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))
        self.Refresh()
        evt.Skip()

    def onKillFocus(self, evt):
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        self.textCtrl.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
        self.Refresh()
        evt.Skip()

    def SetLabel(self, label):
        self.textCtrl.SetLabel(label)


class ConfigurationDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title=_("Browser History Remover - Configuration"), size=(550, 350))
        self.Centre()
        self.initUI()
        self.loadSettings()
        self.Bind(wx.EVT_CHAR_HOOK, self.onKeyDown)
        self.copyHistoryCheckBox.SetFocus()

    def initUI(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)

        self.copyHistoryCheckBox = sHelper.addItem(
            wx.CheckBox(self, label=_("Co&py browser history before deletion"))
        )

        defaultBrowserLabel = wx.StaticText(self, label=_("Select default browser for &quick remove:"))
        sHelper.addItem(defaultBrowserLabel)

        self.defaultBrowserCombo = sHelper.addItem(
            wx.ComboBox(self, choices=BROWSERS, style=wx.CB_READONLY)
        )
        self.defaultBrowserCombo.Bind(wx.EVT_COMBOBOX, self.onBrowserChange)

        self.notePanel = FocusableStaticText(self, label="")
        self.notePanel.SetMinSize((500, 60))
        sHelper.addItem(self.notePanel, flag=wx.EXPAND)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.saveButton = wx.Button(self, label=_("&Save"))
        self.saveButton.Bind(wx.EVT_BUTTON, self.onSave)
        buttonSizer.Add(self.saveButton, flag=wx.RIGHT, border=10)

        self.cancelButton = wx.Button(self, wx.ID_CANCEL, label=_("&Cancel"))
        self.cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)
        buttonSizer.Add(self.cancelButton)

        sHelper.addItem(buttonSizer)

        mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL | wx.EXPAND, proportion=1)
        self.SetSizer(mainSizer)

    def updateNoteText(self):
        selection = self.defaultBrowserCombo.GetSelection()
        if selection != wx.NOT_FOUND:
            browser = BROWSERS[selection]
        else:
            browser = config.conf["browserHistoryRemover"]["defaultBrowser"]
        noteText = _("Note: Assign the shortcut to remove the history of {browser} via quick shortcut.\nDefault shortcut: NVDA+Alt+D").format(browser=browser)
        self.notePanel.SetLabel(noteText)

    def onBrowserChange(self, evt):
        self.updateNoteText()
        evt.Skip()

    def loadSettings(self):
        self.copyHistoryCheckBox.SetValue(config.conf["browserHistoryRemover"]["copyHistoryBeforeDeletion"])
        defaultBrowser = config.conf["browserHistoryRemover"]["defaultBrowser"]
        if defaultBrowser in BROWSERS:
            self.defaultBrowserCombo.SetSelection(BROWSERS.index(defaultBrowser))
        else:
            self.defaultBrowserCombo.SetSelection(0)
        self.updateNoteText()

    def onKeyDown(self, evt):
        keyCode = evt.GetKeyCode()

        if keyCode == wx.WXK_ESCAPE:
            self.onCancel(None)
            return

        evt.Skip()

    def onSave(self, evt):
        config.conf["browserHistoryRemover"]["copyHistoryBeforeDeletion"] = self.copyHistoryCheckBox.GetValue()
        selection = self.defaultBrowserCombo.GetSelection()
        if selection != wx.NOT_FOUND:
            config.conf["browserHistoryRemover"]["defaultBrowser"] = BROWSERS[selection]
        self.EndModal(wx.ID_OK)

    def onCancel(self, evt):
        self.EndModal(wx.ID_CANCEL)


class BrowserHistoryRemoverDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title=_("Browser History Remover"), size=(500, 400))
        self.Centre()
        self.initUI()
        self.Bind(wx.EVT_CHAR_HOOK, self.onKeyDown)
        self.browsersList.SetFocus()

    def initUI(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)

        browsersLabel = wx.StaticText(self, label=_("Select browser:"))
        sHelper.addItem(browsersLabel)

        self.browsersList = wx.ListBox(self, choices=BROWSERS, style=wx.LB_SINGLE)
        self.browsersList.SetSelection(0)
        sHelper.addItem(self.browsersList, proportion=1, flag=wx.EXPAND)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.deleteButton = wx.Button(self, label=_("&Delete History"))
        self.deleteButton.Bind(wx.EVT_BUTTON, self.onDeleteHistory)
        buttonSizer.Add(self.deleteButton, flag=wx.RIGHT, border=10)

        self.restoreButton = wx.Button(self, label=_("&Restore History"))
        self.restoreButton.Bind(wx.EVT_BUTTON, self.onRestoreHistory)
        buttonSizer.Add(self.restoreButton, flag=wx.RIGHT, border=10)

        self.configButton = wx.Button(self, label=_("&Configurations"))
        self.configButton.Bind(wx.EVT_BUTTON, self.onConfigurations)
        buttonSizer.Add(self.configButton, flag=wx.RIGHT, border=10)

        self.exitButton = wx.Button(self, wx.ID_CANCEL, label=_("E&xit"))
        self.exitButton.Bind(wx.EVT_BUTTON, self.onExit)
        buttonSizer.Add(self.exitButton)

        sHelper.addItem(buttonSizer)

        mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL | wx.EXPAND, proportion=1)
        self.SetSizer(mainSizer)

    def onKeyDown(self, evt):
        keyCode = evt.GetKeyCode()
        modifiers = evt.GetModifiers()

        if keyCode == wx.WXK_ESCAPE:
            self.onExit(None)
            return

        if modifiers == wx.MOD_CONTROL:
            if keyCode in (ord('Q'), ord('q')):
                self.onExit(None)
                return
            if keyCode in (ord('F'), ord('f')):
                self.browsersList.SetFocus()
                return

        if modifiers == wx.MOD_ALT:
            if keyCode in (ord('D'), ord('d')):
                self.onDeleteHistory(None)
                return
            if keyCode in (ord('R'), ord('r')):
                self.onRestoreHistory(None)
                return
            if keyCode in (ord('C'), ord('c')):
                self.onConfigurations(None)
                return

        evt.Skip()

    def onExit(self, evt):
        self.EndModal(wx.ID_CANCEL)

    def onConfigurations(self, evt):
        configDialog = ConfigurationDialog(self)
        configDialog.ShowModal()
        configDialog.Destroy()

    def onDeleteHistory(self, evt):
        selection = self.browsersList.GetSelection()
        if selection == wx.NOT_FOUND:
            gui.messageBox(
                _("No browser selected."),
                _("Error"),
                wx.OK | wx.ICON_ERROR,
                self
            )
            return

        selected_browser = BROWSERS[selection]

        if not isBrowserInstalled(selected_browser):
            gui.messageBox(
                _("Sorry, {browser} is not installed in your system.").format(browser=selected_browser),
                _("Browser Not Found"),
                wx.OK | wx.ICON_ERROR,
                self
            )
            return

        if isBrowserRunning(selected_browser):
            gui.messageBox(
                _("Please exit {browser} before removing history.").format(browser=selected_browser),
                _("Browser Running"),
                wx.OK | wx.ICON_WARNING,
                self
            )
            return

        confirm = gui.messageBox(
            _("Delete all browsing history for {browser}?").format(browser=selected_browser),
            _("Confirm Deletion"),
            wx.YES_NO | wx.ICON_QUESTION,
            self
        )

        if confirm == wx.NO:
            return

        success, error_message = self.deleteBrowserHistory(selected_browser)

        if success:
            gui.messageBox(
                _("History for {browser} has been deleted successfully.").format(browser=selected_browser),
                _("Success"),
                wx.OK | wx.ICON_INFORMATION,
                self
            )
        else:
            gui.messageBox(
                _("Failed to delete history for {browser}.\n\nReason: {error}").format(
                    browser=selected_browser,
                    error=error_message
                ),
                _("Error"),
                wx.OK | wx.ICON_ERROR,
                self
            )

    def onRestoreHistory(self, evt):
        selection = self.browsersList.GetSelection()
        if selection == wx.NOT_FOUND:
            gui.messageBox(
                _("No browser selected."),
                _("Error"),
                wx.OK | wx.ICON_ERROR,
                self
            )
            return

        selected_browser = BROWSERS[selection]

        if not isBrowserInstalled(selected_browser):
            gui.messageBox(
                _("Sorry, {browser} is not installed in your system.").format(browser=selected_browser),
                _("Browser Not Found"),
                wx.OK | wx.ICON_ERROR,
                self
            )
            return

        if isBrowserRunning(selected_browser):
            gui.messageBox(
                _("Please exit {browser} before restoring history.").format(browser=selected_browser),
                _("Browser Running"),
                wx.OK | wx.ICON_WARNING,
                self
            )
            return

        backup_base_path = getBackupBasePath(selected_browser)
        initial_path = backup_base_path if os.path.exists(backup_base_path) else os.path.expanduser("~")

        dirDialog = wx.DirDialog(
            self,
            _("Select backup folder containing history for {browser}").format(browser=selected_browser),
            defaultPath=initial_path,
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
        )

        if dirDialog.ShowModal() != wx.ID_OK:
            dirDialog.Destroy()
            return

        backup_path = dirDialog.GetPath()
        dirDialog.Destroy()

        if not backup_path:
            gui.messageBox(
                _("No folder selected."),
                _("Error"),
                wx.OK | wx.ICON_ERROR,
                self
            )
            return

        if not os.path.exists(backup_path):
            gui.messageBox(
                _("Selected folder does not exist."),
                _("Error"),
                wx.OK | wx.ICON_ERROR,
                self
            )
            return

        if not os.listdir(backup_path):
            gui.messageBox(
                _("Selected folder is empty."),
                _("Error"),
                wx.OK | wx.ICON_ERROR,
                self
            )
            return

        browser_path = getBrowserPath(selected_browser)
        if not browser_path:
            gui.messageBox(
                _("Could not determine browser data path for {browser}.").format(browser=selected_browser),
                _("Error"),
                wx.OK | wx.ICON_ERROR,
                self
            )
            return

        confirm = gui.messageBox(
            _("This will replace the current history data for {browser} with the backup from:\n{path}\n\nCurrent history data will be deleted. Continue?").format(
                browser=selected_browser,
                path=backup_path
            ),
            _("Confirm Restore"),
            wx.YES_NO | wx.ICON_QUESTION,
            self
        )

        if confirm == wx.NO:
            return

        success, message = restoreHistoryFiles(backup_path, browser_path)

        if success:
            gui.messageBox(
                _("History for {browser} has been restored successfully.\n\n{details}").format(
                    browser=selected_browser,
                    details=message
                ),
                _("Success"),
                wx.OK | wx.ICON_INFORMATION,
                self
            )
        else:
            gui.messageBox(
                _("Failed to restore history for {browser}.\n\nReason: {error}").format(
                    browser=selected_browser,
                    error=message
                ),
                _("Error"),
                wx.OK | wx.ICON_ERROR,
                self
            )

    def deleteBrowserHistory(self, browser):
        try:
            browser_path = getBrowserPath(browser)

            if not browser_path or not os.path.exists(browser_path):
                return False, _("Browser data path not found.")

            if config.conf["browserHistoryRemover"]["copyHistoryBeforeDeletion"]:
                copy_success, copy_result = copyHistoryFiles(browser_path, browser)
                if not copy_success:
                    return False, _("Failed to backup history: {}").format(copy_result)

            delete_success, delete_result = deleteHistoryFiles(browser_path)
            if not delete_success:
                return False, delete_result

            return True, ""

        except Exception as e:
            logging.error("Error deleting history for {}: {}".format(browser, str(e)))
            return False, str(e)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self):
        super().__init__()
        self.createMenu()

    def createMenu(self):
        self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
        self.menuItem = self.toolsMenu.Append(
            wx.ID_ANY,
            _("Browser History Remover"),
            _("Remove browsing history for various browsers")
        )
        gui.mainFrame.sysTrayIcon.Bind(
            wx.EVT_MENU,
            self.onBrowserHistoryRemover,
            self.menuItem
        )

    def terminate(self):
        try:
            self.toolsMenu.Remove(self.menuItem)
        except Exception:
            pass

    def onBrowserHistoryRemover(self, evt):
        wx.CallAfter(self.showDialog)

    def showDialog(self):
        gui.mainFrame.prePopup()
        dialog = None
        try:
            dialog = BrowserHistoryRemoverDialog(gui.mainFrame)
            dialog.ShowModal()
        finally:
            if dialog:
                try:
                    dialog.Destroy()
                except RuntimeError:
                    pass
            gui.mainFrame.postPopup()

    @scriptHandler.script(
        description=_("Open Browser History Remover"),
        category=_("Browser History Remover"),
        gesture="kb:NVDA+alt+b"
    )
    def script_openBrowserHistoryRemover(self, gesture):
        wx.CallAfter(self.showDialog)

    @scriptHandler.script(
        description=_("Quick remove history for default browser"),
        category=_("Browser History Remover"),
        gesture="kb:NVDA+alt+d"
    )
    def script_quickRemoveHistory(self, gesture):
        wx.CallAfter(self.quickRemoveHistory)

    def quickRemoveHistory(self):
        defaultBrowser = config.conf["browserHistoryRemover"]["defaultBrowser"]

        if not isBrowserInstalled(defaultBrowser):
            ui.message(_("{browser} is not installed.").format(browser=defaultBrowser))
            return

        if isBrowserRunning(defaultBrowser):
            ui.message(_("{browser} is running. Please exit it before history deletion.").format(browser=defaultBrowser))
            return

        browser_path = getBrowserPath(defaultBrowser)
        if not browser_path or not os.path.exists(browser_path):
            ui.message(_("Browser data path not found for {browser}.").format(browser=defaultBrowser))
            return

        try:
            if config.conf["browserHistoryRemover"]["copyHistoryBeforeDeletion"]:
                copy_success, copy_result = copyHistoryFiles(browser_path, defaultBrowser)
                if not copy_success:
                    ui.message(_("Failed to backup history for {browser}.").format(browser=defaultBrowser))
                    return

            delete_success, delete_result = deleteHistoryFiles(browser_path)
            if delete_success:
                ui.message(_("History for {browser} has been deleted successfully.").format(browser=defaultBrowser))
            else:
                ui.message(_("Failed to delete history for {browser}.").format(browser=defaultBrowser))
        except Exception as e:
            logging.error("Error deleting history for {}: {}".format(defaultBrowser, str(e)))
            ui.message(_("Failed to delete history for {browser}.").format(browser=defaultBrowser))

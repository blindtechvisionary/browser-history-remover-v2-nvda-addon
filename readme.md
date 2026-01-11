# Browser History Remover V2

## Overview

**Browser History Remover V2** is a powerful NVDA add-on designed to help you
manage and delete browsing history across multiple web browsers from a single,
accessible interface. Instead of opening each browser individually and
navigating through settings menus, this add-on lets you handle everything
directly from within NVDA.

Version 2 introduces significant improvements, including a configuration
system that remembers your preferences, the ability to backup history before
deletion, and a quick removal feature that lets you clear your default
browser's history with a single keyboard shortcut.

One important capability of this add-on is its ability to clear local history
data even when you are signed into your browser account. Whether you use
Chrome Sync, Firefox Sync, or similar services, this tool effectively removes
local traces of your browsing activity.

* * *

## What is New in Version 2

  * **Configuration Dialog:** A dedicated settings panel where you can customize how the add-on behaves.
  * **History Backup Option:** Choose to save a copy of your browser history before it gets deleted, providing a safety net in case you need to recover something later.
  * **Default Browser Selection:** Set your preferred browser for quick removal operations.
  * **Quick Remove Shortcut:** Press NVDA+Alt+D to instantly delete history from your default browser without opening any dialogs.
  * **Persistent Settings:** Your preferences are saved automatically and remembered between NVDA sessions.
  * **Improved Accessibility:** Better keyboard navigation throughout all dialogs.

* * *

## Supported Browsers

The add-on supports history removal for the following browsers:

### Chromium-Based Browsers

  * Google Chrome
  * Microsoft Edge
  * Opera
  * Brave
  * Vivaldi
  * Chromium

### Firefox-Based Browsers

  * Mozilla Firefox
  * Waterfox
  * Pale Moon
  * Basilisk

### Other Browsers

  * SeaMonkey

**Important:** This add-on removes local browsing history stored on your
computer. It does not delete history that has been synced to cloud services
like Google Account or Firefox Sync. To completely clear your browsing
footprint, you should also manage your sync settings within the browser
itself.

* * *

## Getting Started

### Opening the Main Dialog

There are two ways to open Browser History Remover:

  * Press **NVDA+Alt+B** from anywhere in Windows.
  * Navigate to **NVDA Menu, then Tools, then Browser History Remover**.

### The Main Dialog

When you open the add-on, you will find a straightforward interface:

  * **Browser List:** A list box containing all supported browsers. Use the arrow keys to select the browser whose history you want to delete.
  * **Delete History Button (Alt+D):** Removes the browsing history for the selected browser.
  * **Configurations Button (Alt+C):** Opens the configuration dialog where you can adjust settings.
  * **Exit Button:** Closes the dialog.

* * *

## Configuration Options

Press Alt+C from the main dialog or activate the Configurations button to
access the settings panel.

### Copy Browser History Before Deletion

When this checkbox is enabled, the add-on creates a backup of your browser
history files before deleting them. The backup is saved to:

`C:\Users\YourUsername\Downloads\browser_history_remover\history\BrowserName\`

This feature is useful if you want to preserve a record of your browsing
history or need to recover deleted data later.

### Default Browser for Quick Remove

Select your preferred browser from the dropdown list. This browser will be
used when you press the quick remove shortcut (NVDA+Alt+D), allowing you to
delete history instantly without opening any dialogs.

### Note Panel

The configuration dialog includes an informational note that displays which
browser is set for quick removal. This panel can receive keyboard focus for
screen reader users.

### Saving Your Settings

  * **Save Button (Alt+S):** Saves your configuration and returns to the main dialog.
  * **Cancel Button (Alt+C):** Discards any changes and returns to the main dialog.

Your settings are stored using NVDA's configuration system and persist across
restarts.

* * *

## Keyboard Shortcuts

### Global Shortcuts

Shortcut | Action  
---|---  
NVDA+Alt+B | Open the Browser History Remover dialog  
NVDA+Alt+D | Quick remove history for your default browser  
  
### Main Dialog Shortcuts

Shortcut | Action  
---|---  
Alt+D | Delete history for the selected browser  
Alt+C | Open the configuration dialog  
Ctrl+F | Move focus to the browser list  
Ctrl+Q or Escape | Close the dialog  
  
### Configuration Dialog Shortcuts

Shortcut | Action  
---|---  
Alt+S | Save settings  
Alt+C or Escape | Cancel and close  
  
You can customize the global shortcuts through NVDA Preferences, then Input
Gestures, under the Browser History Remover category.

* * *

## Using Quick Remove

The quick remove feature is designed for users who frequently clear their
browsing history and want to do so as efficiently as possible.

  1. First, open the configuration dialog and select your preferred default browser.
  2. Optionally, enable the backup option if you want copies of your history saved before deletion.
  3. Save your settings.
  4. From now on, simply press NVDA+Alt+D to instantly clear history for that browser.

When you use quick remove, the add-on will speak status messages to keep you
informed:

  * If the browser is not installed, you will hear a message indicating this.
  * If the browser is currently running, you will be asked to close it first.
  * Upon successful deletion, you will hear a confirmation message.

* * *

## How It Works

The add-on locates browser data directories in the Windows AppData folders and
removes files associated with browsing history. Different browsers store their
data in different locations:

### Chromium-Based Browsers

These browsers store data in the Local AppData folder. The add-on targets
files and folders including History, Cookies, Cache, Web Data, Favicons, Top
Sites, Shortcuts, Visited Links, and various cache directories.

### Firefox-Based Browsers

These browsers use profile folders in the Roaming AppData directory. The add-
on removes places.sqlite (which contains history and bookmarks data), form
history, session data, and cache folders.

Before attempting deletion, the add-on checks whether the target browser is
currently running. If it is, you will receive a warning and the deletion will
not proceed until you close the browser.

* * *

## Installation

  1. Download the browserHistoryRemover.nvda-addon file from the distribution source.
  2. Open NVDA and go to Tools, then Add-on store.
  3. Click the Install button and browse to the downloaded file.
  4. Select the file and confirm the installation.
  5. Restart NVDA when prompted to complete the installation.

* * *

Or, You can install the Add-on directly from the NVDA add-on store.

* * *

## Version Information

  * **Add-on Version:** 2.0
  * **Minimum NVDA Version:** 2023.1
  * **Last Tested With:** 2025.1

* * *

## Important Notes and Disclaimers

  * Deleting browser history is a permanent action. Once deleted, the data cannot be recovered through normal means unless you have enabled the backup option.
  * The backup feature copies history-related files before deletion. These backups are stored in your Downloads folder and can accumulate over time. You may want to periodically clean up old backups.
  * This add-on only affects local data. Cloud-synced history remains on remote servers until you delete it through your browser account settings.
  * Always close the target browser before attempting to delete its history. The add-on will warn you if the browser is running, but attempting to delete files while a browser is open may result in errors.
  * The developer assumes no responsibility for data loss or unintended consequences resulting from the use of this add-on. Use it at your own discretion.

* * *

## Troubleshooting

### History deletion fails

Make sure the browser is completely closed, including any background
processes. Some browsers continue running in the background even after you
close the main window. Check your system tray or use Task Manager to ensure
the browser process has ended.

### Browser shows as not installed

The add-on checks standard installation paths. If you have installed a browser
in a non-standard location, the add-on may not detect it. Currently, custom
installation paths are not supported.

### Settings are not saving

Ensure you click the Save button in the configuration dialog. Pressing Escape
or Cancel will discard your changes.

* * *

## Developer Information

**Developed by:** Sujan Rai

**Email:** allcontentnepali@gmail.com

**Community Channel:** <https://t.me/blindtechvisionary>

For bug reports, feature requests, or general feedback, feel free to reach out
through email or join the Telegram channel for updates and discussions.

* * *

## License

This add-on is released under the GNU General Public License version 2,
consistent with the NVDA add-on ecosystem and open source principles.

* * *

**Browser History Remover V2** \- Efficient, accessible browser history
management for NVDA users.


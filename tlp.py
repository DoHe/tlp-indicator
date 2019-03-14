#!/usr/bin/env python3
import os
import re
import subprocess
import time

from gi import require_version

require_version("Gtk", "3.0")
require_version("AppIndicator3", "0.1")

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

THIS = os.path.abspath(os.path.dirname(__file__))
BUNNY_ICON = os.path.join(THIS, "bunny_black.svg")
GREY_BUNNY_ICON = os.path.join(THIS, "bunny_grey.svg")
TURTLE_ICON = os.path.join(THIS, "turtle_black.svg")
GREY_TURTLE_ICON = os.path.join(THIS, "turtle_grey.svg")
TITLE = "TLP Indicator"


TLP_COMMAND = ["pkexec", "tlp"]
TLP_STAT_COMMAND = ["tlp-stat", "-s"]
NOTIFY_COMMAND = ["notify-send"]

METHOD_REGEX = re.compile(r"Mode\s+=\s(?P<mode>\S*)")

INDICATOR = None


def send_message(message, image=None):
    cmd = NOTIFY_COMMAND
    if image:
        cmd = cmd + ["-i", image]
    cmd = cmd + [TITLE, message]
    subprocess.call(cmd)


def tlp(args):
    return subprocess.check_output(TLP_COMMAND + args).decode("utf8")


def tlp_set(set_mode, icon, icon_gray):
    out = tlp([set_mode])
    if "started" in out:
        send_message("Changed to {} mode".format(set_mode), icon)
        if INDICATOR:
            INDICATOR.set_icon(icon_gray)
    else:
        send_message("Error changing to {} mode: {}".format(set_mode, out), icon)


def tlp_stat():
    return subprocess.check_output(TLP_STAT_COMMAND).decode("utf8")


def set_ac(_):
    tlp_set("ac", BUNNY_ICON, GREY_BUNNY_ICON)


def set_bat(_):
    tlp_set("bat", TURTLE_ICON, GREY_TURTLE_ICON)


def mode():
    out = tlp_stat()
    for line in out.splitlines():
        match = METHOD_REGEX.match(line)
        if match:
            return match.group("mode")
    return "Unknown"


def close(response):
    send_message("Quitting... TLP is still running")
    time.sleep(0.1)
    raise SystemExit


def add_menu_item(title, func, menu):
    item = gtk.MenuItem(title)
    menu.append(item)
    item.connect_object("activate", func, title)
    item.show()


if __name__ == "__main__":
    icon = GREY_TURTLE_ICON if mode() == "battery" else GREY_BUNNY_ICON
    indicator = appindicator.Indicator.new(
        "TLP indicator", icon, appindicator.IndicatorCategory.HARDWARE
    )
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

    menu = gtk.Menu()
    add_menu_item("AC", set_ac, menu)
    add_menu_item("Battery", set_bat, menu)
    add_menu_item("Quit", close, menu)
    indicator.set_menu(menu)
    INDICATOR = indicator

    gtk.main()

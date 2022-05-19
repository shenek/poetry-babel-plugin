import gettext
from pathlib import Path

gettext.bindtextdomain("messages", Path(__file__).parent / "locale")
gettext.textdomain("messages")

_ = gettext.gettext


def foo():
    print(_("This is foo function"))

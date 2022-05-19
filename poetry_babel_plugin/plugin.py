import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po
from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.console_events import COMMAND
from cleo.events.event_dispatcher import EventDispatcher
from cleo.io.io import IO
from poetry.console.application import Application
from poetry.console.commands.build import BuildCommand
from poetry.console.commands.install import InstallCommand
from poetry.plugins.application_plugin import ApplicationPlugin


class BabelPlugin(ApplicationPlugin):
    def activate(self, application: Application):
        self._stored_application = application
        application.event_dispatcher.add_listener(COMMAND, self.compile_messages)

    def compile_messages(self, event: ConsoleCommandEvent, event_name: str, dispatcher: EventDispatcher):
        command = event.command
        if not isinstance(command, (BuildCommand, InstallCommand)):
            return
        io = event.io
        io.write_line("Babel plugin is used")
        io.write_line("")

        # Detect file path
        root_dir = self._stored_application.poetry.package.root_dir

        if config := self._stored_application.poetry.pyproject.data.get("tool", {}).get("poetry_babel_plugin"):
            if compile_list := config.get("compile"):
                # Iterate through section list
                for compile_opts in compile_list:
                    if directory := compile_opts.get("directory"):
                        dir_path = root_dir / directory
                        domains = compile_opts.get("domains", ["messages"])
                        locales = compile_opts.get("locales")
                        fuzzy = compile_opts.get("fuzzy", False)
                        for domain in domains:
                            self.compile_message(io, domain, dir_path, locales, fuzzy)

        io.write_line("")

    def compile_message(
        self, io: IO, domain: str, dir_path: Path, locales: Optional[Iterable[str]] = None, fuzzy: bool = False
    ):
        if locales is None:
            # Detect locales by listing the directory
            locale_paths = [(p.name, p) for p in dir_path.glob("*") if p.is_directory()]
        else:
            locale_paths = [(locale, dir_path / locale) for locale in locales]

        input: List[Tuple[str, Path, Path]] = []
        for locale, locale_path in locale_paths:
            po_path = locale_path / "LC_MESSAGES" / f"{domain}.po"
            if po_path.exists():
                mo_path = po_path.parent / f"{domain}.mo"
                input.append((locale, po_path, mo_path))

        for locale, po_file, mo_file in input:
            io.write(f"Compiling <fg=cyan>{locale}</> locale for <fg=cyan>{domain}</> domain... ")
            with po_file.open() as f:
                catalog = read_po(f, locale)

            catalog.fuzzy
            errors = list(catalog.check())

            with mo_file.open("wb") as f:
                write_mo(f, catalog, use_fuzzy=fuzzy)

            if errors:
                io.write_line("<fg=red;options=bold>OK</> (errors)")
            elif catalog.fuzzy and fuzzy:
                io.write_line("<fg=yellow;options=bold>OK</> (fuzzy used)")
            elif catalog.fuzzy and not fuzzy:
                io.write_line("<fg=yellow;options=bold>OK</> (fuzzy skipped)")
            else:
                io.write_line("<fg=green;options=bold>OK</>")

            if io.is_debug() or errors:
                io.write_line(f"<fg=cyan>{po_file}</> -> <fg=cyan>{mo_file}</>")

            for message, error in errors:
                io.write_error_line(f"{message.lineno}: {error}")

# Example how poetry babel plugin can be used

Translation were extracted using
```
pybabel extract example/ -o example/locale/messages.pot
pybabel init -l cs -i example/locale/messages.pot -d example/locale/
```

Then `example/locale/cs/LC_MESSAGES/messages.po` was modified.

During the build/install you can see the plugin output
```
# poetry install
Babel plugin is used

Compiling cs locale for messages domain... OK

Updating dependencies
Resolving dependencies... (0.5s)

Writing lock file

No dependencies to install or update

Installing the current project: example (0.0.0)
```

And you can check that transaltion is used after the install.
```
# LANGUAGE=cs python -m example
Tohle je funkce foo
```

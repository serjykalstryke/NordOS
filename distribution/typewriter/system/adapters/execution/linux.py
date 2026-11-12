import os


def launch(app, arguments):
    if (app.architecture, os.uname().machine) != ("amd64", "x86_64"):
        raise RuntimeError(f"{app.name} does not support this system's architecture.")
    os.execv(app.launcher, [str(app.launcher), *arguments])

#!/usr/bin/python3
import os
import sys

sys.path.insert(0, "/usr/local/lib/typewriter")
from adapters.execution import linux
from library.applications import DEFAULT_APP, STARTUP_APP, applications
from platform_linux.boot import preview_app

registered = applications()
selection = STARTUP_APP.read_text().strip() if STARTUP_APP.is_file() else preview_app() or DEFAULT_APP
app = registered.get(selection)
if app is None or not os.access(app.launcher, os.X_OK):
    sys.exit(f"Writing app unavailable: {selection}")

if app.environment != "linux":
    sys.exit(f"Writing app environment unavailable: {app.environment}")

linux.launch(app, sys.argv[1:])

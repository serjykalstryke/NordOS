from dataclasses import dataclass
from pathlib import Path
import plistlib

DEFAULT_APP = "byok-studio"
BUNDLES = Path("/Applications")
STARTUP_APP = Path("/etc/typewriter/writing-app")


@dataclass(frozen=True)
class WritingApp:
    id: str
    name: str
    summary: str
    environment: str
    architecture: str
    bundle: Path
    launcher: Path
    package: str


def applications(directory=BUNDLES):
    registered = {}
    for bundle in sorted(directory.glob("*.app")):
        contents = bundle / "Contents"
        with (contents / "Info.plist").open("rb") as manifest:
            data = plistlib.load(manifest)
        app = WritingApp(
            id=data["TypewriterID"],
            name=data["CFBundleDisplayName"],
            summary=data["TypewriterSummary"],
            environment=data["TypewriterExecution"]["environment"],
            architecture=data["TypewriterExecution"]["architecture"],
            bundle=bundle,
            launcher=contents / "MacOS" / data["CFBundleExecutable"],
            package=data["TypewriterSource"]["package"],
        )
        if app.id in registered:
            raise RuntimeError(f"Duplicate writing app registration: {app.id}")
        registered[app.id] = app
    return registered

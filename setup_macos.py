"""py2app build configuration for the macOS Quill app.

Usage:
    pip install -e ".[ui,macos]"
    python setup_macos.py py2app
    ./scripts/build_macos.sh          # sign + notarize + DMG

Produces dist/Quill.app.
"""
from setuptools import setup

from quill import __version__

# py2app's finalize_options aborts the build if the distribution carries
# install_requires, which modern setuptools auto-populates from pyproject.toml's
# [project.dependencies]. The .app bundles its own dependencies, so clear it
# right before py2app's own check runs. (Also build with setuptools < 80.)
import py2app.build_app as _py2app_build_app

_orig_py2app_finalize = _py2app_build_app.py2app.finalize_options


def _py2app_finalize_no_install_requires(self):  # type: ignore[no-untyped-def]
    self.distribution.install_requires = None
    _orig_py2app_finalize(self)


_py2app_build_app.py2app.finalize_options = _py2app_finalize_no_install_requires

from quill.platform.macos.shell_integration import (
    APP_DISPLAY_NAME,
    BUNDLE_IDENTIFIER,
    document_types_plist,
)

APP = ["macos_app.py"]

OPTIONS = {
    "argv_emulation": False,
    "packages": ["quill"],
    "includes": ["wx"],
    "plist": {
        "CFBundleName": APP_DISPLAY_NAME,
        "CFBundleDisplayName": APP_DISPLAY_NAME,
        "CFBundleIdentifier": BUNDLE_IDENTIFIER,
        "CFBundleShortVersionString": __version__,
        "CFBundleVersion": __version__,
        "LSMinimumSystemVersion": "12.0",
        "NSHighResolutionCapable": True,
        "CFBundleDocumentTypes": document_types_plist(),
        "NSMicrophoneUsageDescription": "Quill uses the microphone for dictation.",
    },
}

setup(
    app=APP,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)

#!/usr/bin/env bash
# Build, sign, notarize, and package the macOS Quill app.
# Prereqs: pip install -e ".[ui,macos]"; an Apple "Developer ID Application"
# certificate; a notarytool keychain profile (xcrun notarytool store-credentials).
set -euo pipefail

echo "==> Building .app with py2app"
python setup_macos.py py2app

APP="dist/Quill.app"
DMG="dist/Quill.dmg"

if [[ -n "${IDENTITY:-}" ]]; then
  echo "==> Codesigning (hardened runtime, inside-out)"
  # --deep is unreliable: it leaves nested .so/.dylib without a Developer ID
  # signature or secure timestamp, which fails notarization. Sign every nested
  # Mach-O individually first, then the bundle last.
  find "$APP" \( -name "*.so" -o -name "*.dylib" \) -print0 \
    | xargs -0 -P 6 -I{} codesign --force --timestamp --options runtime --sign "$IDENTITY" "{}"
  if [[ -e "$APP/Contents/Frameworks/Python.framework/Versions/3.11/Python" ]]; then
    codesign --force --timestamp --options runtime --sign "$IDENTITY" \
      "$APP/Contents/Frameworks/Python.framework/Versions/3.11/Python"
  fi
  for exe in "$APP/Contents/MacOS/"*; do
    codesign --force --timestamp --options runtime --sign "$IDENTITY" "$exe"
  done
  codesign --force --timestamp --options runtime --sign "$IDENTITY" "$APP"
  codesign --verify --strict --verbose=2 "$APP"
else
  echo "!! IDENTITY not set — skipping codesign (set IDENTITY='Developer ID Application: ...')"
fi

echo "==> Creating DMG"
hdiutil create -volname Quill -srcfolder "$APP" -ov -format UDZO "$DMG"

if [[ -n "${NOTARY_PROFILE:-}" ]]; then
  echo "==> Notarizing"
  xcrun notarytool submit "$DMG" --keychain-profile "$NOTARY_PROFILE" --wait
  echo "==> Stapling"
  xcrun stapler staple "$DMG"
else
  echo "!! NOTARY_PROFILE not set — skipping notarization"
fi

echo "==> Done: $DMG"

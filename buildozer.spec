[app]
title = ऊटिन
package.name = ootin
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

python.version = 3.11.8
hostpython.version = 3.11.8

requirements = python3==3.11.8,kivy,pyjnius

orientation = portrait
fullscreen = 0

# Icon line removed for now — you haven't uploaded icon.png yet.
# Add it back only after icon.png actually exists in the repo root:
# android.icon = icon.png

android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_SCAN,BLUETOOTH_ADVERTISE,BLUETOOTH_CONNECT,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

android.api = 33
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a

android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1

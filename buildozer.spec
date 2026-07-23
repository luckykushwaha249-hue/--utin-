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

# Camel logo (place a 512x512 icon.png in source folder)
android.icon = icon.png

android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_SCAN,BLUETOOTH_ADVERTISE,BLUETOOTH_CONNECT,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

p4a.branch = 2026.5.9

android.api = 33
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a

android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1

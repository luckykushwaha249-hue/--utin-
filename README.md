# ऊटिन – Camel Bluetooth Chat

A simple Bluetooth chat app for two Android devices.  
Features a camel logo (add `icon.png`) and a camel ASCII interface.

## Build
- Add a camel icon (512x512 PNG) as `icon.png` (optional, default is used if missing).
- Use GitHub Actions (fast build) or local Buildozer.

## Usage
1. Pair devices in Android Bluetooth settings.
2. On one phone: tap **Host**.
3. On the other: tap **Refresh**, select the host device, tap **Join**.
4. Send messages.

## Permissions
All required Bluetooth and location permissions are requested at runtime.

## Build locally
```bash
buildozer android debug deploy run

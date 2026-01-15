[app]
title = Amiral Titan 2.0
package.name = amiraltitan
package.domain = org.trading
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 2.0

# Requirements bien propres (sans espaces inutiles)
requirements = python3,kivy==2.3.0,pandas,requests,certifi

orientation = portrait
fullscreen = 0

# On cible les architectures modernes (très important)
android.archs = arm64-v8a, armeabi-v7a

# On fixe les versions pour éviter que GitHub ne cherche partout
android.api = 33
android.minapi = 21
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True

# Permissions
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1

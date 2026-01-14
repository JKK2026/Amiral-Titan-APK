[app]
title = Amiral Titan 2.0
package.name = amiraltitan
package.domain = org.trading
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 2.0

# NOUVEAU : Kivy fait partie des requirements
requirements = python3, kivy, pandas, requests

# Paramètres Android
orientation = portrait
fullscreen = 0
android.arch = armeabi-v7a

# NOUVEAU : Ajout de la permission internet
android.permissions = INTERNET

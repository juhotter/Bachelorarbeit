# readme

## REFERENCES:
### https://github.com/mitmproxy/android-unpinner
### https://github.com/shroudedcode/apk-mitm
### https://github.com/sensepost/objection

# Automatisiertes Herunterladen von APKS
`./eval.py download --fromfile FILENAME `
  > es muss sich ein .txt File im selben Ordner befinden, wo Packagenamen aufgelistet sind.


# Auswertung eines TextFiles welches JSON Lines enthält:
`./eval.py evaluate`

# Wendet eine Methode auf eine Bestimmte APK an:
`./eval.py run --method METHODENNAME NAME.APK `
> choose between:
- apkmitm
- objection
- frida
- none,
- rooted 

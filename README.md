# readme



# Automatisiertes Herunterladen von APKS \n
./eval.py download --fromfile FILENAME \n
  es muss sich ein .txt File im selben Ordner befinden, wo Packagenamen aufgeslistet sind. \n


# Auswertung eines TextFiles welches JSON Lines enthält:\n
./eval.py evaluate \n

# Wendet eine Methode auf eine Bestimmte APK an: \n
./eval.py run --method METHODENNAME NAME.APK \n
  choose between -> apkmitm,objection,frida,none,rooted \n

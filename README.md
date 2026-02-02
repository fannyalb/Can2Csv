# Can2Csv
Kleines Python-Projekt um Can-Daten in CSV umzuwandeln

## Installation
* Zip-Datei vom letzten Release downloaden: https://github.com/fannyalb/Can2Csv/releases/latest
* Entpacken 
* `install.bat` ausfuehren

## Programm starten
* `runCan2Csv.bat` ausfuehren. Es oeffnet sich das Applikationsfenster ![Applikationsfenster](resources/applikationsfenster.png-)
 
### Verwendung

### "DBC-File"
DBC-Datei auswaehlen, die zum decodieren der MDF/MF4-Dateien verwendet werden soll

### "MF4-Datei"/"oder Ordner
Unkonvertierte (rohe) MF4-Datei, oder Ordner mit MF4-Dateien, die dann als
CSV exportiert werden sollen

### "Export Ordner"
Ordner, in dem die CSV-Dateien gespeichert werden

### Export-Dateiname
Praefix, der CSV-Dateien, die erstellt werden

### "CSV Exportieren"
Die Signale werden pro Channelgruppe in eine separate CSV-Datei geschrieben
Die selbst berechneten Werte kommen in die eine Datei mit dem Suffix `CustomValues`

## Berechnete Werte ("Custom Values")
#### Schlittenwagen
* `sw_strecke_delta_m` :
  * Zurueckgelegte Strecke in letztem Zeitintervall des Schlittenwagens (Aus General_LD_TrommelSpeed und Trommeldurchmesser 0.5 m)
* `sw_strecke_cumsum_m`:
  * Aufsummierte Streckendeltas -> Zurueckgelegte Gesamtstrecke ist der Wert der letzten Zelle

#### Laufwagen
##### Gewichte
* `lw_weight_mov_current_kg`: Gewicht, das in diesem Zeitintervall gemessen wurde, falls eine Bewegung (> 50 rpm und Zeit > 15 s) stattfindet (aus General_LD_MeassuredWeight, MotorDrive_LD_ActualSpeed)
* `lw_weight_mov_cumsum_kg`: `lw_weight_mov_current_kg` aufsummiert
* `lw_weight_kg`: Alle gemessenen Gewichte (1x pro unterschiedlicher Messwert) aufsummiert (General_LD_MeassuredWeight)
* 
##### Zuzug/Auslass
* `lw_rope_delta_m`: Zurueckgelegte Strecke des Lastseils im letzten Zeitintervall (aus MotorLift_LD_ActualSpeed mit Uebersetzung i = 60 und Trommeldruchmesser 0.28 m)
* `lw_rope_pull_delta_m`: Nur positive Werte von lw_rope_delta_m
* `lw_rope_release_delta_m`: Nur negative Werte von lw_rope_delta_m
* `lw_rope_cumsum_m`: Absolutwerte von lw_rope_delta_m aufsummiert
* `lw_rope_pull_cumsum_m`: `lw_rope_pull_delta_m` aufsummiert
* `lw_rope_release_cumsum_m`: `lw_rope_release_delta_m` aufsummiert

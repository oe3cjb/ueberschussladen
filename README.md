﻿# Überschussladen für Fronius WR mit Smartmeter und go e-charger

einfaches Python Script, das auf einem Raspberry läuft, um Überschussladen zu relaisieren.
Ausgelesen wird eine Fronius Smartmeter via Fronius Wechselrichter Gen24, gesteuert wird eine go e-charger Wallbox.
Getestet und verwendet wird das ganze mit einem Tesla Model 3 - ob es bei anderen Fahrzeugen auch funktioniert, ist nicht gesichert.

BENUTZUNG AUF EIGENE GEFAHR - OHNE JEGLICHER GEWÄHRLEISTUNG!

Ab 1380W (6A bei 230V~ einpahsig) wird das Laden gestartet und wenn genügend Leistung vorhanden ist,
in 1A - Schritten gesteigert. Sind 16A erreicht, wird auf dreiphasig umgeschalten und von dort wieder in 1A-Schritten erhöht.
Bei abnehmender PV-Leistung geht es wieder in 1A Schritten retour, bis das Minimum erreicht wird und die Ladung stoppt.

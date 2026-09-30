# OfflineProof

PrÃ¼ft festgelegte Browser-Erwartungen wÃ¤hrend Onlinebetrieb, Offlinebetrieb, Offline-Neuladen und Wiederverbindung. So werden Datenverlust und doppelte EintrÃ¤ge sichtbar.

Erste nutzbare Version 0.1.0. Python ab 3.11, MIT-Lizenz. VollstÃ¤ndige Schnittstellen und Beispiele stehen in der [englischen README](README.md).

## Installation

Im geklonten Repo eine virtuelle Umgebung anlegen:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

## Beispiel

```sh
offlineproof run examples/scenario.json --out outputs/check
```

Berichte entstehen als `report.json` und `report.html` im gewÃ¤hlten Ausgabeordner. RÃ¼ckgabecode 0 bedeutet bestanden, 1 bedeutet Befunde, 2 einen Eingabe- oder Laufzeitfehler. Die Beispieldaten sind kÃ¼nstlich.

Die Netzwerksimulation gilt fÃ¼r den Browser. Eine Backend-Zustellung wird daraus nicht abgeleitet. Alle vier Phasen brauchen eigene Erwartungen. Nach erfolgreicher PrÃ¼fung wird der Zustand nach einer kurzen Wartezeit erneut geprÃ¼ft. Jeder Lauf beginnt mit leerem Browserspeicher. Fremde UrsprÃ¼nge und WebSockets sind gesperrt.

Tests: `python -m pytest -q`. FÃ¼r Docker- und Browsertests gelten die zusÃ¤tzlichen Voraussetzungen in der englischen README. Das Werkzeug lÃ¤dt keine Berichte hoch und ruft keine Modell-API auf.

Chromium läuft mit aktivierter Sandbox. Für `localhost` werden IPv4 und IPv6 berücksichtigt. Alle Erwartungen werden gemeinsam in Abständen von 25 Millisekunden geprüft. Sie müssen während der festgelegten Stabilitätsdauer gemeinsam erfüllt bleiben. Dafür sind CSS-Selektoren im Hauptdokument erforderlich. Änderungen zwischen den Stichproben können unbemerkt bleiben. Ein unerreichbarer Server ergibt Rückgabecode 2.

# OfflineProof

Prüft festgelegte Browser-Erwartungen während Onlinebetrieb, Offlinebetrieb, Offline-Neuladen und Wiederverbindung. So werden Datenverlust und doppelte Einträge sichtbar.

Erste nutzbare Version 0.1.0. Python ab 3.11, MIT-Lizenz. Vollständige Schnittstellen und Beispiele stehen in der [englischen README](README.md).

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

Berichte entstehen als `report.json` und `report.html` im gewählten Ausgabeordner. Rückgabecode 0 bedeutet bestanden, 1 bedeutet Befunde, 2 einen Eingabe- oder Laufzeitfehler. Die Beispieldaten sind künstlich.

Die Netzwerksimulation gilt für den Browser. Eine Backend-Zustellung wird daraus nicht abgeleitet. Alle vier Phasen brauchen eigene Erwartungen. Nach erfolgreicher Prüfung wird der Zustand nach einer kurzen Wartezeit erneut geprüft. Jeder Lauf beginnt mit leerem Browserspeicher. Fremde Ursprünge und WebSockets sind gesperrt.

Tests: `python -m pytest -q`. Für Docker- und Browsertests gelten die zusätzlichen Voraussetzungen in der englischen README. Das Werkzeug lädt keine Berichte hoch und ruft keine Modell-API auf.

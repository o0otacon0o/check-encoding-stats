# Dateikodierungs-Analyse Tool - check_encoding_stats

-----

## Übersicht

Dieses Python-Skript ist ein vielseitiges Tool zur **Analyse der Zeichenkodierung von Dateien** innerhalb eines angegebenen Verzeichnisses und all seiner Unterverzeichnisse. Eine seiner Kernfunktionen ist die Fähigkeit, **auch den Inhalt von ZIP- und WAR-Archiven zu prüfen**, was es besonders nützlich macht, um die Kodierung von Code, Konfigurationsdateien oder anderen Ressourcen zu überprüfen, die in Archiven gespeichert sind.

Das Tool erstellt einen detaillierten Bericht, der für jede analysierte Datei die erkannte Kodierung und die Zuverlässigkeit dieser Erkennung auflistet. Am Ende des Berichts findest du eine statistische Zusammenfassung, die dir einen schnellen Überblick über die Dateitypen und die in ihnen gefundenen Kodierungen gibt.

-----

## Funktionen

  * **Rekursive Verzeichnisprüfung:** Analysiert alle Dateien in einem Ausgangsverzeichnis und dessen Unterordnern.
  * **ZIP- & WAR-Archiv-Inspektion:** Scannt den Inhalt von `.zip`- und `.war`-Dateien und prüft die Kodierung der einzelnen darin enthaltenen Dateien.
  * **Intelligente Kodierungserkennung:** Nutzt die robuste `chardet`-Bibliothek, um die wahrscheinliche Zeichenkodierung zu identifizieren.
  * **Zuverlässigkeitsbewertung:** Zeigt an, wie sicher das Tool bei der Erkennung der Kodierung ist, und hebt Ergebnisse mit geringer Zuverlässigkeit hervor.
  * **Detaillierte Protokollierung:** Erstellt eine lesbare Log-Datei mit umfassenden Informationen zu jeder geprüften Datei und jedem Element innerhalb von Archiven.
  * **Statistischer Bericht:** Bietet eine übersichtliche Zusammenfassung der Dateitypen und ihrer jeweiligen Kodierungsverteilung im gesamten Scan-Bereich.

-----

## Installation

Um das Skript nutzen zu können, benötigst du **Python 3**. Falls noch nicht geschehen, installiere bitte die notwendige Bibliothek `chardet` über pip:

```bash
pip install chardet
```

-----

## Nutzung

1.  **Speichere das Skript:** Lade den bereitgestellten Python-Code herunter und speichere ihn als beispielsweise `check_encoding_deep.py` in einem beliebigen Verzeichnis auf deinem Computer.

2.  **Führe das Skript aus:** Öffne dein Terminal oder deine Kommandozeile, navigiere zu dem Speicherort, an dem du das Skript gespeichert hast, und führe es mit dem Pfad zum zu analysierenden Verzeichnis aus:

    ```bash
    python check_encoding_deep.py <pfad_zum_verzeichnis> [optionen]
    ```

    **Beispiele:**

      * **Unter Linux/macOS:**
        ```bash
        python check_encoding_deep.py ~/Dokumente/MeinSoftwareprojekt
        ```
      * **Unter Windows:**
        ```bash
        python check_encoding_deep.py C:\Users\Manuel\Code\LegacySystem
        ```

### Kommandozeilen-Optionen

  * `<pfad_zum_verzeichnis>` (obligatorisch):
    Dies ist der absolute oder relative Pfad zu dem Verzeichnis, dessen Dateien und Archive du analysieren möchtest.

  * `--min_confidence <wert>` (optional):
    Ein Wert zwischen `0.0` und `1.0`, der die Schwelle für die Zuverlässigkeit der Kodierungserkennung festlegt. Liegt die Konfidenz unter diesem Wert, wird die Erkennung im Bericht als "geringe Zuverlässigkeit" markiert.

      * **Standardwert:** `0.9` (90% Konfidenz)

  * `--log_file <dateiname>` (optional):
    Definiert den Namen der Ausgabedatei für den ausführlichen Bericht. Die Datei wird im selben Verzeichnis wie das Skript erstellt.

      * **Standardwert:** `encoding_report_deep.txt`

    **Beispiel für die Verwendung von Optionen:**

    ```bash
    python check_encoding_deep.py /srv/data/archive_dump --min_confidence 0.75 --log_file archiv_scan_bericht.txt
    ```

-----

## Der Analysebericht

Das Skript generiert eine detaillierte Textdatei (standardmäßig `encoding_report_deep.txt`), die aus zwei Hauptabschnitten besteht:

### 1\. Detaillierte Dateianalyse

Dieser Abschnitt listet jede einzelne geprüfte Datei auf – sowohl die direkt im Dateisystem gefundenen als auch die aus ZIP- oder WAR-Archiven extrahierten. Für jede Datei werden folgende Informationen bereitgestellt:

  * **Dateipfad:** Der vollständige Pfad zur Datei. Bei Dateien innerhalb von Archiven wird das Archiv und der interne Pfad klar angezeigt (z.B. `Archiv.zip -> interner/pfad/zur/datei.txt`).
  * **Dateityp:** Die erkannte Dateierweiterung (z.B. `.java`, `.xml`, `.txt`).
  * **Kodierung:** Die von `chardet` erkannte Zeichenkodierung (z.B. `UTF-8`, `Windows-1252`, `ascii`).
  * **Zuverlässigkeit:** Ein numerischer Wert (`0.0` bis `1.0`), der die Konfidenz der Erkennung angibt.
  * **Warnhinweis:** Wenn die Zuverlässigkeit unter dem mit `--min_confidence` festgelegten Wert liegt.

**Beispielausschnitt aus dem Bericht:**

```
Datei: /home/user/projekt/config/settings.properties
  Typ: .properties
  Kodierung: ISO-8859-1
  Zuverlässigkeit: 0.98

Datei (in Archiv): /home/user/deployments/web_app.war -> WEB-INF/classes/messages.properties
  Typ: .properties
  Kodierung: UTF-8
  Zuverlässigkeit: 0.99
```

### 2\. Zusammenfassung der Kodierungsstatistik

Am Ende des Berichts findest du eine konsolidierte Übersicht. Sie zeigt die **Gesamtanzahl aller verarbeiteten Dateien** (einschließlich der Inhalte von Archiven) und die Anzahl der Dateien, bei denen die Kodierung mit geringer Zuverlässigkeit erkannt wurde. Anschließend werden die Ergebnisse nach Dateityp gruppiert, und für jeden Typ wird aufgeführt, wie viele Dateien welche spezifische Kodierung aufweisen.

**Beispielausschnitt aus dem Statistikbericht:**

```
================================================================================
ZUSAMMENFASSUNG DER KODIERUNGSSTATISTIK
================================================================================

Gesamtanzahl der verarbeiteten Dateien (inkl. Archivinhalte): 750
Dateien mit geringer Zuverlässigkeit (<0.9): 8

Dateityp: '.java' (Gesamt: 300 Dateien)
  - UTF-8: 295 Dateien
  - ISO-8859-1: 5 Dateien

Dateityp: '.xml' (Gesamt: 120 Dateien)
  - UTF-8: 118 Dateien
  - ascii: 2 Dateien
```

import os
import argparse
import chardet
from collections import defaultdict
import zipfile
import datetime

# Funktion zur Erkennung der Kodierung
def detect_encoding(data_bytes):
    """
    Erkennt die wahrscheinliche Zeichenkodierung einer Menge von Bytes.
    Erwartet Rohdaten (Bytes), keine Dateipfade.
    """
    if not data_bytes:
        return None, 0.0 # Leere Daten können nicht erkannt werden

    result = chardet.detect(data_bytes)
    encoding = result['encoding']
    confidence = result['confidence']
    return encoding, confidence

# Funktion zur Ermittlung der Dateierweiterung
def get_file_extension(filename):
    """
    Gibt die Dateierweiterung zurück (z.B. '.txt', '.py').
    Gibt 'no_extension' zurück, wenn keine Erweiterung vorhanden ist.
    """
    _, ext = os.path.splitext(filename)
    # Entferne führenden Punkt und konvertiere zu Kleinbuchstaben für Konsistenz
    return ext.lower().lstrip('.') if ext else 'no_extension'

def process_file(file_path, display_name, min_confidence, stats, log_f, is_archive_content=False):
    """
    Verarbeitet eine einzelne Datei (oder eine Datei innerhalb eines Archivs)
    und protokolliert ihre Kodierung.
    """
    global total_processed_files, total_unreliable_encodings

    total_processed_files += 1
    file_ext = get_file_extension(os.path.basename(display_name)) # Use base name for extension

    try:
        # Hier lesen wir die Datei direkt von der Platte
        # Für Archivinhalte wird diese Funktion mit bereits gelesenen Bytes aufgerufen
        with open(file_path, 'rb') as f:
            raw_data = f.read(100000) # Lese die ersten 100KB
    except Exception as e:
        encoding, confidence = f"Fehler beim Lesen der Datei: {e}", 0.0
        raw_data = b'' # Setze leere Daten, damit chardet nicht versucht zu analysieren
        
    encoding, confidence = detect_encoding(raw_data)

    log_f.write(f"Datei: {display_name}\n")
    log_f.write(f"  Typ: .{file_ext}\n")
    log_f.write(f"  Kodierung: {encoding or 'Unbekannt'}\n")
    log_f.write(f"  Zuverlässigkeit: {confidence:.2f}\n")
    
    if confidence < min_confidence and isinstance(encoding, str) and not encoding.startswith("Fehler"):
        log_f.write(f"  ---> Achtung: Geringe Zuverlässigkeit der Kodierung erkannt!\n")
        total_unreliable_encodings += 1
    
    log_f.write("\n")

    # Statistik aktualisieren
    stats[file_ext]['total_files'] += 1
    if encoding:
        stats[file_ext][encoding] += 1
    else:
        stats[file_ext]['Unbekannt/Fehler'] += 1


def process_archive_content(archive_path, file_in_archive_name, min_confidence, stats, log_f, zip_file_obj):
    """
    Verarbeitet eine einzelne Datei *innerhalb* eines ZIP/WAR-Archivs.
    """
    global total_processed_files, total_unreliable_encodings

    total_processed_files += 1
    file_ext = get_file_extension(file_in_archive_name)

    # Die Anzeige im Log, um klar zu machen, dass es sich um eine Archivdatei handelt
    display_name = f"{archive_path} -> {file_in_archive_name}"

    try:
        # Öffne die Datei innerhalb des Archivs
        with zip_file_obj.open(file_in_archive_name, 'r') as member_file:
            # Lese die ersten 100KB des Archivmembers
            raw_data = member_file.read(100000)
            
        encoding, confidence = detect_encoding(raw_data)

    except Exception as e:
        encoding, confidence = f"Fehler beim Lesen des Archivinhalts '{file_in_archive_name}': {e}", 0.0

    log_f.write(f"Datei (in Archiv): {display_name}\n")
    log_f.write(f"  Typ: .{file_ext}\n")
    log_f.write(f"  Kodierung: {encoding or 'Unbekannt'}\n")
    log_f.write(f"  Zuverlässigkeit: {confidence:.2f}\n")
    
    if confidence < min_confidence and isinstance(encoding, str) and not encoding.startswith("Fehler"):
        log_f.write(f"  ---> Achtung: Geringe Zuverlässigkeit der Kodierung erkannt!\n")
        total_unreliable_encodings += 1
    
    log_f.write("\n")

    # Statistik aktualisieren
    stats[file_ext]['total_files'] += 1
    if encoding:
        stats[file_ext][encoding] += 1
    else:
        stats[file_ext]['Unbekannt/Fehler'] += 1

# Globale Zähler (für die Zusammenfassung)
total_processed_files = 0
total_unreliable_encodings = 0

def main():
    global total_processed_files, total_unreliable_encodings

    parser = argparse.ArgumentParser(description="Prüft die Dateikodierung von Dateien in einem Verzeichnis, einschließlich ZIP/WAR-Archiven, und erstellt eine Statistik.")
    parser.add_argument("directory_path", help="Der Pfad zum Verzeichnis, das die zu prüfenden Dateien enthält.")
    parser.add_argument("--min_confidence", type=float, default=0.9,
                        help="Mindestzuverlässigkeit (0.0-1.0), um eine Kodierung zu akzeptieren. Standard: 0.9")
    parser.add_argument("--log_file", type=str, default="encoding_report_deep.txt",
                        help="Name der Log-Datei für den Statistikbericht. Standard: encoding_report_deep.txt")

    args = parser.parse_args()
    target_directory = args.directory_path
    min_confidence = args.min_confidence
    log_file_name = args.log_file

    if not os.path.isdir(target_directory):
        print(f"Fehler: '{target_directory}' ist kein gültiges Verzeichnis.")
        return

    # Dictionary, um Statistiken zu speichern:
    # { 'file_extension': { 'encoding_name': count, 'total_files': count } }
    stats = defaultdict(lambda: defaultdict(int))
    
    print(f"Starte tiefe Kodierungsanalyse im Verzeichnis: '{target_directory}'")
    print(f"Der detaillierte Bericht wird in '{log_file_name}' gespeichert.")
    print("-" * 50)

    # Erstelle/Öffne die Log-Datei
    with open(log_file_name, 'w', encoding='utf-8') as log_f:
        log_f.write(f"Kodierungsanalysebericht für: '{target_directory}'\n")
        log_f.write(f"Datum: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.write(f"Mindest-Zuverlässigkeit für Erkennung: {min_confidence}\n")
        log_f.write("-" * 80 + "\n\n")
        log_f.write("Detaillierte Dateianalyse:\n")
        log_f.write("--------------------------\n")

        for root, _, files in os.walk(target_directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                
                # Überspringe Verzeichnisse und symbolische Links
                if not os.path.isfile(file_path) or os.path.islink(file_path):
                    continue

                # Prüfe, ob es sich um ein Archiv handelt
                if filename.lower().endswith(('.zip', '.war')):
                    log_f.write(f"Verarbeite Archiv: {file_path}\n")
                    log_f.write("--------------------------------\n")
                    try:
                        # Öffne das ZIP/WAR-Archiv
                        with zipfile.ZipFile(file_path, 'r') as zf:
                            for member in zf.infolist():
                                # Wir interessieren uns nur für echte Dateien, nicht für Verzeichnisse im Archiv
                                if not member.is_dir():
                                    process_archive_content(file_path, member.filename, min_confidence, stats, log_f, zf)
                    except zipfile.BadZipFile:
                        log_f.write(f"  FEHLER: '{file_path}' ist kein gültiges ZIP/WAR-Archiv oder ist beschädigt.\n\n")
                        stats['.zip/.war_error']['total_files'] += 1
                        stats['.zip/.war_error']['Fehler_Lesen'] += 1
                    except Exception as e:
                        log_f.write(f"  FEHLER beim Verarbeiten von '{file_path}': {e}\n\n")
                        stats['.zip/.war_error']['total_files'] += 1
                        stats['.zip/.war_error']['Fehler_Unbekannt'] += 1
                    log_f.write("--------------------------------\n\n")
                else:
                    # Normale Datei verarbeiten
                    process_file(file_path, file_path, min_confidence, stats, log_f)

        # Generiere den Statistikbericht
        log_f.write("\n" + "=" * 80 + "\n")
        log_f.write("ZUSAMMENFASSUNG DER KODIERUNGSSTATISTIK\n")
        log_f.write("=" * 80 + "\n\n")

        log_f.write(f"Gesamtanzahl der verarbeiteten Dateien (inkl. Archivinhalte): {total_processed_files}\n")
        log_f.write(f"Dateien mit geringer Zuverlässigkeit (<{min_confidence:.1f}): {total_unreliable_encodings}\n\n")

        for ext, ext_stats in sorted(stats.items()):
            log_f.write(f"Dateityp: '.{ext}' (Gesamt: {ext_stats['total_files']} Dateien)\n")
            for encoding_name, count in sorted(ext_stats.items()):
                if encoding_name != 'total_files':
                    log_f.write(f"  - {encoding_name}: {count} Dateien\n")
            log_f.write("\n")
        
        print(f"\nAnalyse abgeschlossen. Der vollständige Bericht befindet sich in '{log_file_name}'.")

if __name__ == "__main__":
    main()
# pwrshell cmds

## Copy and edit this variable

```powershell
set $SEARCH_STR=""
```

### **1. Alle Dateien auf allen verfügbaren Laufwerken finden, die einen bestimmten String im Namen haben**

```powershell
Get-PSDrive -PSProvider 'FileSystem' | ForEach-Object {
    Get-ChildItem -Path "$($_.Root)\*" -Recurse -ErrorAction SilentlyContinue -Force |
    Where-Object { $_.Name -like "*$SEARCH_STR*" } |
    Select-Object FullName
}
```

_Beschreibung:_ Dieser Befehl durchsucht alle Dateisystemlaufwerke nach Dateien, deren Namen den angegebenen String enthalten. Fehler werden unterdrückt, sodass die Suche auch bei Problemen fortgesetzt wird.

---

### **2. Alle Dateien finden, die einen bestimmten String im Inhalt haben**

```powershell
Get-ChildItem -Path 'C:\' -Recurse -File -ErrorAction SilentlyContinue -Force |
Select-String -Pattern "$SEARCH_STR" -ErrorAction SilentlyContinue |
Select-Object Path
```

_Beschreibung:_ Dieser Befehl durchsucht alle Dateien unter `C:\` nach solchen, die den angegebenen String im Inhalt enthalten. Fehler werden stillschweigend behandelt, um die Verarbeitung fortzusetzen.

---

### **3. Alle Verzeichnisse rekursiv finden, die einen bestimmten String im Namen haben**

```powershell
Get-ChildItem -Path 'C:\' -Recurse -Directory -ErrorAction SilentlyContinue -Force |
Where-Object { $_.Name -like "*$SEARCH_STR*" } |
Select-Object FullName
```

_Beschreibung:_ Dieser Befehl durchsucht alle Verzeichnisse unter `C:\` rekursiv nach solchen, deren Namen den angegebenen String enthalten. Fehler werden unterdrückt, um die Suche nicht zu unterbrechen.

---

**Zusätzliche nützliche Befehle:**

---

### **4. Alle leeren Verzeichnisse finden und löschen**

```powershell
Get-ChildItem -Path 'C:\' -Recurse -Directory -ErrorAction SilentlyContinue -Force |
Where-Object { @(Get-ChildItem $_.FullName -Force -ErrorAction SilentlyContinue).Count -eq 0 } |
Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
```

_Beschreibung:_ Dieser Befehl findet alle leeren Verzeichnisse unter `C:\` und löscht sie. Fehler werden stillschweigend behandelt.

---

### **5. Laufende Prozesse nach Speicherverbrauch sortiert auflisten**

```powershell
Get-Process | Sort-Object -Property WS -Descending | Select-Object -First 10
```

_Beschreibung:_ Zeigt die Top 10 Prozesse an, die am meisten Arbeitsspeicher verbrauchen.

---

### **6. Alle großen Dateien über einer bestimmten Größe finden (z.B. über 100MB)**

```powershell
Get-ChildItem -Path 'C:\' -Recurse -File -ErrorAction SilentlyContinue -Force |
Where-Object { $_.Length -gt 100MB } |
Select-Object FullName, @{Name="SizeMB";Expression={$_.Length / 1MB -as [int]}}
```

_Beschreibung:_ Sucht nach Dateien über 100MB unter `C:\` und listet ihre Pfade und Größen in MB auf.

---

### **7. Liste installierter Programme exportieren**

```powershell
Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue |
Select-Object DisplayName, DisplayVersion, Publisher, InstallDate |
Export-Csv -Path "InstallierteProgramme.csv" -NoTypeInformation
```

_Beschreibung:_ Ruft eine Liste der installierten Programme ab und exportiert sie in eine CSV-Datei namens "InstallierteProgramme.csv".

---

### **8. Eine Datei in Echtzeit auf Änderungen überwachen**

```powershell
$Datei = 'C:\Pfad\zur\Ihrer\Datei.txt'
Get-Content $Datei -Wait
```

_Beschreibung:_ Zeigt den Inhalt einer Datei an und aktualisiert in Echtzeit, sobald Änderungen vorgenommen werden.

---

### **9. Ein Verzeichnis sichern und bestimmte Dateitypen ausschließen**

```powershell
robocopy "C:\Quelle" "D:\Backup" /E /XD *.tmp *.log
```

_Beschreibung:_ Kopiert alle Dateien und Unterverzeichnisse von `C:\Quelle` nach `D:\Backup`, schließt aber Dateien mit den Endungen `.tmp` und `.log` aus.

---

### **10. Prüfen, ob ein Port auf einem entfernten Rechner offen ist**

```powershell
Test-NetConnection -ComputerName RemoteHostName -Port 80
```

_Beschreibung:_ Testet die Konnektivität zu einem Remote-Host auf einem bestimmten Port (z.B. Port 80).

---

**Hinweise:**

- Ersetzen Sie `"IhrString"` und `"IhrSuchString"` durch den tatsächlichen String, nach dem Sie suchen möchten.
- Passen Sie Pfade wie `'C:\'` oder `'C:\Pfad\zur\Ihrer\Datei.txt'` entsprechend Ihrer Systemumgebung an.
- Der Parameter `-ErrorAction SilentlyContinue` unterdrückt Fehlermeldungen und setzt die Ausführung fort.
- Seien Sie vorsichtig beim Ausführen von Befehlen, die Dateien löschen oder verändern (z.B. leere Verzeichnisse löschen).
- Verwenden Sie `-Force`, um auch versteckte und Systemdateien einzuschließen.

## Um laufende PowerShell-Prozesse anzuzeigen, kannst du das `Get-Process`-Cmdlet verwenden, um eine Liste aller aktiven Prozesse zu erhalten. Du kannst speziell nach PowerShell-Prozessen filtern, indem du nach dem Prozessnamen "powershell" oder "pwsh" (für PowerShell Core) suchst. Hier sind einige Möglichkeiten, wie du dies tun kannst

1. **Alle Prozesse anzeigen**:

   ```powershell
   Get-Process
   ```

2. **Nur PowerShell-Prozesse anzeigen**:

   ```powershell
   Get-Process -Name powershell
   ```

   Für PowerShell Core:

   ```powershell
   Get-Process -Name pwsh
   ```

3. **Detaillierte Informationen zu PowerShell-Prozessen anzeigen**:

   ```powershell
   Get-Process -Name powershell | Format-List *
   ```

   Für PowerShell Core:

   ```powershell
   Get-Process -Name pwsh | Format-List *
   ```

4. **Beenden eines bestimmten PowerShell-Prozesses**:
   Du kannst einen bestimmten PowerShell-Prozess anhand seiner Prozess-ID (PID) beenden. Zum Beispiel:

   ```powershell
   Stop-Process -Id <Prozess-ID>
   ```

   Um die Prozess-ID zu finden, kannst du `Get-Process` verwenden:

   ```powershell
   Get-Process -Name powershell
   ```

   Dann wähle die PID aus der Liste aus und benutze `Stop-Process`, um den Prozess zu beenden.

Hier ist ein vollständiges Beispiel, um laufende PowerShell-Prozesse anzuzeigen und detaillierte Informationen zu einem bestimmten Prozess zu erhalten:

```powershell
# Zeige alle laufenden PowerShell-Prozesse an
Get-Process -Name powershell

# Zeige detaillierte Informationen zu einem bestimmten PowerShell-Prozess an (zum Beispiel dem ersten in der Liste)
Get-Process -Name powershell | Select-Object -First 1 | Format-List *
```

### Kills all processes found under the searched Name

```powershell
Get-Process -Name python | ForEach-Object {
    # List the process name and PID
    Write-Host "Found process: Name = $($_.ProcessName), PID = $($_.Id)"

    # Stop the process
    Stop-Process -Id $_.Id -Force

    # Confirm the process has been stopped
    Write-Host "Stopped process with PID $($_.Id)"
}
```

### Quick start python core ai server

```powershell
Set-Location -Path "D:\server\app\backend\" && .\.venv\Scripts\activate && fastapi dev "app\main.py"
```

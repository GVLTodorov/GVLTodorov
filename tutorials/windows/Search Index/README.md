Fix Windows Search accumulating thousands of individually excluded folders (via `CrawlScopeManager`) and reset it back to defaults.

Check current excluded/included rule count:
```powershell
(Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Windows Search\CrawlScopeManager\Windows\SystemIndex\WorkingSetRules').Count
```

Deleting the registry keys directly, or stopping the service and deleting the index database (`C:\ProgramData\Microsoft\Search\Data\Applications\Windows`), does **not** work — the service resyncs `WorkingSetRules` from its own internal state on next start, or detects the missing files as corruption and can get permanently stuck in `StartPending`.

What actually works — reset the setup flag and let Windows Search redo its own first-run setup:

```powershell
# Run as Administrator
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows Search' -Name 'SetupCompletedSuccessfully' -Value 0 -Type DWord
sc.exe stop WSearch
sc.exe start WSearch
```

Service comes back up clean (no stuck `StartPending`), `SetupCompletedSuccessfully` flips back to `1` on its own, and `WorkingSetRules` drops from thousands of entries down to the normal Windows default set (~20-40).

Note: use `sc.exe stop`/`sc.exe start`, not the `Stop-Service`/`Start-Service` cmdlets — those can report a failure/timeout on this service even when it actually stops and starts fine.

After the reset, indexing will restart from scratch for whatever locations are in scope (Classic mode: Documents/Pictures/Music/Desktop) — expect a temporary CPU/disk bump until it catches up.

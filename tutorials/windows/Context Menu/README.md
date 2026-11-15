## 🖥️ Windows 10

Set "Old" Explorer Context Menu as Default

```reg add "HKEY_CURRENT_USER\SOFTWARE\CLASSES\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /ve /f```

Remove Explorer "Command Bar"

```reg add "HKCU\Software\Classes\CLSID\{d93ed569-3b3e-4bff-8355-3c44f6a52bb5}\InprocServer32" /f /ve```

Restart Windows Explorer. (Applies the above settings without needing a reboot)

```taskkill /f /im explorer.exe```

```start explorer.exe```

## 🖥️ Windows 11

Restore Win 11 Explorer Context Menu

```reg.exe delete "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" /f```

Restore Win 11 Explorer Command Bar

```reg.exe delete "HKCU\Software\Classes\CLSID\{d93ed569-3b3e-4bff-8355-3c44f6a52bb5}" /f```

Restart Windows Explorer. (Applies the above settings without needing a reboot)

```taskkill /f /im explorer.exe```

```start explorer.exe```

## 🖥️ Windows 11 November 2026

The late October 2026 update (KB5127936) brought back the short context menu, and the single registry key above stopped working. You now need a second key as well. Tested on Windows 11 26H2, build 26300.9818. The change applies only to the current user, and you don't need admin rights.

Set "Old" Explorer Context Menu as Default (both commands are required)

```reg add "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /ve /f```

```reg add "HKCU\Software\Classes\CLSID\{51668040-5e31-4023-bbe3-149163bd80f1}\InprocServer32" /ve /f```

Restore Win 11 Explorer Context Menu (if you get "key not found", the key is already gone)

```reg delete "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" /f```

```reg delete "HKCU\Software\Classes\CLSID\{51668040-5e31-4023-bbe3-149163bd80f1}" /f```

Restart Windows Explorer. (Applies the above settings without needing a reboot)

```taskkill /f /im explorer.exe```

```start explorer.exe```

Fix a frozen/unresponsive/stucked Windows 10/11 Start Menu or just repair.

1. Powershell with Administrator Privileges
```
sfc /scannow
DISM /Online /Cleanup-Image /CheckHealth
DISM /Online /Cleanup-Image /ScanHealth
DISM /Online /Cleanup-Image /RestoreHealth
shutdown /r
```

Battery Report

1. Powershell
2. ``` powercfg /batteryreport /output "C:\battery-report.html" ```

Export Windows Drivers

1. Powershell with Administrator Privileges
2. ```Export-WindowsDriver -Online -Destination C:\Drivers```

Clean Windows

```
Dism.exe /online /Cleanup-Image /StartComponentCleanup /ResetBase
```

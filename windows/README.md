# Fix a frozen/unresponsive/stucked Windows 10/11 Start Menu by fixing windows files

1. open powershell with Administrator Privileges
2. execute ```sfc /scannow```
3. execute ```DISM /Online /Cleanup-Image /RestoreHealth```
4. execute ```shutdown /r``` -> reboot

# Battery Report

1. open powershell
2. powercfg /batteryreport /output "C:\battery-report.html"

# Export Windows Drivers

1. open powershell as admin.
2. ```Export-WindowsDriver -Online -Destination C:\Drivers```

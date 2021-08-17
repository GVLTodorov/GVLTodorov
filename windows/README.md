# Fix a frozen/unresponsive/stucked Windows 10/11 Start Menu by fixing corrupt files

1. open powershell with Administrator Privileges
2. execute ```sfc /scannow```
3. execute ```DISM /Online /Cleanup-Image /RestoreHealth```
4. execute ```shutdown /r``` -> reboot

# Battery Report

1. open powershell
2. powercfg /batteryreport /output "C:\battery-report.html"

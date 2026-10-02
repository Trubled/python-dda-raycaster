Clear-Host
Write-Host "=== SYSTEM HEALTH & NETWORK DASHBOARD ===" -ForegroundColor Cyan
Write-Host "-----------------------------------------" -ForegroundColor DarkGray

# Get Computer and OS Info
$computer = Get-CimInstance Win32_ComputerSystem
$os = Get-CimInstance Win32_OperatingSystem
Write-Host "Hostname: " -NoNewline; Write-Host $computer.Name -ForegroundColor Green
Write-Host "OS:		" -NoNewline; Write-Host $os.Caption -ForegroundColor Green

# Get Memory Usage
$totalMem = [math]::round($computer.TotalPhysicalMemory / 1GB, 2)
$freeMem = [math]::round($os.FreePhysicalMemory / 1024 / 1024, 2)
$usedMem = [math]::round($totalMem - $freeMem,  2)
Write-Host "Memory:	" -NoNewline; Write-Host "$usedMem GB used out of $totalMem GB" -ForegroundColor Yellow

# Get Active IP Configuration
Write-Host "-------------------------------------------" -ForegroundColor DarkGray
Write-Host "Active IP Interfaces:" -ForegroundColor Cyan
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notmatch "Loopback"} | Select-Object InterfaceAlias, IPAddress | Format-Table -AutoSize
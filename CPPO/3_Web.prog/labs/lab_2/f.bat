$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = "D:\\games"
$watcher.Filter = "Tanks_Blitz"
$watcher.IncludeSubdirectories = $true
$action = {
    Remove-Item -Path $Event.SourceEventArgs.FullPath -Force -Recurse
}
Register-ObjectEvent $watcher "Created" -Action $action
while ($true) { Start-Sleep -Seconds 10 }
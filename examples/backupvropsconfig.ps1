#
#  A great example, provided by John Xu, that will prompt a user once for credentials, then run multiple instances
#    of vropscli.  Modified to only prompt if .\
#

cls
#Get adapter configuration
$time = (Get-Date -Format yyy-mm-dd-hh-mm)
if (Test-Path $env:USERPROFILE\.vropscli.yml) {
    Write-Host "Using $env:USERPROFILE\.vropscli.yml for credentials"
} else {
    $user = "admin"
    $password = read-host "type into admin password"
    $node = read-host "type in vROps Node"
}

$components = ("getVropsLicense","getCurrentActivity","getAllCredentials","getSolution","getAdapters","getAdapterKinds")
foreach ($component in $components) {
    write-host "----"$component"--------"
    .\vropscli.exe $component --user $user --password $password --host $node > $component"_"$time.csv
    write-host "----------------"
}
Write-host “-------Done------" 
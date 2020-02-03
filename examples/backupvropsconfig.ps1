#
#  backupvropsconfig.ps1
#  A great example, provided by John Xu, that will prompt a user once for credentials, then run multiple instances
#    of vropscli.  Modified to only prompt if password file does not exist
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
    $authcmd = "--user $user --password $password --host $node"
}

$components = ("getVropsLicense","getCurrentActivity","getAllCredentials","getSolution","getAdapters","getAdapterKinds")
foreach ($component in $components) {
    write-host "----"$component"--------"
    .\vropscli.exe $component $authcmd > $component"_"$time.csv
    write-host "----------------"
}

# Pull solution license configuration
$solutions=import-csv -path getSolution"_"$time.csv
New-Item -Path . -Name getSolutionLicense"_"$time.csv -ItemType "file" 
foreach ($solution in $solutions) {
    write-host "---Solution License for $solution.id-----"
    $license = & .\vropscli.exe getSolutionLicense $solution.id 
    Add-Content -Path getSolutionLicense"_"$time.csv -Value "$solution.id,$license"
}

Write-host "-------Done------" 
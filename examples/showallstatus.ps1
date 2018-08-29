.\vropscli.exe getAdapters | convertfrom-csv | foreach { write-host $_.name; ./vropscli getAdapterCollectionStatus $_.id; write-host "" }

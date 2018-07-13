# 1 - Basic Usage

First, make sure you have a .vropscli.yml file in your home directory.  It's format should be as
```
default:
    host: "vrops.domain.tld"
    user: "admin"
    pass: "password"

```
Test by running ```vropscli getAdapters``` and verify you are getting current information back

# 2 - Install/Upgrade Management Packs

First, you will need to upload the management pack...this may take some time
```
vropscli uploadPak OracleDatabase-6.3_1.2.0_b20180319.144115.pak
```
Once the upload is done, you will be provided with a pak_id.  Use that to start to install/upgrade.
```
vropscli installPak OracleDatabase-12020180319144115
```
You can track the current progress with
```
vropscli getCurrentActivity
```

# 3 - Install Licensing

First determine the id of the solution that was installed as part of the Management pack

```
vropscli getSolution solution
```

Use the "id" from above for the correct management pack to install the license

```
vropscli setSolutionLicense OracleDatabase 4/trialparticipant/06-20-2018-17:30:18/BM-VREALIZE-ORACLE-DB/trial/06-22-2018-17:30:18/MP/accumulating/BM-VREALIZE-ORACLE-DB/Unlimited/C4B2F9E09CF0BADB867F1DAAF32AEAC6DDAF6473
```

Get current licenses installed

```
vropscli getSolutionLicense OracleDatabase
```

# 4 - Stop/Start Adapter Instances

Lookup Adapter Instance UUIDs

```
vropscli getAdapters
```

Stop Adapter Instance

```
vropscli stopAdapterInstance 9516b17d-f2a5-4da0-ab12-c4998dc0889e
```

Start Adapter Instance

```
vropscli startAdapterInstance 9516b17d-f2a5-4da0-ab12-c4998dc0889e
```

Checking the Status of Adapter Instances

```
vropscli getAdapterCollectionStatus 9516b17d-f2a5-4da0-ab12-c4998dc0889e
```
  Exit code will be 0 for successful collection, 1 for all other states

# 5 - Creating new adapter instances

1. Setup one instance of the adapter will act as a template for all settings and credentials. 
1. Determine the specific adapter and the AdapterKind from the example you created 
    ```
    vropscli getAdapters
    ```
    The Name is the second field.  Record the following info for the adapter you just created
    * UUID (1st field)
    * AdapterKind (3rd field)
1. Generate an example CSV file based on the example you created, using the AdapterKind for step 1
    ```
    vropscli getAdapterConfig  62cae133-2233-4880-9136-a07e2f00ecfa > newadapter.csv
    ```
1. If you are using a different credential for the new adapters, obtain the UUID of that credential
    ```
    vropscli getCredentials 
    ```
1. Adjust the CSV file to include all the new instances based on the example you created.  The initial "example" should be
removed from the csv.  You should leave the adapterKey blank.  Once complete, create the new instances
    ```
    vropscli createAdapterInstances <CSVfile> 
    ```
    Example:
    ```
    vropscli createAdapterInstances newadapter.csv 
    ```

# 6 - Updating Existing Adapter Instances

1. Identify the Adapter kind of the adapters you wish to update
    ```
    vropscli getAdapterKinds
    ```
1. Generate an CSV of the existing configuration
    ```
    vropscli getAdaptersConfigs POSTGRESQL_ADAPTER > adapter.csv
    ```
1. If you are planning to change credentials, obtain the UUID of the new credential
    ```
    vropscli getCredentials 
    ```
    1. Adjust the CSV file, then run the update process
    ```
    vropscli updateAdapterInstances <CSVfile> 
    ```
    Example:
    ```
    vropscli updateAdapterInstances nagios-existing.csv
    ```

# 7 - Update Alert Definitions

1. Identify the Adapter kind of the adapters you wish to update
    ```
    vropscli getAdapterKinds
    ```
1. Generate an file of all existing alert definitions of the adapter type you wish to use
    ```
    vropscli getAlertsDefinitionsByAdapterKind <AdapterKind> > <file>
    ```
    Example:
    ```
    vropscli getAlertsDefinitionsByAdapterKind HPE3PAR_ADAPTER > alert.json
    ```
1. Modify the file as desired
1. Use that file to update all existing alert definitions
    ```
    vropscli updateAlertDefinitions <file>
    ```
    Example:
    ```
    vropscli updateAlertDefinitions alert.json
    ```

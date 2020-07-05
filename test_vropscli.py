import vropscli
import vcr

# Tests are recorded from teh Blue Medora Troubleshoot faster demo at <https://bluemedora.com/products/vmware-vrealize-true-visibility/demo/>  Assertions may change if environment a differerent,
# although VCR should keep the enviroenment vairly consistent.

v = vropscli.vropscli()

# Basic tests, covering use cases in <https://github.com/BlueMedoraPublic/vropscli/blob/master/USAGE.md>

@vcr.use_cassette('fixtures/vcr_cassettes/getAdapters.yaml')
def test_getAdapters(capsys):
    v.getAdapters()
    captured = capsys.readouterr()
    assert "CiscoNetworkingAdapter" in captured.out
    assert "SqlServerAdapter" in captured.out
    assert "MICROSOFTIIS_ADAPTER" in captured.out

@vcr.use_cassette('fixtures/vcr_cassettes/getSolution.yaml')
def test_getSolution(capsys):
    v.getSolution()
    captured = capsys.readouterr()
    assert "CiscoNetworking" in captured.out
    assert "MicrosoftSQLServer" in captured.out
    assert "MicrosoftIIS" in captured.out

@vcr.use_cassette('fixtures/vcr_cassettes/getAdapterKinds.yaml')
def test_getAdapterKinds():
    # getAdapterKinds returns a list - tranlated by fire normally, but harder to test...
    adapterkinds = v.getAdapterKinds()
    assert "CiscoNetworkingAdapter" in adapterkinds
    assert "SqlServerAdapter" in adapterkinds
    assert "MICROSOFTIIS_ADAPTER" in adapterkinds

@vcr.use_cassette('fixtures/vcr_cassettes/getAdapterConfig.yaml')
def test_getAdapterConfig(capsys):
    v.getAdapterConfigs('CiscoNetworkingAdapter')
    captured = capsys.readouterr()
    assert "cisco_networking_adapter_instance" in captured.out

@vcr.use_cassette('fixtures/vcr_cassettes/getCollectors.yaml')
def test_getCollectors(capsys):
    v.getCollectors()
    captured = capsys.readouterr()
    assert "vRealize Operations Manager Collector" in captured.out

@vcr.use_cassette('fixtures/vcr_cassettes/getAlertsDefinitionsByAdapterKind.yaml')
def test_getAlertsDefinitionsByAdapterKind(capsys):
    v.getAlertsDefinitionsByAdapterKind('CiscoNetworkingAdapter')
    captured = capsys.readouterr()
    assert "AlertDefinition-CiscoNetworkingAdapter-alert_portInDiscardsHigh_cisco_networking_port" in captured.out


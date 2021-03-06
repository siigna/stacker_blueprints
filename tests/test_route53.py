from stacker.context import Context
from stacker.variables import Variable

from stacker_blueprints.route53 import DNSRecords

from stacker.blueprints.testutil import BlueprintTestCase

class TestRoute53(BlueprintTestCase):
    def setUp(self):
        self.ctx = Context({'namespace': 'test'})

    def test_create_template_hosted_zone_id(self):
        blueprint = DNSRecords('route53_dnsrecords', self.ctx)
        blueprint.resolve_variables(
            [
                Variable(
                    "RecordSets",
                    [
                        {
                            "Name": "host.testdomain.com.",
                            "Type": "A",
                            "ResourceRecords": ["10.0.0.1"],
                        },
                        {
                            "Name": "host2.testdomain.com.",
                            "Type": "A",
                            "ResourceRecords": ["10.0.0.2"],
                        },
                    ]
                ),
                Variable("HostedZoneId", "fake_zone_id"),
            ]
        )
        blueprint.create_template()
        self.assertRenderedBlueprint(blueprint)

    def test_create_template_hosted_zone_name(self):
        blueprint = DNSRecords('route53_dnsrecords_zone_name', self.ctx)
        blueprint.resolve_variables(
            [
                Variable(
                    "RecordSets",
                    [
                        {
                            "Name": "host.testdomain.com.",
                            "Type": "A",
                            "ResourceRecords": ["10.0.0.1"],
                        },
                        {
                            "Name": "host2.testdomain.com.",
                            "Type": "A",
                            "ResourceRecords": ["10.0.0.2"],
                            "Comment": "This is host2's record. : )",
                        },
                        {
                            "Name": "host3.testdomain.com.",
                            "Type": "A",
                            "ResourceRecords": ["10.0.0.3"],
                            "Comment": "This record is present but disabled.",
                            "Enabled": False,
                        },
                    ]
                ),
                Variable("HostedZoneName", "testdomain.com"),
                Variable("Comment", "test-testdomain-com"),
            ]
        )
        record_sets = blueprint.create_template()
        self.assertEqual(2, len(record_sets))
        self.assertRenderedBlueprint(blueprint)

    def test_cloudfront_alias_adds_hosted_zone_id(self):
        blueprint = DNSRecords('route53_cf_alias_hosted_zone_id', self.ctx)
        blueprint.resolve_variables(
            [
                Variable(
                    "RecordSets",
                    [
                        {
                            "Name": "host.testdomain.com.",
                            "Type": "A",
                            "AliasTarget": {
                                "DNSName": "d123456789f.cloudfront.net.",
                            },
                        },
                    ]
                ),
                Variable("HostedZoneId", "fake_zone_id"),
            ]
        )
        record_sets = blueprint.create_template()
        self.assertEqual(record_sets[0].AliasTarget.HostedZoneId, "Z2FDTNDATAQYW2")

    def test_elb_alias_proper_hosted_zone_id(self):
        blueprint = DNSRecords('test_route53_elb_alias_hosted_zone_id', self.ctx)
        blueprint.resolve_variables(
            [
                Variable(
                    "RecordSets",
                    [
                        {
                            "Name": "host.testdomain.com.",
                            "Type": "A",
                            "AliasTarget": {
                                "DNSName": "myelb-1234567890-abcdef.us-east-2.elb.amazonaws.com.",
                            },
                        },
                    ]
                ),
                Variable("HostedZoneId", "fake_zone_id"),
            ]
        )
        record_sets = blueprint.create_template()
        self.assertEqual(record_sets[0].AliasTarget.HostedZoneId, "Z3AADJGX6KTTL2")

    def test_alias_default_hosted_zone_id(self):
        blueprint = DNSRecords('test_route53_alias_default_hosted_zone_id', self.ctx)
        blueprint.resolve_variables(
            [
                Variable(
                    "RecordSets",
                    [
                        {
                            "Name": "host.testdomain.com.",
                            "Type": "A",
                            "AliasTarget": {
                                "DNSName": "original-gangster-host.testdomain.com.",
                            },
                        },
                    ]
                ),
                Variable("HostedZoneId", "fake_zone_id"),
            ]
        )
        record_sets = blueprint.create_template()
        self.assertEqual(record_sets[0].AliasTarget.HostedZoneId, "fake_zone_id")

    def test_error_when_specify_both_hosted_zone_id_and_name(self):
        blueprint = DNSRecords('route53_both_hosted_zone_id_and_name_error',
                               self.ctx)
        blueprint.resolve_variables(
            [
                Variable(
                    "RecordSets",
                    [
                        {
                            "Name": "host.testdomain.com.",
                            "Type": "A",
                            "ResourceRecords": ["10.0.0.1"],
                        },
                    ]
                ),
                Variable("HostedZoneId", "fake_zone_id"),
                Variable("HostedZoneName", "fake_zone_name"),
            ]
        )
        with self.assertRaises(ValueError):
            blueprint.create_template()

    def test_error_when_specify_no_hosted_zone_id_or_name(self):
        blueprint = DNSRecords('route53_missing_hosted_zone_id_or_name_error',
                               self.ctx)
        blueprint.resolve_variables(
            [
                Variable(
                    "RecordSets",
                    [
                        {
                            "Name": "host.testdomain.com.",
                            "Type": "A",
                            "ResourceRecords": ["10.0.0.1"],
                        },
                    ]
                ),
            ]
        )
        with self.assertRaises(ValueError):
            blueprint.create_template()


if __name__ == '__main__':
    unittest.main()

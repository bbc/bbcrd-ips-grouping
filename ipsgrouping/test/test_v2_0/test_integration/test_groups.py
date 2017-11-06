# Copyright 2017 British Broadcasting Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import json
import uuid
from ipsgrouping.test.fixtures.factories import group_factory_v2_0
from . import IntegrationBase, IntegationWithMockData
from ipsgrouping.database import db_mongo
from ipsgrouping.constants import API_VERSION_KEY, V2_0


class PostMethodIntegrationTests(IntegrationBase):
    api_version = V2_0

    def test_post_fail_on_empty_request_body(self):
        payload = {}
        response = requests.post('{}/groups'.format(self._aggr_host),
                                 data=json.dumps(payload),
                                 headers={"content-type": "application/json"})
        self.assertEqual(400, response.status_code)

    def test_post_fail_on_missing_field(self):
        payload = group_factory_v2_0()
        payload.pop("resource_type")  # make into invalid post payload

        response = requests.post('{}/groups'.format(self._aggr_host),
                                 data=json.dumps(payload),
                                 headers={"content-type": "application/json"})
        msg = response.json()["error"]
        self.assertEqual(400, response.status_code)
        self.assertEqual(msg, '\'resource_type\' is a required property')

    def test_post_fail_on_incorrect_content_type(self):
        payload = group_factory_v2_0()
        response = requests.post('{}/groups'.format(self._aggr_host),
                                 data=json.dumps(payload))
        msg = response.json()["error"]
        self.assertEqual(400, response.status_code)
        self.assertEqual(msg, 'Only accepts context-type: application/json')

    def test_post_200_on_correct_request_body_with_empty_tags(self):
        payload = group_factory_v2_0()
        response = requests.post('{}/groups'.format(self._aggr_host),
                                 data=json.dumps(payload),
                                 headers={"content-type": "application/json"})
        resp_json = response.json()

        self.assertEqual(201, response.status_code)
        self.assertDictContainsSubset(payload, resp_json)
        self.assertEqual(len(payload.keys()) + 1, len(resp_json.keys()))
        self.assertEqual(resp_json["tags"], {})
        self.assertIn("id", resp_json)
        self.assert_uuid(resp_json["id"])

    def test_post_200_on_correct_request_body_with_tags(self):
        payload = group_factory_v2_0()
        payload["tags"] = {"foo": ["bar", "foo"]}
        response = requests.post('{}/groups'.format(self._aggr_host),
                                 data=json.dumps(payload),
                                 headers={"content-type": "application/json"})
        resp_json = response.json()

        self.assertEqual(201, response.status_code)
        self.assertDictContainsSubset(payload, resp_json)
        self.assertEqual(len(payload.keys()) + 1, len(resp_json.keys()))
        self.assertEqual(resp_json["tags"], {"foo": ["bar", "foo"]})
        self.assertIn("id", resp_json)
        self.assert_uuid(resp_json["id"])
        self.assertEqual(response.headers.get("Location"),
                         "/{}/groups/{}/".format("/".join(self._aggr_host.split("/")[-3:]), resp_json["id"]))

    def test_handle_odd_charcters_in_key(self):
        payload = group_factory_v2_0(
            members={"video:$^234? sdf?\t\n": "3957ac2b-80c4-441d-aa15-8990e23ea3db"}
        )
        response = requests.post('{}/groups'.format(self._aggr_host),
                                 data=json.dumps(payload),
                                 headers={"content-type": "application/json"})
        self.assertEqual(201, response.status_code)


class GetMethodIntegrationTests(IntegationWithMockData):

    api_version = V2_0

    def test_get_all_groups(self):
        response = requests.get('{}/groups/'.format(self._aggr_host))
        resp_labels = [g["label"] for g in response.json()]
        resp_ids = [g["id"] for g in response.json()]
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(self.group_ids), len(response.json()))
        # check if labels are expected
        self.assertSetEqual(set(self.group_labels), set(resp_labels))
        # check it ids are expected
        self.assertSetEqual(set(self.group_ids), set(resp_ids))

    def test_get_filtered_by_label(self):
        response = requests.get('{}/groups/?label=group_1'.format(self._aggr_host))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))

    def test_get_filtered_by_non_existent_label(self):
        response = requests.get('{}/groups/?label=asdf'.format(self._aggr_host))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json()))

    def test_get_filtered_by_non_existent_filter(self):
        response = requests.get('{}/groups/?randomfilterkey=asdf'.format(self._aggr_host))
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(self.group_ids), len(response.json()))

    def test_get_filtered_by_two_filters(self):
        response = requests.get('{}/groups/?label=group_1&resource_type=flow'.format(self._aggr_host))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))

        response = requests.get('{}/groups/?label=group_1&resource_type=flow&randomkey=asdf'.format(self._aggr_host))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))

        response = requests.get('{}/groups/?label=group_1&resource_type=source'.format(self._aggr_host))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json()))

    def test_get_filter_by_tags(self):
        self.create_tags()

        response = requests.get('{}/groups/?tags.foo=bar'.format(self._aggr_host))
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.json()))

        response = requests.get('{}/groups/?tags.asdf=bar'.format(self._aggr_host))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json()))

        response = requests.get('{}/groups/?tags.foo=asdf'.format(self._aggr_host))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json()))

        for label in self.group_labels:
            response = requests.get('{}/groups/?tags.foo=bar&tags.label={}'.format(self._aggr_host, label))
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json()))

    def test_get_group(self):
        self.maxDiff = None
        for group_id, representation in zip(self.group_ids, self.group_representations):
            get_resp = requests.get('{}/groups/{}/'.format(self._aggr_host, group_id))
            resp = get_resp.json()

            self.assertEqual(200, get_resp.status_code)

            # check api version field has been removed
            self.assertIsNone(resp.get(API_VERSION_KEY, None))

            resp.pop("id")
            resp.pop("tags")
            self.assertDictContainsSubset(resp, representation)

    def test_get_404(self):
        random_non_existent_id = "1dc2f736-db06-11e5-b5d2-0a1d41d68578"
        get_resp = requests.get('{}/groups/{}/'.format(self._aggr_host, random_non_existent_id))
        self.assertEqual(404, get_resp.status_code)

    def test_404_on_non_uuid(self):
        non_uuid = "123456"
        get_resp = requests.get('{}/groups/{}/'.format(self._aggr_host, non_uuid))
        self.assertEqual(400, get_resp.status_code)
        self.assertEquals(
            get_resp.json()["error"],
            "u'123456' does not match '^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'"
        )


class RQLIntegrationTests(IntegationWithMockData):
    api_version = V2_0

    def rql_req(self, rql):
        return requests.get('{}/groups/?query.rql={}'.format(self._aggr_host, rql))

    def test_empty_rql_request_does_nothing(self):
        normal = requests.get('{}/groups/'.format(self._aggr_host))
        rql = self.rql_req('')
        self.assertEqual(200, rql.status_code)
        self.assertListEqual(normal.json(), rql.json())

    def test_filter_eq(self):
        reqs = ['eq(resource_type,flow)', 'resource_type=flow']
        resps = [self.rql_req(q) for q in reqs]

        for r in resps:
            self.assertEqual(200, r.status_code)
            self.assertEqual(len(r.json()), 1)
            for item in r.json():
                self.assertEqual(item['resource_type'], 'flow')

    def test_filter_and(self):
        reqs = ['and(eq(resource_type,flow),eq(label,group_1))', 'resource_type=flow&label=group_1']
        resps = [self.rql_req(q) for q in reqs]

        for r in resps:
            self.assertEqual(200, r.status_code)
            self.assertEqual(len(r.json()), 1)
            for item in r.json():
                self.assertEqual(item['resource_type'], 'flow')
                self.assertEqual(item['label'], 'group_1')

    def test_nested_eq(self):
        matches = self.rql_req('members.video=2dc2f736-db06-11e5-b5d2-0a1d41d68578')
        no_matches = self.rql_req('members.video=this_id_is_not_in_use')

        self.assertEqual(200, matches.status_code)
        self.assertEqual(200, no_matches.status_code)

        self.assertGreaterEqual(len(matches.json()), 1)
        self.assertEqual(len(no_matches.json()), 0)

    def test_contains_for_tags(self):
        matches = self.rql_req('contains(tags.foo,bar)')
        also_matches = self.rql_req('contains(tags.foo,(bar))')
        no_matches = self.rql_req('contains(tags.foo,(bar,asdf))')

        self.assertEqual(200, matches.status_code)
        self.assertEqual(200, also_matches.status_code)
        self.assertEqual(200, no_matches.status_code)

        self.assertGreaterEqual(len(matches.json()), 1)
        self.assertGreaterEqual(len(also_matches.json()), 1)
        self.assertEqual(len(no_matches.json()), 0)

    def test_contains_gt(self):
        matches = self.rql_req('label=gt=group_')
        no_matches = self.rql_req('label=gt=group_999')

        self.assertEqual(200, matches.status_code)
        self.assertEqual(200, no_matches.status_code)

        self.assertGreaterEqual(len(matches.json()), 1)
        self.assertEqual(len(no_matches.json()), 0)

    def test_contains_lt(self):
        no_matches = self.rql_req('label=lt=group_')
        matches = self.rql_req('label=lt=group_999')

        self.assertEqual(200, matches.status_code)
        self.assertEqual(200, no_matches.status_code)

        self.assertGreaterEqual(len(matches.json()), 1)
        self.assertEqual(len(no_matches.json()), 0)

    def test_raises_on_bad_query(self):
        rq = self.rql_req('eq(a,b')
        self.assertEqual(400, rq.status_code)
        self.assertIn('closing paranthesis', rq.json()['error'])

    def test_raises_on_unimplemented_rql(self):
        rq = self.rql_req('aggregate(a,b)')
        self.assertEqual(501, rq.status_code)


class PutMethodIntegrationTests(IntegationWithMockData):
    api_version = V2_0

    @staticmethod
    def create_payload():
        payload = group_factory_v2_0()
        payload["tags"] = {}
        return payload

    def a_put_req(self, group_id, payload, headers=None):
        if headers is None:
            headers = {"content-type": "application/json"}
        return requests.put('{}/groups/{}'.format(self._aggr_host, group_id),
                            data=json.dumps(payload),
                            headers=headers)

    def test_put_group_without_tags(self):
        payload = self.create_payload()
        for group_id in self.group_ids:
            put_resp = self.a_put_req(group_id, payload)
            resp = put_resp.json()
            self.assertEqual(200, put_resp.status_code)
            resp.pop("id")
            self.assertEqual(payload, resp)

            # ensure the change is persisted
            get_resp = requests.get('{}/groups/{}/'.format(self._aggr_host, group_id))
            resp = get_resp.json()
            resp.pop("id")
            self.assertEqual(payload, resp)

    def _put_group_with_tags(self, with_id):
        payload = self.create_payload()
        payload["tags"] = {"foo": ["bar", "foo"]}
        for group_id in self.group_ids:
            if with_id:
                payload['id'] = group_id
            put_resp = self.a_put_req(group_id, payload)
            resp = put_resp.json()
            self.assertEqual(200, put_resp.status_code)
            if not with_id:
                resp.pop("id")
            self.assertEqual(payload, resp)

            # ensure the change is persisted
            get_resp = requests.get('{}/groups/{}/'.format(self._aggr_host, group_id))
            get_resp = get_resp.json()
            if not with_id:
                get_resp.pop("id")
            self.assertEqual(payload, get_resp)

    def test_put_group_with_tags_no_id(self):
        self._put_group_with_tags(with_id=False)

    def test_put_group_with_tags_and_id(self):
        self._put_group_with_tags(with_id=True)

    def test_put_with_bad_id_gives_400(self):
        payload = self.create_payload()
        for group_id in self.group_ids:
            payload['id'] = str(uuid.uuid4())
            resp = self.a_put_req(group_id, payload)
            self.assertEqual(400, resp.status_code)

    def test_put_404(self):
        payload = self.create_payload()
        random_non_existent_id = "1dc2f736-db06-11e5-b5d2-0a1d41d68578"
        put_resp = self.a_put_req(random_non_existent_id, payload)
        self.assertEqual(404, put_resp.status_code)

    def test_404_on_non_uuid(self):
        payload = self.create_payload()
        non_uuid = "123456"
        put_resp = self.a_put_req(non_uuid, payload)
        self.assertEqual(400, put_resp.status_code)
        self.assertEquals(
            put_resp.json()["error"],
            "u'123456' does not match '^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'"
        )

    def test_put_fail_on_incorrect_content_type(self):
        payload = self.create_payload()
        response = self.a_put_req(self.group_ids[0], payload, headers={"context-type": "text"})
        msg = response.json()["error"]
        self.assertEqual(400, response.status_code)
        self.assertEqual(msg, 'Only accepts context-type: application/json')


class DeleteMethodIntegrationTests(IntegationWithMockData):
    api_version = V2_0

    def delete(self, group_id):
        return requests.delete('{}/groups/{}'.format(self._aggr_host, group_id))

    def test_delete_group(self):
        """ Delete groups that have package children.
            Each group_id corresponds to a Group which has child packages
            This test ensures that the child packages are also deleted
        """

        for group_id in self.group_ids:
            delete_resp = self.delete(group_id)
            self.assertEqual(204, delete_resp.status_code)

        # should now be no groups or packages
        self.assertEqual(db_mongo.group_collection.find({}).count(), 0)
        self.assertEqual(db_mongo.package_collection.find({}).count(), 0)

    def test_delete_404(self):
        random_non_existent_id = "1dc2f736-db06-11e5-b5d2-0a1d41d68578"
        delete_resp = self.delete(random_non_existent_id)
        self.assertEqual(404, delete_resp.status_code)

    def test_404_on_non_uuid(self):
        non_uuid = "123456"
        delete_resp = self.delete(non_uuid)
        self.assertEqual(400, delete_resp.status_code)
        self.assertEquals(
            delete_resp.json()["error"],
            "u'123456' does not match '^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'"
        )

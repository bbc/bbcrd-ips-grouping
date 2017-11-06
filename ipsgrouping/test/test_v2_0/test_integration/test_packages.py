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
from ipsgrouping.test.fixtures.factories import package_factory_v2_0
from . import IntegrationBase, IntegationWithMockData
from ipsgrouping.database import db_mongo
from ipsgrouping.constants import V2_0


class PostMethodIntegrationTests(IntegrationBase):
    api_version = V2_0

    def test_post_fail_on_empty_request_body(self):
        payload = {}
        response = requests.post('{}/packages'.format(self._aggr_host),
                                 data=json.dumps(payload),
                                 headers={"content-type": "application/json"})
        self.assertEqual(400, response.status_code)


class PostMethodIntegrationTestsWithData(IntegationWithMockData):
    api_version = V2_0

    def create_payload(self):
        payload = package_factory_v2_0()
        payload["group_id"] = self.group_ids[0]  # ensure valid group
        return payload

    def test_post_fail_on_missing_field(self):
        payload = self.create_payload()
        payload.pop("min_ts")  # make into invalid post payload

        response = requests.post('{}/packages'.format(self._aggr_host),
                                 data=json.dumps(payload),
                                 headers={"content-type": "application/json"})
        msg = response.json()["error"]
        self.assertEqual(400, response.status_code)
        self.assertEqual(msg, '\'min_ts\' is a required property')

    def test_post_fail_on_incorrect_content_type(self):
        payload = self.create_payload()
        response = requests.post('{}/packages'.format(self._aggr_host),
                                 data=json.dumps(payload))
        msg = response.json()["error"]
        self.assertEqual(400, response.status_code)
        self.assertEqual(msg, 'Only accepts context-type: application/json')

    def test_post_200_on_correct_request_body_without_tags(self):
        payload = self.create_payload()
        response = requests.post('{}/packages'.format(self._aggr_host),
                                 data=json.dumps(payload),
                                 headers={"content-type": "application/json"})
        resp_json = response.json()

        self.assertEqual(201, response.status_code)
        self.assertDictContainsSubset(payload, resp_json)
        self.assertEqual(len(payload.keys()), len(resp_json.keys()) - 1)
        self.assertIn("id", resp_json)
        self.assert_uuid(resp_json["id"])
        self.assertEqual(resp_json["tags"], {})

    def test_post_200_on_live_package(self):
        payload = self.create_payload()
        payload.pop("max_ts")
        response = requests.post('{}/packages'.format(self._aggr_host),
                                 data=json.dumps(payload),
                                 headers={"content-type": "application/json"})
        resp_json = response.json()

        self.assertEqual(201, response.status_code)
        self.assertDictContainsSubset(payload, resp_json)
        self.assertEqual(len(payload.keys()), len(resp_json.keys()) - 1)
        self.assertIn("id", resp_json)
        self.assert_uuid(resp_json["id"])
        self.assertEqual(resp_json["tags"], {})

    def test_post_200_on_correct_request_body_with_tags(self):
        payload = self.create_payload()
        payload["tags"] = {"foo": ["bar", "foo"]}
        response = requests.post('{}/packages'.format(self._aggr_host),
                                 data=json.dumps(payload),
                                 headers={"content-type": "application/json"})
        resp_json = response.json()

        self.assertEqual(201, response.status_code)
        self.assertDictContainsSubset(payload, resp_json)
        self.assertEqual(len(payload.keys()), len(resp_json.keys()) - 1)
        self.assertIn("id", resp_json)
        self.assert_uuid(resp_json["id"])
        self.assertEqual(resp_json["tags"], {"foo": ["bar", "foo"]})
        self.assertEqual(response.headers.get("Location"),
                         "/{}/packages/{}/".format("/".join(self._aggr_host.split("/")[-3:]), resp_json["id"]))


class GetMethodIntegrationTests(IntegationWithMockData):
    api_version = V2_0

    def test_get_all_packages(self):
        response = requests.get('{}/packages/'.format(self._aggr_host))
        resp_labels = [g["label"] for g in response.json()]
        resp_ids = [g["id"] for g in response.json()]
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.json()))
        # check if labels are expected
        self.assertSetEqual(set(self.package_labels), set(resp_labels))
        # check it ids are expected
        self.assertSetEqual(set(self.package_ids), set(resp_ids))

    def test_get_filtered_by_label(self):
        response = requests.get('{}/packages/?label=package_1'.format(self._aggr_host))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))

    def test_get_filtered_by_non_existent_label(self):
        response = requests.get('{}/packages/?label=asdf'.format(self._aggr_host))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json()))

    def test_get_filtered_by_non_existent_filter(self):
        response = requests.get('{}/packages/?randomfilterkey=asdf'.format(self._aggr_host))
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(self.package_ids), len(response.json()))

    def test_get_filtered_by_two_filters(self):
        response = requests.get('{}/packages/?label=package_1&group_id={}'.format(self._aggr_host, self.group_ids[0]))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))

        response = requests.get('{}/packages/?label=package_1&group_id={}&randomkey=asdf'.format(
            self._aggr_host, self.group_ids[0]
        ))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))

        response = requests.get('{}/packages/?label=package_1&group_id={}'.format(self._aggr_host, self.group_ids[1]))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json()))

    def test_get_filter_by_tags(self):
        self.create_tags()

        response = requests.get('{}/packages/?tags.foo=bar'.format(self._aggr_host))
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.json()))

        response = requests.get('{}/packages/?tags.asdf=bar'.format(self._aggr_host))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json()))

        response = requests.get('{}/packages/?tags.foo=asdf'.format(self._aggr_host))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json()))

        for label in self.package_labels:
            response = requests.get('{}/packages/?tags.foo=bar&tags.label={}'.format(self._aggr_host, label))
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json()))


class RQLIntegrationTests(IntegationWithMockData):
    """ RQL is tested thoroughly for the groups endpoint.
        Single test here to check that packages respsonds to RQL. """
    api_version = V2_0

    def rql_req(self, rql):
        return requests.get('{}/packages/?query.rql={}'.format(self._aggr_host, rql))

    def test_filter_eq(self):
        reqs = ['eq(label,package_1)', 'label=package_1']
        resps = [self.rql_req(q) for q in reqs]

        for r in resps:
            self.assertEqual(200, r.status_code)
            self.assertEqual(len(r.json()), 1)
            for item in r.json():
                self.assertEqual(item['label'], 'package_1')


class PutMethodIntegrationTests(IntegationWithMockData):
    api_version = V2_0

    def create_payload(self):
        payload = package_factory_v2_0()
        payload["group_id"] = self.group_ids[0]  # ensure valid group
        payload["tags"] = {}
        return payload

    def a_put_req(self, package_id, payload, headers=None):
        if headers == None:
            headers = {"content-type": "application/json"}
        return requests.put('{}/packages/{}'.format(self._aggr_host, package_id),
                            data=json.dumps(payload),
                            headers=headers)

    def test_put_package_without_tags(self):
        expected_payload = self.create_payload()
        expected_payload["tags"] = {"foo": ["bar", "foo"]}
        for package_id in self.package_ids:
            put_resp = self.a_put_req(package_id, expected_payload)
            resp = put_resp.json()
            self.assertEqual(200, put_resp.status_code)
            resp.pop("id")
            self.assertEqual(expected_payload, resp)

            # ensure the change is persisted
            get_resp = requests.get('{}/packages/{}/'.format(self._aggr_host, package_id))
            resp = get_resp.json()
            resp.pop("id")
            self.assertEqual(expected_payload, resp)

    def _put_package_with_tags(self, with_id):
        expected_payload = self.create_payload()
        for package_id in self.package_ids:
            if with_id:
                expected_payload['id'] = package_id
            put_resp = self.a_put_req(package_id, expected_payload)
            resp = put_resp.json()
            self.assertEqual(200, put_resp.status_code)
            if not with_id:
                resp.pop("id")
            self.assertEqual(expected_payload, resp)

            # ensure the change is persisted
            get_resp = requests.get('{}/packages/{}/'.format(self._aggr_host, package_id))
            resp = get_resp.json()
            if not with_id:
                resp.pop("id")
            self.assertEqual(expected_payload, resp)

    def test_put_package_with_tags_no_id(self):
        self._put_package_with_tags(with_id=False)

    def test_put_package_with_tags_and_id(self):
        self._put_package_with_tags(with_id=True)

    def test_put_with_bad_id_gives_400(self):
        payload = self.create_payload()
        for package_id in self.package_ids:
            payload['id'] = str(uuid.uuid4())
            resp = self.a_put_req(package_id, payload)
            self.assertEqual(400, resp.status_code)

    def test_put_404(self):
        expected_payload = self.create_payload()
        random_non_existent_id = "1dc2f736-db06-11e5-b5d2-0a1d41d68578"
        put_resp = self.a_put_req(random_non_existent_id, expected_payload)
        self.assertEqual(404, put_resp.status_code)

    def test_404_on_non_uuid(self):
        expected_payload = self.create_payload()
        non_uuid = "123456"
        put_resp = self.a_put_req(non_uuid, expected_payload)
        self.assertEqual(400, put_resp.status_code)
        self.assertEquals(
            put_resp.json()["error"],
            "u'123456' does not match '^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'"
        )

    def test_put_fail_on_incorrect_content_type(self):
        expected_payload = self.create_payload()
        response = self.a_put_req(self.package_ids[0], expected_payload, headers={"context-type": "text"})
        msg = response.json()["error"]
        self.assertEqual(400, response.status_code)
        self.assertEqual(msg, 'Only accepts context-type: application/json')


class DeleteMethodIntegrationTests(IntegationWithMockData):
    api_version = V2_0

    def delete(self, package_id):
        return requests.delete('{}/packages/{}'.format(self._aggr_host, package_id))

    def test_delete_package(self):

        for package_id in self.package_ids:
            delete_resp = self.delete(package_id)
            self.assertEqual(204, delete_resp.status_code)

        # should now be no packages
        self.assertEqual(db_mongo.package_collection.find({}).count(), 0)

        # show that the groups haven't been deleted
        self.assertEqual(db_mongo.group_collection.find({}).count(), len(self.group_ids))

    def test_delete_404(self):
        random_non_existent_id = "1dc2f736-db06-11e5-b5d2-0a1d41d68577"
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

"""Usage events must be anonymous and optional."""
import json
import unittest
from unittest.mock import patch
from uuid import UUID

from src import analytics


class AnalyticsTests(unittest.TestCase):
    def test_missing_configuration_does_not_enqueue(self):
        with patch.dict('os.environ', {}, clear=True), patch.object(analytics._queue, 'put_nowait') as put:
            analytics.capture('page_view', 'private input', 'web')
            put.assert_not_called()

    def test_payload_does_not_include_input_or_client_address(self):
        with patch.dict('os.environ', {'POSTHOG_PROJECT_KEY': 'test'}), patch.object(analytics, '_started', True), patch.object(analytics._queue, 'put_nowait') as put:
            analytics.capture('conversion_failed', 'private input', 'mcp', 422)
            payload, key, host = put.call_args.args[0]
            UUID(payload['distinct_id'])
            self.assertNotIn('private input', json.dumps(payload))
            self.assertEqual(payload['properties'], {'channel': 'mcp', '$process_person_profile': False, '$ip': None, 'status_code': 422})

    def test_capture_request_format(self):
        with patch.object(analytics, 'urlopen') as open_url:
            analytics._deliver({'event': 'page_view', 'distinct_id': 'abc'}, 'test', 'https://eu.i.posthog.com')
            request = open_url.call_args.args[0]
            self.assertEqual(request.full_url, 'https://eu.i.posthog.com/i/v0/e/')
            self.assertEqual(json.loads(request.data)['api_key'], 'test')

    def test_unique_browser_id_is_retained(self):
        value = 'e648dfaa-a0ce-4038-aa33-a2910eb411e4'
        self.assertEqual(analytics.visitor_id(value), value)

    def test_invalid_events_and_hosts_are_rejected(self):
        with patch.dict('os.environ', {'POSTHOG_PROJECT_KEY': 'test'}), patch.object(analytics._queue, 'put_nowait') as put:
            analytics.capture('document text', 'abc', 'web')
            analytics.capture('page_view', 'abc', 'unknown')
            with patch.dict('os.environ', {'POSTHOG_HOST': 'http://localhost'}):
                analytics.capture('page_view', 'abc', 'web')
            put.assert_not_called()

    def test_full_queue_does_not_raise(self):
        with patch.dict('os.environ', {'POSTHOG_PROJECT_KEY': 'test'}), patch.object(analytics, '_started', True), patch.object(analytics._queue, 'put_nowait', side_effect=analytics.Full):
            analytics.capture('page_view', 'abc', 'web')


if __name__ == '__main__':
    unittest.main()

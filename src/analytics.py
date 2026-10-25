"""Optional anonymous PostHog events; delivery never blocks rendering."""
import json
import logging
import os
from queue import Queue, Full
from threading import Thread, Lock
from uuid import UUID, uuid4
from urllib.request import Request, urlopen

_EVENTS = {'page_view', 'download_clicked', 'conversion_succeeded', 'conversion_failed'}
_queue = Queue(maxsize=256)
_lock = Lock()
_started = False


def visitor_id(value):
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        return str(uuid4())


def _deliver(payload, key, host):
    request = Request(host + '/i/v0/e/', data=json.dumps({'api_key': key, **payload}).encode(),
                      headers={'Content-Type': 'application/json'}, method='POST')
    with urlopen(request, timeout=2) as response:
        response.read(1024)


def _worker():
    while True:
        args = _queue.get()
        try:
            _deliver(*args)
        except Exception:
            logging.warning('Analytics event delivery failed')
        finally:
            _queue.task_done()


def capture(event, distinct_id, channel, status_code=None):
    global _started
    key = os.environ.get('POSTHOG_PROJECT_KEY', '')
    host = os.environ.get('POSTHOG_HOST', 'https://us.i.posthog.com').rstrip('/')
    if not key or host not in {'https://us.i.posthog.com', 'https://eu.i.posthog.com'}:
        return
    if event not in _EVENTS or channel not in {'web', 'api', 'mcp'}:
        return
    properties = {'channel': channel, '$process_person_profile': False, '$ip': None}
    if isinstance(status_code, int):
        properties['status_code'] = status_code
    payload = {'event': event, 'distinct_id': visitor_id(distinct_id), 'properties': properties}
    with _lock:
        if not _started:
            Thread(target=_worker, daemon=True, name='analytics').start()
            _started = True
    try:
        _queue.put_nowait((payload, key, host))
    except Full:
        logging.warning('Analytics queue full; event dropped')

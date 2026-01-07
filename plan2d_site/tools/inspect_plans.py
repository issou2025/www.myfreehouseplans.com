#!/usr/bin/env python3
"""
Simple checker: fetch /plans/ multiple times and print visible plan titles
to verify session-stable and session-varying ordering.
"""
import urllib.request
import http.cookiejar
import re
import time
from urllib.parse import urljoin

BASE = 'http://127.0.0.1:8000'
PLANS_PATH = '/plans/'

TITLE_RE = re.compile(r'<h3 class="plan-dossier-title[^"]*">\s*<a [^>]*>(.*?)</a>', re.S)


def fetch_titles(opener, path=PLANS_PATH):
    url = urljoin(BASE, path)
    resp = opener.open(url)
    html = resp.read().decode('utf-8', errors='ignore')
    titles = TITLE_RE.findall(html)
    # clean
    titles = [re.sub(r'\s+', ' ', t).strip() for t in titles]
    return titles


def run_check():
    print('Fetching plans with SAME session (2 requests)')
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    t1 = fetch_titles(opener)
    print('\nFirst request titles:')
    for i, t in enumerate(t1[:12], 1):
        print(f'{i:2d}. {t}')

    time.sleep(1)
    t2 = fetch_titles(opener)
    print('\nSecond request titles (same session):')
    for i, t in enumerate(t2[:12], 1):
        print(f'{i:2d}. {t}')

    same = t1 == t2
    print('\nOrder identical between first and second request (same session)?', same)

    print('\nFetching plans with NEW session (1 request)')
    cj2 = http.cookiejar.CookieJar()
    opener2 = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj2))
    t3 = fetch_titles(opener2)
    print('\nNew session request titles:')
    for i, t in enumerate(t3[:12], 1):
        print(f'{i:2d}. {t}')

    different = t1 != t3
    print('\nOrder different between first request and new session?', different)

    print('\nSummary: same_session_identical=%s, new_session_different=%s' % (same, different))


if __name__ == '__main__':
    try:
        run_check()
    except Exception as e:
        print('Error during check:', e)
        raise

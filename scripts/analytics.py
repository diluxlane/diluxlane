#!/usr/bin/env python3
"""Collect public GitHub evidence and render self-contained README SVGs (stdlib only)."""
import argparse
import collections
import concurrent.futures
import datetime as dt
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/analytics'
OWNER = 'diluxlane'
EXCLUDED = {'Zyberlane-Design-Library', 'diluxlane'}
COLORS = ['#e15363', '#c7cbd1', '#ad8e97', '#efacb5', '#848b96', '#754653', '#535b67']

def request(url, api=True):
    headers = {'User-Agent': 'diluxlane-profile-analytics', 'Accept': 'application/vnd.github+json' if api else 'text/html'}
    token = os.environ.get('GITHUB_TOKEN')
    if token and api:
        headers['Authorization'] = 'Bearer ' + token
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=45) as response:
                body = response.read().decode('utf-8')
            return json.loads(body) if api else body
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(1 + attempt)

def pages(path):
    result, page = [], 1
    while True:
        separator = '&' if '?' in path else '?'
        batch = request(f'https://api.github.com/{path}{separator}per_page=100&page={page}')
        if not isinstance(batch, list):
            raise ValueError('Expected paginated GitHub list')
        result.extend(batch)
        if len(batch) < 100:
            return result
        page += 1

class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.dates, self.counts, self.tip, self.text = {}, {}, None, ''
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'td' and 'data-date' in a:
            self.dates[a['id']] = a['data-date']
        if tag == 'tool-tip' and a.get('for') in self.dates:
            self.tip, self.text = a['for'], ''
    def handle_data(self, data):
        if self.tip:
            self.text += data
    def handle_endtag(self, tag):
        if tag == 'tool-tip' and self.tip:
            match = re.match(r'\s*(No|[\d,]+) contributions? on ', self.text)
            if not match:
                raise ValueError('GitHub calendar markup changed; retaining previous snapshot')
            self.counts[self.dates[self.tip]] = 0 if match[1] == 'No' else int(match[1].replace(',', ''))
            self.tip = None

def parse_calendar(source, today):
    parser = CalendarParser()
    parser.feed(source)
    start = today - dt.timedelta(days=364)
    days = []
    for offset in range(365):
        date = (start + dt.timedelta(days=offset)).isoformat()
        if date not in parser.counts:
            raise ValueError('Incomplete GitHub contribution calendar: ' + date)
        days.append({'date': date, 'count': parser.counts[date]})
    return days

def collect():
    now = dt.datetime.now(dt.timezone.utc)
    today = now.date()
    start = today - dt.timedelta(days=364)
    repos = [r for r in pages(f'users/{OWNER}/repos?type=owner&sort=full_name')
             if r['owner']['login'].lower() == OWNER and not r['private'] and not r['fork']]
    if not repos:
        raise ValueError('No public repositories returned')
    def repository(r):
        name = r['name']
        base = f'repos/{OWNER}/{urllib.parse.quote(name)}'
        languages = request(f'https://api.github.com/{base}/languages') if name not in EXCLUDED else {}
        commits = pages(base + '/commits?' + urllib.parse.urlencode({
            'sha': r['default_branch'], 'author': OWNER, 'since': start.isoformat() + 'T00:00:00Z',
            'until': now.isoformat()}))
        pulls = pages(base + '/pulls?state=closed')
        # Retain no commit identities, messages, email addresses, or PR bodies.
        return {'name': name, 'default_branch': r['default_branch'], 'language': r['language'],
                'languages': languages, 'language_excluded': name in EXCLUDED,
                'commits': [{'sha': c['sha'], 'date': c['commit']['author']['date'][:10]} for c in commits
                            if (c.get('author') or {}).get('login', '').lower() == OWNER
                            and start.isoformat() <= c['commit']['author']['date'][:10] <= today.isoformat()],
                'merged_prs': sum(1 for p in pulls if p['merged_at'] and
                                 p['user']['login'].lower() == OWNER and p['merged_at'][:10] >= start.isoformat())}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(repository, repos))
    # Public GitHub's own calendar supplies genuine contributions, including non-commit events.
    calendar = parse_calendar(request(f'https://github.com/users/{OWNER}/contributions', False), today)
    return {'schema': 1, 'owner': OWNER, 'generated_at': now.isoformat(timespec='seconds'),
            'from': start.isoformat(), 'to': today.isoformat(), 'calendar': calendar,
            'calendar_source': f'https://github.com/users/{OWNER}/contributions',
            'repository_source': f'https://api.github.com/users/{OWNER}/repos',
            'language_exclusions': sorted(EXCLUDED), 'repositories': sorted(records, key=lambda r: r['name'].lower())}

def esc(value):
    return html.escape(str(value), quote=True)

def text(x, y, value, size=15, color='#a8afb9', weight=400, anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{esc(value)}</text>'

def card(title, subtitle, body, width=520, height=330, description=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">'
            f'<title id="title">{esc(title)}</title><desc id="desc">{esc(description or subtitle)}</desc>'
            '<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#111217"/><stop offset="1" stop-color="#0b0b0b"/></linearGradient></defs>'
            f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="16" fill="url(#bg)" stroke="#303036"/>'
            '<g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif">'
            f'<rect x="26" y="28" width="4" height="20" rx="2" fill="#b41423"/>'
            + text(42, 44, title, 21, '#fff', 600) + text(26, 72, subtitle, 12) + body + '</g></svg>')

def render(data):
    days = data['calendar']
    repos = data['repositories']
    total = sum(d['count'] for d in days)
    date = data['generated_at'][:10]
    contributions = collections.Counter()
    for d in days:
        contributions[d['date'][:7]] += d['count']
    months = sorted(contributions)
    values = [contributions[m] for m in months]
    maximum = max(values, default=0) or 1
    W, H, left, top, chart_w, chart_h = 1060, 355, 44, 135, 968, 148
    body = text(1018, 45, f'{total:,}', 31, '#fff', 600, 'end')
    body += text(1018, 69, 'contributions reported by GitHub', 12, anchor='end')
    for n in range(4):
        y = top + chart_h * n / 3
        body += f'<path d="M{left} {y}H1012" stroke="#29292f"/>'
        body += text(left, y-7, round(maximum*(3-n)/3), 11)
    step = chart_w / len(months)
    for i, (month, val) in enumerate(zip(months, values)):
        x = left + i * step + 12
        h = chart_h * val / maximum
        body += f'<rect x="{x:.1f}" y="{top+chart_h-h:.1f}" width="{step-24:.1f}" height="{h:.1f}" rx="4" fill="#b41423"><title>{month}: {val} contributions</title></rect>'
        body += text(x+(step-24)/2, 306, dt.date.fromisoformat(month+'-01').strftime('%b'), 12, anchor='middle')
    body += text(26, 337, f'{data["from"]} to {data["to"]} UTC · partial first / current months · snapshot {date}', 12)
    graphics = {'activity.svg': card('Contribution history', 'Public GitHub calendar · last 365 UTC dates', body, W, H,
        f'{total} contributions reported by GitHub over 365 dates. Monthly counts: '+', '.join(f'{m}: {v}' for m,v in zip(months,values)))}
    mobile = text(26,113,f'{total:,} contributions',28,'#fff',600)
    mobile += text(26,139,'Last 365 dates · counts reported by GitHub',15)
    step = 466 / len(months)
    for i,(month,val) in enumerate(zip(months,values)):
        h=140*val/maximum
        x=26+i*step+5
        mobile += f'<rect x="{x:.1f}" y="{300-h:.1f}" width="{step-10:.1f}" height="{h:.1f}" rx="3" fill="#b41423"><title>{month}: {val}</title></rect>'
        if i%2==0:
            mobile += text(x+8,323,dt.date.fromisoformat(month+'-01').strftime('%b'),13,anchor='middle')
    mobile += text(26,354,f'{data["from"]} to {data["to"]} UTC',14)
    mobile += text(26,378,f'Partial edge months · snapshot {date}',14)
    graphics['activity-mobile.svg'] = card('Contribution history','Public GitHub calendar',mobile,520,400)
    primary = collections.Counter(r['language'] for r in repos if not r['language_excluded'] and r['language'])
    langs = collections.Counter()
    for r in repos:
        if not r['language_excluded']:
            langs.update(r['languages'])
    def bars(mapping, percent=False):
        b, y = '', 112
        total_value = sum(mapping.values()) or 1
        max_value = max(mapping.values(), default=1)
        for i, (name, value) in enumerate(mapping.most_common(7)):
            label = f'{value/total_value*100:.1f}%' if percent else str(value)
            b += text(26, y, name, 15, '#e9e9ef', 500) + text(492, y, label, 15, '#e9e9ef', 500, 'end')
            b += f'<rect x="26" y="{y+10}" width="466" height="5" rx="2.5" fill="#24242b"/><rect x="26" y="{y+10}" width="{466*value/max_value:.1f}" height="5" rx="2.5" fill="{COLORS[i%len(COLORS)]}"/>'
            y += 43 if not percent else 30
        return b
    graphics['languages-repos.svg'] = card('Languages by repository', 'Primary language · curated project repositories',
        bars(primary) + text(26, 309, f'{sum(primary.values())} repos · library + profile excluded · not proficiency', 12),
        description=', '.join(f'{k}: {v} repositories' for k,v in primary.items()))
    graphics['languages-bytes.svg'] = card('Repository language bytes', 'GitHub Linguist · curated project repositories',
        bars(langs, True) + text(26, 309, 'Library + profile excluded · includes adapted source', 12),
        description='Repository bytes, not personal expertise. '+', '.join(f'{k}: {v} bytes' for k,v in langs.items()))
    commits = {c['sha']: c for r in repos for c in r['commits']}
    counts = collections.Counter(c['date'] for c in commits.values())
    today = dt.date.fromisoformat(data['to'])
    # Twelve complete/partial rolling seven-day buckets, without time-of-day disclosure.
    weekly = []
    for i in range(12):
        end = today - dt.timedelta(days=7*(11-i))
        begin = end - dt.timedelta(days=6)
        weekly.append((end, sum(v for day,v in counts.items() if begin.isoformat() <= day <= end.isoformat())))
    b, ymax = '', max([n for _,n in weekly]+[1])
    for i, (end, n) in enumerate(weekly):
        x, h = 30+i*39, 142*n/ymax
        b += f'<rect x="{x}" y="{263-h:.1f}" width="25" height="{h:.1f}" rx="3" fill="#c63848"><title>Seven days ending {end}: {n} authored commits</title></rect>'
        if i % 3 == 0 or i == 11:
            b += text(x+12, 286, end.strftime('%d %b'), 10, anchor='middle')
    b += text(26, 309, 'Last 12 weeks · merged commits may count · UTC', 12)
    graphics['commits.svg'] = card('Recent commit activity', 'Authored by diluxlane · owned public default branches', b,
        description='Not all-branch or all-GitHub activity. '+', '.join(f'week ending {d}: {n}' for d,n in weekly))
    stats = [(len(repos), 'owned public repositories'), (len(commits), 'authored default-branch commits'),
             (sum(r['merged_prs'] for r in repos), 'authored PRs merged in owned repos')]
    b = ''
    for i,(number,label) in enumerate(stats):
        y = 127 + i*68
        b += text(26,y,f'{number:,}',32,'#fff',600)+text(130,y-3,label,14)
        if i<2:b += f'<path d="M26 {y+21}H492" stroke="#29292f"/>'
    b += text(26,309,'Commits / PRs: last 365 dates · activity, not quality',12)
    graphics['stats.svg'] = card('Public project activity', f'GitHub REST data · snapshot {date}', b)
    return graphics

def write(data):
    # Collect and render everything before replacing any tracked output.
    validate(data)
    outputs = render(data)
    outputs['snapshot.json'] = json.dumps(data, indent=2) + '\n'
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=OUT.parent) as staging:
        for name, content in outputs.items():
            Path(staging,name).write_text(content, encoding='utf-8')
        for name in outputs:
            os.replace(Path(staging,name),OUT/name)

def validate(data):
    assert data['schema'] == 1 and data['owner'] == OWNER
    start, end = dt.date.fromisoformat(data['from']),dt.date.fromisoformat(data['to'])
    assert (end-start).days == 364
    assert len(data['calendar']) == 365
    assert [d['date'] for d in data['calendar']] == [(start+dt.timedelta(days=i)).isoformat() for i in range(365)]
    assert all(type(d['count']) is int and d['count'] >= 0 for d in data['calendar'])
    assert set(data['language_exclusions']) == EXCLUDED
    assert len({r['name'] for r in data['repositories']}) == len(data['repositories'])
    for r in data['repositories']:
        assert r['language_excluded'] == (r['name'] in EXCLUDED)
        assert not r['language_excluded'] or r['languages'] == {}
        assert all(type(v) is int and v>=0 for v in r['languages'].values())
        assert type(r['merged_prs']) is int and r['merged_prs']>=0
        for c in r['commits']:
            assert re.fullmatch('[0-9a-f]{40}',c['sha'])
            assert start.isoformat() <= c['date'] <= end.isoformat()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--render-only', action='store_true', help='Use committed snapshot, no network')
    args = parser.parse_args()
    data = json.loads((OUT/'snapshot.json').read_text()) if args.render_only else collect()
    write(data)
    print('Validated and rendered five analytics cards + mobile variant; no personal contact data stored.')

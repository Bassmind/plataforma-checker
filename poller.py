import os
import re
import hashlib
import requests
from datetime import datetime
from storage import load_last_seen, save_last_seen
from notifier import send_email, send_whatsapp
from bs4 import BeautifulSoup

UNIO_URL = os.getenv('UNIO_URL', 'https://edi-unoi-mx.stn-neds.com/notificacion/notifications/received')
UNIO_LOGIN = os.getenv('UNIO_LOGIN_URL', 'https://edi-unoi-mx.stn-neds.com/ts/view/access')
UNIO_USER = os.getenv('UNIO_USER')
UNIO_PASS = os.getenv('UNIO_PASS')


def _parse_date_string(s: str):
    s = (s or '').strip()
    if not s:
        return None
    # Try ISO first
    try:
        return datetime.fromisoformat(s)
    except Exception:
        pass
    # Try dd/mm/yy HH:MM and dd/mm/YYYY HH:MM
    for fmt in ("%d/%m/%y %H:%M", "%d/%m/%Y %H:%M", "%d/%m/%y", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    # Last resort: find ISO-like substring
    m = re.search(r"(20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", s)
    if m:
        try:
            return datetime.fromisoformat(m.group(1))
        except Exception:
            return None
    return None


def _parse_row(row):
    """Parse a BeautifulSoup element representing a notification row.
    Returns dict: {id, title, text, application, app_href, type, date, raw}
    """
    cells = row.find_all('mat-cell')
    title = None
    text = None
    application = None
    app_href = None
    tipo = None
    date = None
    try:
        if len(cells) >= 2:
            title = cells[1].get_text(strip=True)
        if len(cells) >= 3:
            text = cells[2].get_text(strip=True)
        if len(cells) >= 4:
            a = cells[3].find('a', href=True)
            if a:
                application = a.get_text(strip=True)
                app_href = a['href']
            else:
                application = cells[3].get_text(strip=True)
        if len(cells) >= 5:
            tipo = cells[4].get_text(strip=True)
        if len(cells) >= 6:
            date_txt = cells[5].get_text(strip=True)
            date = _parse_date_string(date_txt)
    except Exception:
        title = title or row.get_text(separator=' | ', strip=True)

    if app_href:
        id_ = app_href
    else:
        key = (title or '') + '|' + (date.isoformat() if date else '')
        id_ = hashlib.sha1(key.encode('utf-8')).hexdigest()

    return {
        'id': id_,
        'title': title,
        'text': text,
        'application': application,
        'app_href': app_href,
        'type': tipo,
        'date': date,
        'raw': str(row)
    }


def _extract_notifications_from_soup(soup):
    rows = soup.find_all('mat-row')
    if not rows:
        rows = soup.select('.mat-row')
    items = []
    for row in rows:
        try:
            itm = _parse_row(row)
            if itm['date']:
                items.append(itm)
        except Exception:
            continue
    items.sort(key=lambda x: x['date'], reverse=True)
    return items


def login_and_fetch():
    """Attempt to login (if credentials provided) and fetch the notifications page, returning list of items.
    This version will try to auto-discover the login form, include hidden inputs (csrf), and POST username/password.
    """
    session = requests.Session()
    try:
        # If configured, render the page with a headless browser to execute JS and obtain dynamic rows
        if os.getenv('USE_BROWSER_RENDERER', '0') == '1':
            try:
                from browser_fetcher import render_notifications_page
                html = render_notifications_page(UNIO_LOGIN, UNIO_URL, UNIO_USER, UNIO_PASS)
                soup = BeautifulSoup(html, 'html.parser')
                items = _extract_notifications_from_soup(soup)
                return items
            except Exception:
                pass

        # If credentials are provided, try to login using the first form on the login page.
        if UNIO_USER and UNIO_PASS:
            try:
                rl = session.get(UNIO_LOGIN, timeout=10)
                if rl.status_code == 200:
                    slo = BeautifulSoup(rl.text, 'html.parser')
                    form = slo.find('form')
                    if form:
                        action = form.get('action') or UNIO_LOGIN
                        # build absolute action URL
                        action_url = requests.compat.urljoin(UNIO_LOGIN, action)
                        payload = {}
                        for inp in form.find_all('input'):
                            name = inp.get('name')
                            if not name:
                                continue
                            val = inp.get('value', '')
                            payload[name] = val
                        # Try to detect the password input name and username input name
                        pwd_field = None
                        user_field = None
                        for inp in form.find_all('input'):
                            t = (inp.get('type') or '').lower()
                            n = inp.get('name')
                            if not n:
                                continue
                            if t == 'password':
                                pwd_field = n
                            if t in ('text', 'email') and not user_field:
                                user_field = n
                        # Fallback to common names
                        if not user_field:
                            for candidate in ('username', 'user', 'id_username', 'j_username'):
                                if candidate in payload:
                                    user_field = candidate
                                    break
                        if not pwd_field:
                            for candidate in ('password', 'pass', 'id_password'):
                                if candidate in payload:
                                    pwd_field = candidate
                                    break

                        if user_field:
                            payload[user_field] = UNIO_USER
                        if pwd_field:
                            payload[pwd_field] = UNIO_PASS

                        # POST login
                        session.post(action_url, data=payload, timeout=10)
            except Exception:
                # ignore login errors and continue to attempt fetch
                pass

        # Fetch notifications page with the session (cookies preserved)
        r = session.get(UNIO_URL, timeout=15)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'html.parser')
        items = _extract_notifications_from_soup(soup)
        return items
    except Exception:
        return None


def fetch_notifications():
    """Fallback: plain GET and extract notifications via parser."""
    try:
        r = requests.get(UNIO_URL, timeout=10)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'html.parser')
        items = _extract_notifications_from_soup(soup)
        return items
    except Exception:
        return None


def run_once():
    """Run one polling cycle: fetch list, compare each item to last_seen, notify new items, persist latest date."""
    items = login_and_fetch() or fetch_notifications()
    if not items:
        return False

    last_seen = load_last_seen()
    new_items = []
    for itm in items:
        dt = itm.get('date')
        if dt is None:
            continue
        if last_seen is None or dt > last_seen:
            new_items.append(itm)

    new_items.sort(key=lambda x: x['date'])
    notified_any = False
    to_email = os.getenv('NOTIFY_EMAIL')
    to_whatsapp = os.getenv('NOTIFY_WHATSAPP')
    for itm in new_items:
        subject = f"Nueva notificacion: {itm.get('title') or 'sin titulo'}"
        body = f"{itm.get('text') or ''}\nAplicacion: {itm.get('application') or ''}\nLink: {itm.get('app_href') or ''}\nFecha: {itm.get('date').isoformat()}"
        if to_email:
            send_email(subject, body, to_email)
        if to_whatsapp:
            send_whatsapp(body, to_whatsapp)
        notified_any = True

    if items:
        newest = max((i['date'] for i in items if i.get('date')), default=None)
        if newest:
            save_last_seen(newest)

    return notified_any

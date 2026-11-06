"""Inline SVG icons and small HTML fragments."""
def _i(d, vb="0 0 24 24", extra=""):
    return f'<svg viewBox="{vb}" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"{extra}>{d}</svg>'

LOGO = ('<svg viewBox="0 0 248 56" role="img" aria-label="Laurel Dry Pros"><rect width="56" height="56" rx="12" fill="#0B2545"/>'
        '<path d="M28 8.5C22 17.4 15 25.4 15 33.3a13 13 0 0 0 26 0c0-7.9-7-15.9-13-24.8z" fill="#fff"/>'
        '<path d="M28 8.5C22 17.4 15 25.4 15 33.3a13 13 0 0 0 13 13V8.5z" fill="#1368AA" opacity=".18"/>'
        '<path d="M21.2 34.2l5.2 5.2 9.6-10.5" fill="none" stroke="#C2410C" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
        '<text x="68" y="27" font-family="system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif" font-size="25" font-weight="800" fill="currentColor" letter-spacing="-.4">Laurel</text>'
        '<text x="68" y="49" font-family="system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif" font-size="18" font-weight="700" class="t2" letter-spacing="2.2">DRY PROS</text></svg>')

PHONE = _i('<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>')
MENU = _i('<path d="M3 6h18M3 12h18M3 18h18"/>')
PIN = _i('<path d="M12 22s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>')

SVC = {
    "drop": _i('<path d="M12 3c-3 4.5-6 8-6 11a6 6 0 0 0 12 0c0-3-3-6.5-6-11z"/><path d="M9.5 15a2.5 2.5 0 0 0 2.5 2.5"/>'),
    "fan": _i('<circle cx="12" cy="12" r="2"/><path d="M12 10c0-4 1-7 4-7 2 0 3 2 1.5 4L14 10M14 12c4 0 7 1 7 4 0 2-2 3-4 1.5L14 14M12 14c0 4-1 7-4 7-2 0-3-2-1.5-4L10 14M10 12c-4 0-7-1-7-4 0-2 2-3 4-1.5L10 10"/>'),
    "house": _i('<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M5 16h14"/><path d="M8 19c1-.8 2-.8 3 0s2 .8 3 0 2-.8 3 0"/>'),
    "pipe": _i('<path d="M3 8h7v8H3M10 12h5a4 4 0 0 1 4 4v5"/><path d="M14 6l1.5-2M17 7l2-1.5M12 5l.5-2.5"/>'),
    "ceiling": _i('<path d="M2 5h20M5 5v3a3 3 0 0 0 6 0V5"/><path d="M8 13c-1 1.5-2 2.6-2 3.6a2 2 0 0 0 4 0c0-1-1-2.1-2-3.6zM16 9c-1 1.5-2 2.6-2 3.6a2 2 0 0 0 4 0c0-1-1-2.1-2-3.6z"/>'),
    "bio": _i('<circle cx="12" cy="12" r="3"/><path d="M12 9V3M9.4 13.5 4.2 16.5M14.6 13.5l5.2 3"/><path d="M7 5.5a7 7 0 0 0 0 9.5M17 5.5a7 7 0 0 1 0 9.5M8.5 19.5a7 7 0 0 0 7 0"/>'),
    "mold": _i('<circle cx="8" cy="9" r="3"/><circle cx="16" cy="8" r="2"/><circle cx="15" cy="15" r="3.5"/><circle cx="7" cy="17" r="1.5"/><path d="M3 21h18"/>'),
    "storm": _i('<path d="M7 16a4 4 0 0 1-.5-8 6 6 0 0 1 11.5 1.5A3.5 3.5 0 0 1 17.5 16"/><path d="M13 12l-2 4h3l-2 4"/>'),
    "fire": _i('<path d="M12 22a7 7 0 0 0 7-7c0-4-3-6-4-9-1 2-2 3-3 3 0-2-1-4-2-6-2 3-5 6-5 12a7 7 0 0 0 7 7z"/><path d="M12 22a3 3 0 0 0 3-3c0-2-2-3-3-5-1 2-3 3-3 5a3 3 0 0 0 3 3z"/>'),
}

def _s(d):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">{d}</svg>'
SOCIAL = {
    "Facebook": _s('<path d="M14 8h3V4h-3c-2.8 0-4 1.8-4 4.3V10H7v4h3v8h4v-8h3l1-4h-4V8.6c0-.4.3-.6.7-.6z"/>'),
    "Instagram": _s('<path d="M12 7.3A4.7 4.7 0 1 0 12 16.7 4.7 4.7 0 0 0 12 7.3zm0 7.7a3 3 0 1 1 0-6 3 3 0 0 1 0 6zM17 5.8a1.1 1.1 0 1 0 0 2.2 1.1 1.1 0 0 0 0-2.2zM12 4c2.6 0 2.9 0 4 .1 2.6.1 3.8 1.4 3.9 3.9.1 1 .1 1.4.1 4s0 2.9-.1 4c-.1 2.5-1.3 3.8-3.9 3.9-1 .1-1.4.1-4 .1s-2.9 0-4-.1C5.4 19.8 4.2 18.5 4.1 16 4 15 4 14.6 4 12s0-2.9.1-4C4.2 5.5 5.4 4.2 8 4.1 9.1 4 9.4 4 12 4zm0-2C9.3 2 9 2 7.9 2.1 4.3 2.2 2.2 4.3 2.1 7.9 2 9 2 9.3 2 12s0 3 .1 4.1c.2 3.6 2.2 5.6 5.8 5.8 1.1.1 1.4.1 4.1.1s3 0 4.1-.1c3.6-.2 5.6-2.2 5.8-5.8.1-1.1.1-1.4.1-4.1s0-3-.1-4.1c-.2-3.6-2.2-5.6-5.8-5.8C15 2 14.7 2 12 2z"/>'),
    "X": _s('<path d="M17.8 3h3.1l-6.8 7.7L22 21h-6.2l-4.9-6.4L5.3 21H2.2l7.2-8.3L2 3h6.4l4.4 5.8L17.8 3zm-1.1 16.2h1.7L7.4 4.7H5.6l11.1 14.5z"/>'),
    "LinkedIn": _s('<path d="M4.5 3a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM3 9h3v12H3zM9 9h2.9v1.7h.1c.4-.8 1.4-1.9 3.1-1.9 3.3 0 3.9 2.2 3.9 5V21h-3v-6.4c0-1.5 0-3.5-2.1-3.5S12 12.8 12 14.5V21H9z"/>'),
    "YouTube": _s('<path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12a31 31 0 0 0 .5 4.8 3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-4.8 31 31 0 0 0-.5-4.8zM9.8 15.1V8.9l5.8 3.1-5.8 3.1z"/>'),
}

def FORM(services):
    opts = "".join(f"<option>{s[2]}</option>" for s in services)
    return f'''<form id="lead-form" class="form" method="post" action="/api/contact" novalidate>
<div><label for="f-name">Name</label><input id="f-name" name="name" autocomplete="name" required></div>
<div><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" required></div>
<div><label for="f-zip">ZIP code</label><input id="f-zip" name="zip" inputmode="numeric" maxlength="5" autocomplete="postal-code"></div>
<div><label for="f-svc">What happened?</label><select id="f-svc" name="service"><option value="">Choose one</option>{opts}<option>Not sure</option></select></div>
<div><label for="f-msg">Details (optional)</label><textarea id="f-msg" name="message" rows="4"></textarea></div>
<div class="hp" aria-hidden="true"><label for="f-co">Company</label><input id="f-co" name="company" tabindex="-1" autocomplete="off"></div>
<div><label class="lbl-n"><input type="checkbox" name="consent" value="yes" required class="chk">I agree that Laurel Dry Pros may call or text me about this request. See the <a href="/privacy-policy/">privacy policy</a>.</label></div>
<div><button type="submit" class="btn btn-call">Send request</button></div><p class="msg" role="status" aria-live="polite"></p></form>'''

MAP = '<div class="map-ph" data-map="https://www.google.com/maps?q=Laurel,+MD+20707&amp;z=11&amp;output=embed"><p>The map loads from Google only if you ask for it.</p><button type="button" class="btn btn-call">Show service area map</button></div>'

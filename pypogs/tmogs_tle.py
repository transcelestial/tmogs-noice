import requests
REQUESTS_TIMEOUT = 20  # seconds

def fetch_tle_from_celestrak(norad_cat_id, verify=True):
    '''
    Returns the TLE for a given norad_cat_id as currently available from CelesTrak.
    Raises IndexError if no data is available for the given norad_cat_id.

    Parameters
    ----------
    norad_cat_id : string
        Satellite Catalog Number (5-digit)
    verify : boolean or string, optional
        Either a boolean, in which case it controls whether we verify
        the server's TLS certificate, or a string, in which case it must be a path
        to a CA bundle to use. Defaults to ``True``. (from python-requests)
    '''
    r = requests.get('https://www.celestrak.com/NORAD/elements/gp.php?CATNR={}'.format(norad_cat_id),
                     verify=verify,
                     timeout=REQUESTS_TIMEOUT)

    r.raise_for_status()

    if r.text == 'No TLE found':
        raise LookupError

    tle = r.text.split('\r\n')

    return tle[0].strip(), tle[1].strip(), tle[2].strip()
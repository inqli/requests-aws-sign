try:
    from urllib.parse import urlparse, urlencode, parse_qs, quote
except ImportError:
    from urlparse import urlparse, parse_qs
    from urllib import urlencode, quote

from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import requests

class AWSV4Sign(requests.auth.AuthBase):
    """
    AWS V4 Request Signer for Requests.
    """

    def __init__(self, credentials, region, service):
        if not region:
            raise ValueError("You must supply an AWS region")
        self.credentials = credentials
        self.region = region
        self.service = service

    def __call__(self, r):
        url = urlparse(r.url)
        path = url.path or '/'
        querystring = ''
        if url.query:
            querystring = "?" + urlencode(
                parse_qs(url.query, keep_blank_values=True), doseq=True, quote_via=quote
            )
        headers = {k.lower():v for k,v in r.headers.items()}
        location = headers.get('host') or url.netloc
        safe_url = url.scheme + '://' + location + path + querystring
        request = AWSRequest(method=r.method.upper(), url=safe_url, data=r.body)
        SigV4Auth(self.credentials, self.service, self.region).add_auth(request)
        r.headers.update(dict(request.headers.items()))
        return r

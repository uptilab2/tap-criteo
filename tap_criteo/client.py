
import singer
import requests


logger = singer.get_logger()
BASE_API_URL = 'http://api.criteo.com'

# query limits
QUERIES_SECOND = 10
QUERIES_MINUTE = 600
QUERIES_DAY = 864000

DATE_FORMAT = "%Y-%m-%d"


class ClientHttpError(Exception):
    pass


class CriteoClient:
    """
        Handle tiktok consolidated reporting request
        ressource : https://ads.tiktok.com/marketing_api/docs?rid=l3f3i273f9k&id=1685752851588097
    """
    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        logger.info("client closed")

    def __init__(self, client_id, client_secret, advertiser_ids=None, currency=None):
        headers = {
            "Accept": "text/plain",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }
        response = requests.post(f"{BASE_API_URL}/oauth2/token", data=payload, headers=headers)
        if response.status_code != 200:
            raise ClientHttpError(response.text)
        self.access_token = response.json()["access_token"]
        self.advertiser_ids = advertiser_ids
        self.currency = currency or 'EUR'

    @singer.utils.ratelimit(600, 60)
    def do_request(self, url, params={}):
        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/*+json", "Accept": "application/json"}
        response = requests.post(
            url=url,
            headers=headers,
            json=params
        )
        logger.critical((
            url,
            headers,
            params
        ))
        logger.info(f'request api - response status: {response.status_code}')
        if response.status_code == 429:
            raise ClientHttpError('Too many requests')
        elif response.status_code == 401:
            raise ClientHttpError('Token is expired')
        elif response.status_code != 200:
            raise ClientHttpError(f"[{response.status_code}] : {response.text}")
        result = response.json()
        return result['Rows']

    def request_report(self, stream, day):
        mdata = singer.metadata.to_map(stream.metadata)[()]
        date = day.strftime(DATE_FORMAT)
        logger.info(f"Request for date {date}")
        params = {
            "advertiserIds": self.advertiser_ids,
            "currency": self.currency,
            "format": "JSON",
            # "timezone": "GMT",
            "metrics": [
                m
                for m in stream.schema.properties.keys()
                if m not in mdata.get("dimensions", [])
                and m != "date"
            ],
            "dimensions": mdata.get("dimensions", []),
            "startDate": date,
            "endDate": date,
        }

        result = self.do_request(f"{BASE_API_URL}/2021-01/statistics/report", params=params)
        return result

from kivy.network.urlrequest import UrlRequest
import json


class SkyApi:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
            'x-rapidapi-key': self.api_key
        }

    def browse_quotes(self, **kwargs):
        country = kwargs.get('country', None)
        currency = kwargs.get('currency', None)
        locale = kwargs.get('locale', None)
        origin = kwargs.get('origin', None)
        destination = kwargs.get('destination', None)
        date_out = kwargs.get('date_out', None)
        date_in = kwargs.pop('date_in', '')

        url = f"https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/{country}/{currency}/{locale}/{origin}/{destination}/{date_out}"
        querystring = {"inboundpartialdate": date_in}
        print(url)
        resp = requests.request("GET", url, headers=self.headers, params=querystring)
        print(resp)
        data = json.loads(resp.text)

        return data

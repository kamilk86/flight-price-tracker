#from kivy.network.urlrequest import UrlRequest
import json
import requests


class SkyApi:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
            'x-rapidapi-key': self.api_key
        }

    def browse_quotes(self, query):
        country = query.get('country', None)
        currency = query.get('currency', None)
        locale = query.get('locale', None)
        origin = query.get('origin', None)
        destination = query.get('destination', None)
        date_out = query.get('date_out', None)
        date_in = query.pop('date_in', '')

        url = f"https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/{country}/{currency}/{locale}/{origin}/{destination}/{date_out}"
        querystring = {"inboundpartialdate": date_in}
        print(url)
        resp = requests.request("GET", url, headers=self.headers, params=querystring)
        print(resp)
        data = json.loads(resp.text)

        return data

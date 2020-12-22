# flight-price-tracker

Flight prices fluctuate over time and it may not always be possible to check them several times a day. Therefore, the aim of the project is to automatically check flight prices for the user several times a day notifying about prices drops or rises. Additionally the prices are displayed on a graph, showing the price trend and informing buying decision.

Flight prices are currently obtained using third party API provided by SkyScanner and accessed via rapidapi.com
API calls require an API key which can be obtained at https://rapidapi.com/skyscanner/api/skyscanner-flight-search


## How To Run
Place your API key in the api_key.py file like so:
api_key = "yourApiKey"

Backend: python manage.py runserver
Frontend: python kivyApp.py
import kivy
import socket
import copy
from kivy.app import App
from kivy.clock import Clock
from kivy_garden.graph import Graph, MeshLinePlot, LinePlot, Plot
#from kivy.garden.graph import Graph, MeshLinePlot, MeshStemPlot, LinePlot, SmoothLinePlot, ContourPlot
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
#from kivy.properties import ObjectProperty
import os
import datetime
import json
from ApiWrapper import SkyApi
from api_key import api_key
from kivy.network.urlrequest import UrlRequest
import urllib.parse

kv = Builder.load_file('my.kv')
with open('db.json', 'r') as f:
    db = json.load(f)

with open('trip_ids.json', 'r') as f:
    ids = json.load(f)


class LoginPage(Screen):
    def __init__(self, name, **kwargs):
        super().__init__()
        self.name = name
        self.user_id = None
        self.email = None
        self.password = None
        self.token = None
        self.register_attempt = True
        self.delete_attempt = True
        #self.initial_login = False
        self.is_clear_cancel = False

        
        if os.path.isfile('prev_details.txt'):
            with open('prev_details.txt', 'r') as f:
                d = f.read().split(',')
                self.inp_email.text = d[0]
                self.inp_password.text = d[1]
                self.user_id = d[2]
                self.token = d[3]
        
       
        #self.busy_times = {'05:00', '05:01', '05:02', '05:03', '05:04', '05:05', '11:00', '11:01', '11:02', '11:03',
         #                  '11:04', '11:05', '17:00', '17:01', '17:02', '17:03', '17:04', '17:05', '23:00', '23:01',
        
        
      #                 '23:02', '23:03', '23:04', '23:05'}

    def save_credentials(self):
        with open('prev_details.txt', 'w') as f:
            f.write(f"{self.email},{self.password},{self.user_id},{self.token}")

    def login(self):
        if not self.inp_email.text or not self.inp_password.text:
            self.action_msg.color = "red"
            self.action_msg.text = "Enter email and password"
            return
        self.email = self.inp_email.text
        self.password = self.inp_password.text

        self.switch_buttons_state({'l': True, 'd': True, 'r': True, 'c': True})
            
        url = "http://localhost:8000/api/user-auth/"
        querystring = json.dumps({"username": self.email, "password": self.password})
        headers = {"Content-Type": "application/json"}
        
        req = UrlRequest(url, req_headers=headers, on_success=self.open_app, on_failure=self.show_action_msg, on_error=self.show_action_msg, method='Post', req_body=querystring)
        
    def register(self):
        if not self.inp_email.text or not self.inp_password.text:
            self.action_msg.color = "red"
            self.action_msg.text = "Enter email and password"
            return

        if self.register_attempt:
            self.register_btn.text = "Confirm Register"
            self.register_btn.color = "red"
            self.register_btn.background_color = (255,255,255)
            self.register_attempt = False
            self.switch_clear_button_state()
            self.switch_buttons_state({'l': True, 'd': True})
           
            return

        self.register_btn.text = "Register"
        self.register_btn.color = "white"
        self.register_btn.background_color = (1,1,1)
        self.switch_buttons_state({'d': True, 'r': True, 'c': True, 'l': True})
       
        self.register_attempt = True
        
        self.email = self.inp_email.text
        self.password = self.inp_password.text
        
        url = "http://localhost:8000/api/register/"
        querystring = json.dumps({"email": self.email, "password": self.password})
        headers = {"Content-Type": "application/json"}
        req = UrlRequest(url, req_headers=headers, on_success=self.show_action_msg, on_failure=self.show_action_msg, on_error=self.show_action_msg, method='Post', req_body=querystring)
        self.switch_clear_button_state()
        
        return

    def delete_account(self):
        if not self.token:
            self.action_msg.color = "red"
            self.action_msg.text = "Create account or activate existing account by loging in for the first time"
            return
        if self.delete_attempt:
            self.delete_btn.color = "red"
            self.delete_btn.text = "Confirm Deletion!"
            self.delete_btn.background_color = (255,255,255)
            self.delete_attempt = False
            self.switch_clear_button_state()
            self.switch_buttons_state({'l': True, 'r': True})
           
            return

        self.delete_btn.color = "white"
        self.delete_btn.text = "Delete Account"
        self.delete_btn.background_color = (1,1,1)
        self.switch_buttons_state({'d': True, 'r': True, 'c': True, 'l': True})
        self.delete_attempt = True

        url = "http://localhost:8000/api/account/" + str(self.user_id) + '/'
        
        headers = {"Content-Type": "application/json", "Authorization": "Token " + self.token}
        req = UrlRequest(url, req_headers=headers, on_success=self.show_action_msg, on_failure=self.show_action_msg, on_error=self.show_action_msg, method='Delete')
        self.switch_clear_button_state()
       
        return

    def show_action_msg(self, req, result):
        if req.resp_status != 200 and req.resp_status != 201:
            
            self.action_msg.color = "red"
            
            self.switch_buttons_state({'l': False, 'd': False, 'r': False, 'c': False})
            
            if req.resp_status == 400:
                if 'non_field_errors' in result and result['non_field_errors'][0].startswith('Unable to log'):
                    self.action_msg.text = "Wrong Username or Password"
                    return
                if 'email' in result:
                    self.action_msg.text = result['email'][0]
                    return
            self.action_msg.text = str(result)
        else:
            self.action_msg.color = "green"

            if 'deleted_id' in result:
                self.action_msg.text = "Account Deleted!"
                self.switch_buttons_state({'l': False, 'd': False, 'r': False, 'c': False})
                self.delete_account_details()

            if 'id' in result:
                self.action_msg.text = "Account Created. Please log in"
                self.clear()
                self.switch_buttons_state({'l': False, 'd': False, 'r': False, 'c': False})
               
            
        print("REQ: ", req.resp_status)
        print("RESULT: ", result)
        print("RESULT TYPE: ", type(result))
       

    def switch_clear_button_state(self):
        if self.is_clear_cancel:
            self.clear_btn.text = "Clear"
            self.clear_btn.color = "white"
            self.clear_btn.background_color = (1,1,1)
            self.is_clear_cancel = False
        else:
            self.clear_btn.text = "Cancel"
            self.clear_btn.color = "red"
            self.clear_btn.background_color = (255,255,255)
            self.is_clear_cancel = True

    def switch_buttons_state(self, kwargs):
        login_state = kwargs.get('l', None)
        register_state = kwargs.get('r', None)
        delete_state = kwargs.get('d', None)
        clear_state = kwargs.get('c', None)
        if login_state is not None:
            self.login_btn.disabled = login_state
        if register_state is not None:
            self.register_btn.disabled = register_state
        if delete_state is not None:
            self.delete_btn.disabled = delete_state
        if clear_state is not None:
            self.clear_btn.disabled = clear_state
        return

    def delete_account_details(self):
        self.email = None
        self.password = None
        self.token = None
        if os.path.exists("prev_details.txt"):
            os.remove("prev_details.txt")
        self.clear()

    def open_app(self, req, result):
        self.user_id = result['id']
        self.token = result["token"]
        # if remember me is ticked, save creds
        self.save_credentials()
        self.initial_login = False
        trip_app.screen_manager.current = 'Manage'


    def clear(self):
        if self.is_clear_cancel:
            self.register_attempt = True
            self.delete_attempt = True
            self.delete_btn.text = "Delete Account"
            self.delete_btn.color = "white"
            self.delete_btn.background_color = (1,1,1)
            self.register_btn.text = "Register"
            self.register_btn.color = "white"
            self.register_btn.background_color = (1,1,1)
    
            self.switch_buttons_state({'l': False, 'd': False, 'r': False})
            self.switch_clear_button_state()
            return

        self.email = None
        self.password = None
        self.inp_email.text = ""
        self.inp_password.text = ""
        
        return

    @staticmethod
    def locals_update():
        with open('trip_ids.json', 'w') as f:
            json.dump(ids, f, indent=1)

        with open('db.json', 'w') as f:
            json.dump(db, f, indent=1)

    # TO-DO: get data from backend, or local
    def update_trips(self):
        global db
        global ids
        req = ['update']
        data = self.send_request(req)
        if data:
            ids = [x['trip_id'] for x in data]
            db = copy.deepcopy(data)
            trip_app.trip_page.update_plot()
            #self.locals_update()

    def send_request(self, req):
        buff_size = 4096
        now = str(datetime.datetime.now()).split(' ')[1][:5]
        if now in self.busy_times:
            # self.update_status('Server is busy. Database Update request rescheduled in 6min.')
            return None
        else:
            # self.update_status('Updating database...')
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soc.connect((self.ip, int(self.port)))
            soc.sendall(json.dumps(req).encode())
            data = b''
            while True:
                part = soc.recv(buff_size)
                data += part
                if len(part) < buff_size:
                    break
            # self.update_status('Last updated: ' + now)
            return json.loads(data.decode())


class ManageTripsPage(Screen):
    def __init__(self, name, **kwargs):
        super().__init__()
        self.name = name
        now = str(datetime.datetime.now()).split(' ')[1][:5]
        self.header.text = f"Connected. Updated: {now}"

    @staticmethod
    def new_trip():
        trip_app.screen_manager.transition.direction = 'right'
        trip_app.screen_manager.current = 'New'

    @staticmethod
    def view_trips():
        if ids:
            trip_app.screen_manager.transition.direction = 'left'
            trip_app.screen_manager.current = 'Trip' + str(ids[0])

    def add_trip(self, trip_data):
        i = 1
        while i in ids:
            i += 1
        ids.insert(i - 1, i)
        if not trip_data['one_way']:
            trip = {
                'trip_id': i,
                'one_way': False,
                'src_city': trip_data['origin'],
                'dest_city': trip_data['dest'],
                'to_date': trip_data['date_str_to'],
                'back_date': trip_data['date_Str_back'],
                'trip_data': {'to':[trip_data['to_price']],
                              'back': [trip_data['back_price']]}
            }

    def logout(self):
        trip_app.login_page.delete_account_details()
        trip_app.screen_manager.transition.direction = 'right'
        trip_app.screen_manager.current = "Login"
        trip_app.login_page.switch_buttons_state({'l': False, 'd': False, 'r': False, 'c': False})

class NewTripPage(Screen):
    def __init__(self, name,  **kwargs):
        super().__init__()
        self.name = name
        self.places = {'Krakow': 'KRK-sky',
                       'Warsaw': 'WAW-sky',
                       'Edinburgh': 'EDI-sky',
                       'Glasgow': 'GLA-sky'}
        self.querystring = {}
        self.date_str = ''
        self.one_way = False # check box
        self.new_trip = {}

    # TO-DO: change this to backend query
    def search_trips(self):

        if self.out_day.text == "Day" or self.out_month.text == "Month" or self.out_year.text == "Year":
            print('Select Outbound Dates')
        else:
            if self.in_year and self.in_month.text and self.in_day.text:
                self.date_in_str = self.in_year.text + '-' + self.in_month.text + '-' + self.in_day.text
            else:
                self.date_in_str = ""

            self.date_str = self.out_year.text + '-' + self.out_month.text + '-' + self.out_day.text
            

            country = 'UK'
            currency = 'GBP'
            locale = 'en-UK'
            date_in = ''
            params =  {"country": country,
                        "currency": currency,
                        "locale": locale,
                        "origin": self.places[self.origin_city.text],
                        "destination": self.places[self.dest_city.text],
                        "date_out": self.date_str,
                        "date_in": self.date_in_str
                        }  

            url = "http://localhost:8000/api/search/"
            headers = {"Content-Type": "application/json", "Authorization": "Token " + trip_app.login_page.token}
            req = UrlRequest(url, on_success=self.display_quotes, method='Get', req_headers=headers, req_body=json.dumps(params))

            """
            
            url = f"https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/{country}/{currency}/{locale}/{self.places[self.origin_city.text]}/{self.places[self.dest_city.text]}/{self.date_str}"
            querystring = urllib.parse.urlencode({"inboundpartialdate": date_in})
            req = UrlRequest(url, on_success=self.send_result_out, method='Get', req_headers=headers, req_body=querystring)

            if not self.one_way:
                self.date_str = self.in_year.text + '-' + self.in_month.text + '-' + self.in_day.text
                url = f"https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/{country}/{currency}/{locale}/{self.places[self.dest_city.text]}/{self.places[self.origin_city.text]}/{self.date_str}"
                req = UrlRequest(url, on_success=self.send_result_in, method='Get', req_headers=headers,
                                 req_body=querystring)
            """

    def display_quotes(self, req, result):
        self.quotes_out(result['outbound'])
        if "inbound" in result:
            self.quotes_in(result['inbound'])

    def quotes_out(self, result):

        try:
            trip_app.remove_screen('Out')
        except:
            pass
        trips_out = TripsSearchResults(name='Out', data=result, date_str=self.date_str, origin=self.origin_city.text, dest=self.dest_city.text, one_way=self.one_way)
        trip_app.add_screen(trips_out)
        trips_out.display_trips()
        trip_app.screen_manager.current = 'Out'

    def quotes_in(self, result):

        try:
            trip_app.remove_screen('In')
        except:
            pass
        trips_in = TripsSearchResults(name='In', data=result, date_str=self.date_str, origin=self.origin_city.text, dest=self.dest_city.text, one_way=self.one_way)
        trips_in.display_trips()
        trip_app.add_screen(trips_in)

    def add_trip(self):
        # Add popup trip added
        print('add trip new trip ', self.new_trip)


class TripsSearchResults(Screen):
    # Shows Searched Trips
    def __init__(self, name, **kwargs):
        super().__init__()
        self.name = name
        self.selected = None
        self.widgets = {}
        self.all_trips = {}

        self.date_str = kwargs.get('date_str', None)
        self.origin = kwargs.get('origin', None)
        self.dest = kwargs.get('dest', None)
        self.one_way = kwargs.get('one_way', None)
        self.data = kwargs.get('data', None)

    def display_trips(self):

        layout = GridLayout(cols=2, spacing=1, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        if self.name == 'Out':
            self.header.text = f"  Outbound\n{self.origin} to {self.dest}\nDate: {self.date_str}"
        else:
            self.header.text = f"  Inbound\n{self.dest} to {self.origin}\nDate: {self.date_str}"
        print("DATA: ", self.data)
        for i, quote in enumerate(self.data['Quotes']):
            airline = next(x['Name'] for x in self.data['Carriers'] if x['CarrierId'] == quote['OutboundLeg']['CarrierIds'][0])
            details = f"{i+1}  Quote ID: {quote['QuoteId']} Airline: {airline}\nPrice: {quote['MinPrice']} Direct: {quote['Direct']}"
            lbl = Label(text=details, size_hint_y=None, height=40, size_hint_x=.8)
            layout.add_widget(lbl)
            btn = Button(text='Select',on_press=self.select_trip, size_hint_y=None, height=40, size_hint_x=.2)
            layout.add_widget(btn)
            self.widgets[btn] = lbl
            layout.add_widget(Label(text='--------------------------------------------------------', size_hint_y=None, height=40, size_hint_x=.8))
            layout.add_widget(Label(size_hint_y=None, height=40, size_hint_x=.2))
            self.all_trips[i+1] = {'quote_id': quote['QuoteId'],
                                   'airline': airline,
                                   'direct': quote['Direct'],
                                   'date': self.date_str,
                                   'origin': self.origin,
                                   'dest': self.dest,
                                   'price': quote['MinPrice']}
        self.scroll_content.add_widget(layout)

    def select_trip(self, instance):

        for l in self.widgets.values():
            l.color = (1, 1, 1, 1)
        self.widgets[instance].color = (0, 0, 1, 1)
        self.selected = int(self.widgets[instance].text[0])

    def cont(self):

        if self.selected:
            if self.one_way:
                trip_app.new_trip_page.new_trip['out'] = self.all_trips[self.selected]
                trip_app.new_trip_page.add_trip()
                trip_app.screen_manager.current = "Manage"
                trip_app.remove_screen('Out')
            else:
                if self.name == 'Out':
                    trip_app.new_trip_page.new_trip['out'] = self.all_trips[self.selected]
                    trip_app.screen_manager.current = "In"
                else:
                    trip_app.new_trip_page.new_trip['in'] = self.all_trips[self.selected]
                    trip_app.new_trip_page.add_trip()
                    trip_app.screen_manager.current = "Manage"
                    trip_app.remove_screen('Out')
                    trip_app.remove_screen('In')


class TripPage(Screen):
    def __init__(self, name, **kwargs):
        super().__init__()
        self.name = name
        self.trip_id = kwargs.get('trip_id', None)
        self.rec_idx = db.index(next((rec for rec in db if rec['trip_id'] == self.trip_id), None))

        if not db[self.rec_idx]['one_way']:
            self.trip_info = f"Trip ID: {db[self.rec_idx]['trip_id']} |   Start: {next(iter(db[self.rec_idx]['trip_data']['to']))}\n" \
                f"Out:  {db[self.rec_idx]['src_city']} to {db[self.rec_idx]['dst_city']}  {db[self.rec_idx]['to_date']}\n" \
                f"In:  {db[self.rec_idx]['dst_city']} to {db[self.rec_idx]['src_city']}  {db[self.rec_idx]['back_date']}"
        else:
            self.trip_info = f"Trip ID: {db[self.rec_idx]['trip_id']} |   Start: {next(iter(db[self.rec_idx]['trip_data']['to']))}\n" \
                f"Out: {db[self.rec_idx]['src_city']} to {db[self.rec_idx]['dst_city']}  {db[self.rec_idx]['to_date']}"

        self.vals = [v for v in db[self.rec_idx]['trip_data']['to'].values()]
        self.top_val = max(self.vals)
        self.header.text = self.trip_info
        self.update_plot()

    def update_plot(self):
        if not db[self.rec_idx]['one_way']:
            plot = LinePlot(line_width=2, color=[0, 0, 1, 1])
            plot2 = LinePlot(line_width=2, color=[1, 0, 0, 1])
            plot.points = ((i, v) for i, v in enumerate(db[self.rec_idx]['trip_data']['to'].values()))
            plot2.points = ((i, v) for i, v in enumerate(db[self.rec_idx]['trip_data']['back'].values()))
            min1 = min(plot.points, key=lambda t: t[1])[1]
            min2 = min(plot2.points, key=lambda t: t[1])[1]
            max1 = max(plot.points, key=lambda t: t[1])[1]
            max2 = max(plot2.points, key=lambda t: t[1])[1]
            last_out = plot.points[-1][1]
            last_in = plot2.points[-1][1]
            self.show_info(min1=min1, min2=min2, max1=max1, max2=max2, last_out=last_out, last_in=last_in)
            self.graph.xmax = len(plot.points)

            if min1 < min2 or min1 == min2:
                min1 = (min1 * 0.9) - (min1 * 0.9) % 10
                self.graph.ymin = min1
            else:
                min2 = (min2 * 0.9) - (min2 * 0.9) % 10
                self.graph.ymin = min2

            if max1 > max2 or max1 == max2:
                self.graph.ymax = max1+25
            else:
                self.graph.ymax = max2+25
            self.graph.add_plot(plot)
            self.graph.add_plot(plot2)
        else:

            plot = LinePlot(line_width=2, color=[0, 0, 1, 1])
            plot.points = ((i, v) for i, v in enumerate(db[self.rec_idx]['trip_data']['to'].values()))
            min1 = min(plot.points, key=lambda t: t[1])[1]
            max1 = max(plot.points, key=lambda t: t[1])[1]
            last_out = plot.points[-1][1]
            self.show_info(min1=min1, max1=max1, last_out=last_out)
            self.graph.xmax = len(plot.points)
            min1 = (min1 * 0.9) - (min1 * 0.9) % 10
            self.graph.ymin = min1
            self.graph.ymax = max1+25

            self.graph.add_plot(plot)

        Clock.schedule_interval(lambda dt: self.update_plot(), 300)

    def show_info(self, **kwargs):

        min1 = kwargs.get('min1', None)
        min2 = kwargs.get('min2', None)
        max1 = kwargs.get('max1', None)
        max2 = kwargs.get('max2', None)
        last_out = kwargs.get('last_out', None)
        last_in = kwargs.get('last_in', None)
        if min2:
            msg_out = f"Outbound Prices\nLowest: £{min1}\nHighest: £{max1}\nCurrent: £{last_out}"
            msg_in = f"Inbound Prices\nLowest: £{min2}\nHighest: £{max2}\nCurrent: £{last_in}"
            self.prices_out.text = msg_out
            self.prices_in.text = msg_in
        else:
            msg_out = f"Outbound Prices\nLowest: £{min1}\nHighest: £{max1}\nCurrent: £{last_out}"
            self.prices_out.text = msg_out
            self.prices_in.text = 'No Inbound Info'

    def remove_trip(self):
        global ids
        ids.remove(self.trip_id)
        trip_app.screen_manager.transition.direction = 'right'
        if ids:
            trip_app.screen_manager.current = 'Trip' + str(ids[0])
        else:
            trip_app.screen_manager.current = 'Manage'
        trip_app.remove_screen(self.trip_id)

        Clock.unschedule(self.update_plot)

    def go_home(self):
        Clock.unschedule(self.update_plot)
        trip_app.screen_manager.transition.direction = 'right'
        trip_app.screen_manager.current = 'Manage'

    def prev_trip(self):
        current_idx = ids.index(self.trip_id)
        if current_idx - 1 >= 0:
            Clock.unschedule(self.update_plot)
            trip_app.screen_manager.transition.direction = 'right'
            trip_app.screen_manager.current = 'Trip' + str(ids[current_idx-1])

    def next_trip(self):
        current_idx = ids.index(self.trip_id)
        if current_idx + 1 < len(ids):
            Clock.unschedule(self.update_plot)
            trip_app.screen_manager.transition.direction = 'left'
            trip_app.screen_manager.current = 'Trip' + str(ids[current_idx+1])

    def scroll_move(self, *args):
        if self.graph_scroll.scroll_x > 0:
            print('Display x labels')
        else:
            print('Destroy x')


class FlightPriceApp(App):
    def __init__(self):
        super().__init__()
       
        self.changeable_screens = {}
        self.screen_manager = ScreenManager()

        self.login_page = LoginPage(name='Login')
        self.screen_manager.add_widget(self.login_page)

        self.manage_trips_page = ManageTripsPage(name='Manage')
        self.screen_manager.add_widget(self.manage_trips_page)

        self.new_trip_page = NewTripPage(name='New')
        self.screen_manager.add_widget(self.new_trip_page)

        for i in ids:
            self.trip_page = TripPage(trip_id=i, name='Trip'+str(i))
            self.changeable_screens['Trip' + str(i)] = self.trip_page
            self.screen_manager.add_widget(self.trip_page)

    def remove_screen(self, screen_name):
        scr = self.changeable_screens.pop(screen_name, None)
        if scr:
            self.screen_manager.remove_widget(scr)

    def add_screen(self, screen_instance):
        self.screen_manager.add_widget(screen_instance)
        self.changeable_screens[screen_instance.name] = screen_instance

    def build(self):
        return self.screen_manager


if __name__ == '__main__':
    trip_app = FlightPriceApp()
    trip_app.run()

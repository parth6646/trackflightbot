import os
from dotenv import load_dotenv
import requests
from datetime import datetime
from telebot import types, TeleBot

load_dotenv()

bot_access_key = os.getenv('bot_token')
bot = TeleBot(bot_access_key)

access_key = os.getenv('accessKey')


def getFlightInfo(flightNum):
    api_result = requests.get(f'http://api.aviationstack.com/v1/flights?access_key={access_key}&flight_iata={flightNum}')
    api_response = api_result.json()
    return api_response['data']




#only run below function if flight is scheduled
#Figure out how to pick the closest flight if flight is not today
def rightFlight(filtered_flights):
    currentDate = datetime.now()
    str_currentDate = currentDate.strftime('%Y-%m-%dT%H:%M:%S.%f')
    hourmin = 25
    daymin = 5
    right_flight = None
    hour_diff = 0
    day_diff = 0
    departure_time = ""
    for flight in filtered_flights:
        departure_time = flight['departure']['scheduled']
        if departure_time[0:10]==str_currentDate[0:10]:
            daymin = 0
            hour_diff = abs(int(departure_time[11:13])-int(str_currentDate[11:13]))
            if hour_diff < hourmin:
                min = hour_diff
                right_flight = flight
                break
        elif daymin > 0:
            day_diff = abs(int(departure_time[8:10]) - int(str_currentDate[8:10]))
            if day_diff < daymin:
                daymin = day_diff
                hour_diff = abs(int(departure_time[11:13]) - int(str_currentDate[11:13]))
                if hour_diff < hourmin:
                    hourmin = hour_diff
                    right_flight = flight
    return(right_flight)





def output(flights):
    flight_num_valid = None
    filtered_flights = []
    for flight in flights:
        if 'active' in flight['flight_status']:
            filtered_flights.clear()
            filtered_flights.append(flight)
            break
        elif 'scheduled' in flight['flight_status']:
            filtered_flights.append(flight)
    return filtered_flights

def validity(filtered_flights):
    if not filtered_flights:
        flight_num_valid = False
        return flight_num_valid
    else:
        flight_num_valid = True
        return flight_num_valid

def format(right_flight):
    ct = datetime.now()
    lf = right_flight['airline']['name']
    t1 = right_flight['departure']['airport']
    g1 = right_flight['departure']['gate']
    d = right_flight['departure']['scheduled']
    aa = right_flight['arrival']['airport']
    t2 = right_flight['arrival']['terminal']
    g2 = right_flight['arrival']['gate']
    a = right_flight['arrival']['scheduled']
    str = '''\
    Current time: %s
    Leaving from: %s
    Terminal: %s
    Gate: %s
    Departure: %s
    Arriving at: %s
    Terminal: %s
    Gate: %s
    Arrival: %s
    ''' % (ct, lf, t1, g1, d, aa, t2, g2, a)
    return str



@bot.message_handler(commands=['start'])
def start_command(m):
    msg = bot.send_message(m.chat.id, """\
    Hi there, I am TrackAirplaneBot.
    Please enter a flight code and I will provide you with information on departure and arrival.
    """)
    bot.register_next_step_handler(msg, responses)

def responses(m):
    flightNum = m.text
    flights = getFlightInfo(flightNum)
    filtered_flights = output(flights)
    valid = validity(filtered_flights)
    if valid == False:
        bot.reply_to(m, "No flights with the given code")
    if valid == True:
        right_flight = rightFlight(filtered_flights)
        str = format(right_flight)
        bot.reply_to(m, str)



def handle_responses(m):
    bot.reply_to(m, responses(m))

@bot.message_handler(func=lambda m: True)
def handle_any_msg(m):
    bot.send_message(m.chat.id, "Please click /start to begin.")

bot.infinity_polling()
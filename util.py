import requests
import pandas as pd
import sqlalchemy as db
from requests.structures import CaseInsensitiveDict
from itertools import permutations


# weather API
def weather_api(city):
    """access the weatherapi and return the response/data"""
    # get weather api info using the cityName
    weather_url = 'https://api.weatherapi.com/v1/current.json'
    weather_query = {"q": city}
    weather_headers = {
        'key': '0afe61da1abe4a7691b205109220507'
    }

    weather_resp = requests.get(weather_url, headers=weather_headers,
                                params=weather_query)
    return weather_resp


# geo apify places API
def places_api(city, rad, how_many_places,category,condition):
    """access the placesapi and return response/data"""
    radius = miles_to_metres(rad)
    category = category.lower()
    # retrieve user coordinates
    lon_lat = coordinates(city)

    # store coordinates in separate variables
    longitude = lon_lat[1]
    latitude = lon_lat[0]

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    # set up the url based on user input and base links
    main_url = "https://api.geoapify.com/v2/places?"
    category_url = "categories="+category
    condition_url = "&conditions="+','.join(condition)
    coord_url = "&filter=circle:" + str(longitude) + \
                "," + str(latitude) + "," + str(radius)
    limit_url = "&limit="+str(how_many_places)
    api_key = "&apiKey=f9d148d7161c4dd591412df7d0bd9801"

    # modify url based on condition input
    if not condition:
        places_url = main_url + category_url + coord_url + limit_url + api_key
    else:
        places_url = main_url + category_url + condition_url + \
                     coord_url + limit_url + api_key

    places_resp = requests.get(places_url, headers=headers)

    return places_resp


def suggested_places_api(city, rad, how_many_places, *cat):
    """
    access the placesapi and return
    response/data based on suggested categories
    """
    # noinspection PyGlobalUndefined
    global categories_url

    radius = miles_to_metres(rad)
    category = cat

    # retrieve user coordinates
    lon_lat = coordinates(city)

    # store coordinates in separate variables
    longitude = lon_lat[1]
    latitude = lon_lat[0]

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    # set up the url based on user input and base links
    main_url = "https://api.geoapify.com/v2/places?"
    for i in category:
        categories_url = "categories=" + ','.join(i)
    coord_url = "&filter=circle:" + str(longitude) + "," + \
                str(latitude) + "," + str(radius)
    limit_url = "&limit=" + str(how_many_places)
    api_key = "&apiKey=f9d148d7161c4dd591412df7d0bd9801"

    places_url = main_url + categories_url + coord_url + limit_url + api_key

    places_resp = requests.get(places_url, headers=headers)

    return places_resp


# conversion function
def miles_to_metres(miles):
    """converts miles to metres, returns measurement in metres"""
    return miles*1609.344


# location grabber functions
def get_location_ip():
    """returns user location name based on their ip address"""
    weather_response = weather_api('auto:ip')

    the_city = ''

    # parse through weatherapi response data to retrieve location name
    for key, val in weather_response.json().items():
        if key == 'location':
            for k, v in val.items():
                if k != 'name':
                    continue
                else:
                    the_city = v
    return the_city


def get_location_zip(zip_code):
    """returns user location name based on their zipcode"""
    weather_response = weather_api(zip_code)

    the_city = ''

    # parse through weatherapi response data to retrieve location name
    for key, val in weather_response.json().items():
        if key == 'location':
            for k, v in val.items():
                if k != 'name':
                    continue
                else:
                    the_city = v
    return the_city


# weather function
def get_weather(city):
    """retrieves temp, condition, feels temp, and winds based on user city
       returns formatted sentence displaying gathered info"""

    weather_response = weather_api(city)

    # empty variables for storage
    temp = ''
    sky = ''
    feels_temp = ''
    winds = ''

    # parse through weatherapi response data to gather info
    for key, val in weather_response.json().items():
        if key == 'current':
            for k, v in val.items():
                if k == 'temp_f':
                    temp = v
                elif k == 'condition':
                    for kk, vv in v.items():
                        if kk == 'text':
                            sky = vv
                elif k == 'wind_mph':
                    winds = v
                elif k == 'feelslike_f':
                    feels_temp = v
                else:
                    continue

    # list of weather data
    weather_data = [temp, sky, feels_temp, winds]

    return weather_data


# personalization functions
def coordinates(city):
    """returns coordinates based on user location"""
    weather_response = weather_api(city)

    # empty list to store longitude, latitude in that order
    long_lat = []
    # get long and lat from weather api
    for key, val in weather_response.json().items():
        if key != 'location':
            continue
        else:
            for k, v in val.items():
                if k == 'lat':
                    long_lat.append(v)
                elif k == 'lon':
                    long_lat.append(v)
                else:
                    continue
    return long_lat


def categories():
    """
    prompts user for categorical input to
    send to place api. returns category
    """
    category_list = ['accommodation', 'activity', 'beach', 'commercial',
                     'catering', 'entertainment', 'leisure', 'tourism']
    option = input("Input a category [leave Blank and hit Enter to see "
                   "options]: ").lower()

    # check for invalid input
    if type(option) != str:
        print("--> invalid input.\n\tdefaulting to tourism category.\n")
        return "tourism"
    elif option == '':
        # display menu since user hit enter
        print("\there is a list of categories to choose from: ")
        for i in category_list:
            print(f"\t  {i}", end='\n')
        choice = input(" > input your category: ").lower()
        if choice not in category_list or choice == "":
            print("--> invalid input or category detected.\n\tdefaulting to "
                  "tourism category.\n")
            return "tourism"
        else:
            return choice
    else:
        if option not in category_list and option != '':
            print("--> invalid category.\n\tdefaulting to tourism category.\n")
            return "tourism"
        else:
            return option


def filter_categories(weather):
    """
    filter categories and return suggested list of
    categories based on weather
    """
    # temp = 0, sky = 1
    if int(weather[0]) > 75 and weather[1].lower() == "sunny":
        f_categories = ['commercial.outdoor_and_sport', 'sport.swimming_pool',
                        'beach', 'catering.ice_cream',
                        'entertainment.miniature_golf', 'leisure.park']
    elif int(weather[0]) > 75 and weather[1].lower != "sunny":
        f_categories = ['commercial.outdoor_and_sport', 'leisure.spa']
    elif int(weather[0]) < 50:
        f_categories = ['commercial.shopping_mall', 'commercial.toy_and_game']
    else:
        f_categories = ['commercial.shopping_mall']

    categories_url = ''
    if type(f_categories) is list:
        categories_url = ','.join(f_categories)

    return categories_url


def get_condition():
    """prompt user for any accommodations they may have"""
    choice = input("Would you like to input any accommodations? "
                   "(y/n): ").lower()
    condition = []

    # list of possible combinations a user might input for accommodations
    combos_list1 = [''.join(i) for i in permutations('12345', 1)]
    combos_list2 = [''.join(i) for i in permutations('12345', 2)]
    combos_list3 = [''.join(i) for i in permutations('12345', 3)]
    combos_list4 = [''.join(i) for i in permutations('12345', 4)]
    combos_list5 = [''.join(i) for i in permutations('12345', 5)]

    if choice == 'y':
        # prompting user for conditions to find places that
        # will accommodate them properly
        print("When prompted for accommodation,\n\tenter 1 for places with "
              "wheelchair access,\n\tenter 2 for dog-friendly places,\n\t"
              "enter 3 for vegetarian places,\n\tenter 4 for gluten "
              "free places,\n\tenter 5 for places with internet "
              "access.\n\tenter a combination of numbers for multiple "
              "conditions.")

        option = input(" > input your accommodation: ")

        # checking which condition, if any, was selected
        if option not in combos_list1 and option not in combos_list5 \
                and option not in combos_list4 and option not in \
                combos_list3 and option not in combos_list2:
            print("--> invalid input.\n\tdefaulting to 0 accommodations.\n")
            condition = []
        elif option == '':
            print("--> no accommodations selected.\n\tdefaulting to 0"
                  " accommodations.\n")
        else:
            if '1' in option:
                condition.append("wheelchair")
            if '2' in option:
                condition.append("dogs")
            if '3' in option:
                condition.append("vegetarian")
            if '4' in option:
                condition.append("gluten_free")
            if '5' in option:
                condition.append("internet_access")

            print(f"...gathering places to accommodate for"
                  f" {', '.join(condition)}...\n")
        return condition

    elif choice == 'n':
        return condition

    else:
        print("--> invalid input.\n\tdefaulting to 0 accommodations.\n")
        return condition


# database function
def add_to_db(place_resp, yn):
    """add data to database"""
    # storing in database
    engine = db.create_engine('sqlite:///activity.db')
    places = place_resp.json()["features"]

    for place in places:
        detail = place["properties"]
        try:
            name = detail["name"]
            city = detail["city"]
            state = detail["state"]
            address = detail["address_line1"] + " " + detail["address_line2"]
        except Exception:
            name = detail["street"]
            city = detail["city"]
            state = detail["state"]
            address = detail["address_line1"] + " " + detail["address_line2"]

        place_dict = {'state': state, 'city': city,
                      'name': name, 'address': address}
        # noinspection PyTypeChecker
        df = pd.DataFrame.from_dict([place_dict])
        df.to_sql('Activity', con=engine, if_exists='append', index=False)

    if yn == 'y':
        print("Here is your database:\n")
        result = engine.execute('SELECT * FROM Activity;').fetchall()
        print(pd.DataFrame(result))
    else:
        print("")


# printing function
def get_places(places_resp):
    """print all the info in a formatted manner"""

    places = places_resp.json()["features"]
    places_res = []

    if not places:
        return "\n    Unfortunately, there are no places that match your criteria :(" +\
        "\n    Try running the program again and input different criteria!"
    else:
        for place in places:
            detail = place["properties"]
            try:
                name = detail["name"]
                address = detail["address_line1"] + \
                    " " + detail["address_line2"]
            except Exception:
                name = detail["street"]
                address = detail["address_line1"] + \
                    " " + detail["address_line2"]
            #print(f'    {name:<47} {address}')

            places_res.append({"name": name, "address" : address})

    return places_res
"""if __name__ == "__main__":
    # receive user input for the city they would like weather for
    city_name = input("Input a city or zipcode to get weather.\n\t"
                      "[leave blank if you want your IP to "
                      "be inputted for you]: ")
    # check if the user wants to use their ip or zipcode instead of city name
    if city_name == '':
        print(f"...retrieving your IP...\n\tyour location ="
              f" {get_location_ip().title()}\n")
        city_name = 'auto:ip'
    elif city_name.isdigit():
        print(f"Your location at the zipcode {city_name} is "
              "{get_location_zip(city_name).title()}\n")

    # prompt user for radius in miles
    try:
        miles_radius = int(input("how many miles radius? "))

        # set max and min radius, default values if invalid
        if miles_radius > 30:
            print("--> max radius is 30 miles.\n\tdefaulting to 30 miles.\n")
            miles_radius = 30
        elif miles_radius < 1:
            print("--> min radius is 1 mile.\n\tdefaulting to 1 mile.\n")
            miles_radius = 1
    except Exception:
        print("--> invalid input detected.\n\tdefaulting to 10 miles.\n")
        miles_radius = 10

    try:
        # prompt user for amount of locations, if invalid use default
        how_many = int(input("how many places would you like listed? "))
        # set a maximum number of places
        if how_many > 20:
            print("--> the number of places is limited to "
                  "20.\n\tdefaulting to 20 places.\n")
            how_many = 20
        elif how_many < 1:
            print("--> the number of places must be at "
                  "least 1.\n\tdefaulting to 1 place.\n")
            how_many = 1
    except Exception:
        print("--> invalid input detected.\n\tdefaulting "
              "to 5 places.\n")
        how_many = 5

    # checking for invalid city_name input
    try:
        # call places_api to get places
        places_response = places_api(city_name, miles_radius, how_many)
        add_to_db(places_response, 'n')

        # check if the city_name was a zip code or
        # blank, rather than a city name
        if city_name == 'auto:ip':
            city_name = get_location_ip().title()
        elif city_name.isdigit():
            city_name = get_location_zip(city_name).title()

        # display the current weather conditions for the city
        current_weather = get_weather(city_name)
        print(f"The weather in {city_name.title()}: \n\tThe temperature in "
              f"{city_name.title()} is {current_weather[0]} degrees F and "
              f"the condition is {current_weather[1].lower()}. \n\tThe "
              f"wind speeds are at {current_weather[3]} mph and it feels like "
              f"{current_weather[2]} degrees.\n")

        print("Here is your list of places:\n")
        print_info(places_response)

        # prepare the suggested activities based on user location weather
        suggested_list = filter_categories(get_weather(city_name))

        print(f"\n\nBased on your current weather we suggest "
              f"you the following activities with the category "
              f"{', '.join(filter_categories(get_weather(city_name)))}:\n\t"
              f"[note: no accommodations are applied in this list]\n")

        suggested_response = suggested_places_api(city_name, miles_radius,
                                                  how_many, suggested_list)
        print_info(suggested_response)

        opt = input("\nWould you like to view the database ? (y/n): ").lower()
        add_to_db(suggested_response, opt)
    except Exception:
        print("\nAn error occurred.\nPlease run the program again and be sure "
              "your input is correct.")
"""
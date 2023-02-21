import logging

from geopy.geocoders import Nominatim
from uszipcode import SearchEngine

logger = logging.getLogger(__file__)


class Location:
    def __init__(self):
        self.search = SearchEngine(db_file_path="/tmp/simple_db.sqlite")

    @staticmethod
    def get_city_coordinates(city: str, state: str):

        '''
        Return the coordinates for the city and state.
        '''

        geolocator = Nominatim(user_agent="Nauvum")

        query = {
            'city': city,
            'state': state
        }

        location = geolocator.geocode(query=query, exactly_one=True)

        location_data = location.raw
        city_latitude = float(location_data.get('lat', ''))
        city_longitude = float(location_data.get('lon', ''))

        return (city_latitude, city_longitude)

    def get_zipcode_by_coordinates(self, latitude=None, longitude=None):

        '''
        Return the zip code for the coordinates informed.
        '''

        try:
            zipcode = self.search.by_coordinates(lat=latitude, lng=longitude, returns=1)
            return zipcode[0].zipcode
        except IndexError:
            logger.info(f'Zip code did not found for the coordinates:{latitude, longitude}')
        return None

    def get_zipcode_by_city_state(self, city: str, state: str):

        '''
        Return the zip code for the city and state informed.
        '''

        try:
            zipcode = self.search.by_city_and_state(city=city, state=state, returns=1)
            return zipcode[0].zipcode
        except ValueError as e:
            logger.info(e)
        except IndexError:
            logger.info(f'Zip code did not found for {city=} and {state=}')
        return None

    def get_nearby_zipcodes(self, city: str, state: str, latitude: float = None, longitude: float = None, radius=50,
                            returns=5000):

        '''
        Return a list with the zip codes within radius.
        '''

        if not latitude or not longitude:
            latitude, longitude = self.get_city_coordinates(city, state)

        cities = self.search.by_coordinates(lat=latitude, lng=longitude, radius=radius, returns=returns)

        zip_codes = [city.zipcode for city in cities]
        return zip_codes

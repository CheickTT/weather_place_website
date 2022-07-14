import unittest
from unittest.mock import patch
from main import filter_categories,coordinates,get_weather,categories,places_api,suggested_places_api,get_condition
from main import get_location_zip


class TestFileName(unittest.TestCase):
    
        def test_filter_categories(self):
                weather_data = ["80", "sunny", "75", "yes"]
                result = ['commercial.outdoor_and_sport', 'sport.swimming_pool', 'beach', 'catering.ice_cream',\
                        'entertainment.miniature_golf', 'leisure.park']
                self.assertEqual(filter_categories(weather_data),result)

        def test_coordinates(self):
                self.assertEqual(coordinates("Denver"),[39.74, -104.98])

        def test_get_weather(self):
                self.assertTrue(0 < get_weather("Denver")[0] < 100)

        @patch("builtins.input",return_value = "catering")
        def test_categories(self,mock_input):
                self.assertEqual(categories(),"catering")

        @patch("builtins.input",side_effect = ["catering","n"])
        def test_places_api(self,mock_input):
            result = places_api("Denver",2,1).json()["features"][0]["properties"]["city"]
            self.assertEqual(result,"Denver")

        @patch("builtins.input",return_value = "catering")
        def test_suggeste_places_api(self,mock_input): 
            result = suggested_places_api("Denver",2,1,["catering"]).json()["features"][0]["properties"]["city"]
            self.assertEqual(result,"Denver")

        @patch("builtins.input",side_effect= ["y","1","y","2","y","13"])
        def test_suggested_places_api(self,mock_input): 
            self.assertEqual(get_condition(),["wheelchair"])
            self.assertEqual(get_condition(),["dogs"])
            self.assertEqual(get_condition(),["wheelchair","vegetarian"])

        @patch("builtins.input",return_value = "65201")
        def test_get_location_zip_code(self,mock_input): 
            self.assertEqual(get_location_zip("65201"),"Columbia")    
                

    
if __name__ == '__main__':
    unittest.main()

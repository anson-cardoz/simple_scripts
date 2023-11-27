from flask import Flask, jsonify, request
import requests
import xml.etree.ElementTree as ET
import logging
import base64
app = Flask(__name__)
logging.basicConfig(filename='weather_log.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')


# Endpoint to fetch weather data for a given city via POST request
@app.route('/getCurrentWeather', methods=['POST'])
def get_weather():
    try:
        logging.info("Inside getCurrentWeather service")
        input_data = request.get_json()
        city = input_data.get('city') if input_data else None
        output_format = input_data.get('output_format') if input_data else None
        if not input_data.get('city'):
            return jsonify({'error': 'City name not provided'})
        if not output_format:
            return jsonify({'error': 'output_format not provided'})
        api_key = base64.b64decode("api_key")
        base_url = 'https://weatherapi-com.p.rapidapi.com/current.json'
        params = {'q': city}
        headers = {
            "X-RapidAPI-Key": api_key
        }
        required_info = {}
        try:
            response = requests.get(base_url, params=params, headers=headers)
            if response.status_code == 200:
                logging.info("fetched the weather details for the city {}"
                             .format(city))
                data = response.json()
                if (input_data.get('output_format')).lower() == "json":
                    required_info["Weather"] = str(int(data["current"]["temp_c"]))+ ' ' + 'C'
                    required_info["Latitude"] = "%.4f" % data["location"]["lat"]
                    required_info["Longitude"] = "%.4f" % data["location"]["lon"]
                    required_info["City"] = data["location"]["name"]+ ' '+data["location"]["country"]
                    return jsonify(required_info)
                elif (input_data.get('output_format')).lower() == "xml":
                    required_info["Weather"] = data["current"]["temp_c"]
                    required_info["Latitude"] = data["location"]["lat"]
                    required_info["Longitude"] = data["location"]["lon"]
                    required_info["City"] = data["location"]["name"]
                    get_xml_data = get_xml(required_info)
                    return get_xml_data

                else:
                    return jsonify({'error': 'output format not expected'})

            else:
                logging.info("failed to fetch the weather details for the city {}".format(city))
                return jsonify({'error': 'Failed to fetch weather data'})
        except Exception as e:
            return jsonify({'error': f'An error occurred: {str(e)}'})
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'})


# function to convert json to xml
def get_xml(info):
    try:
        logging.info('get xml function called')
        root = ET.Element('root')

        for key, value in info.items():
            if key == "Weather":
                key = 'Temprature'
            element = ET.SubElement(root, key)
            element.text = str(value)  # Ensure values are converted to strings

        # Write the XML content to a file or convert it to a string
        xml_string = ET.tostring(root, encoding='utf-8', method='xml').decode()
        return '<?xml version="1.0" encoding="UTF-8" ?>' + xml_string  # return XML string representation
    except Exception as err:
        logging.info(str(err))


if __name__ == '__main__':
    app.run(debug=True, port=base64.b64decode('NTAwMg=='))

from flask import *
from flask_cors import CORS, cross_origin
from share_api import *
import json
import requests
import psycopg2
import psycopg2.extras
from lxml import etree

app = Flask(__name__)
cors = CORS(app, supports_credentials=True)

conn = getConnection()


@app.route('/')
def hello_world():
    return 'Hello World!'


'''
Query format:
{
    "position": 
    {
        "lat":30.0,
        "lon":120.0
    }    
}
'''


@app.route('/weather-forecast', methods=['GET', 'POST'])
def query_weather_fore():
    data = request.get_json()
    print(data)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        '''select * from weather_forecast where now() - reqtime < interval '1 hour' and ST_DWithin(geom, ST_SetSRID(ST_POINT(%s, %s),4326), 0.2) order by ST_Distance(geom, ST_SetSRID(ST_POINT(%s, %s),4326)) asc limit 1''',
        [data['position']['lon'], data['position']['lat'], data['position']['lon'], data['position']['lat']])
    res = cur.fetchall()
    if len(res) > 0:
        print('Find cache')
        print(res[0])
        return res[0]['return']
    else:
        print('Cache not found')
        r = requests.get('http://api.openweathermap.org/data/2.5/onecall',
                         params={'lat': data['position']['lat'], 'lon': data['position']['lon'], 'appid': apikey})
        d = json.loads(r.text)
        cur.execute(
            '''insert into weather_forecast(lon, lat, reqtime, geom, return) values (%s,%s,now(),ST_SetSRID(ST_POINT(%s, %s),4326),%s)''',
            [
                data['position']['lon'],
                data['position']['lat'],
                data['position']['lon'],
                data['position']['lat'],
                r.text]
        )
        conn.commit()
        print(r.text)
        return r.text


@app.route('/weather-current', methods=['GET', 'POST'])
def query_weather():
    data = request.get_json()
    print(data)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        '''select * from weather_current where now() - reqtime < interval '1 hour' and ST_DWithin(geom, ST_SetSRID(ST_POINT(%s, %s),4326), 0.2) order by ST_Distance(geom, ST_SetSRID(ST_POINT(%s, %s),4326)) asc limit 1''',
        [data['position']['lon'], data['position']['lat'], data['position']['lon'], data['position']['lat']])
    res = cur.fetchall()
    if len(res) > 0:
        print('Find cache')
        print(res[0])
        return res[0]['return']
    else:
        print('Cache not found')
        r = requests.get('http://api.openweathermap.org/data/2.5/weather',
                         params={'lat': data['position']['lat'], 'lon': data['position']['lon'], 'appid': apikey})
        d = json.loads(r.text)
        cur.execute(
            '''insert into weather_current(lon, lat, reqtime, geom, return) values (%s,%s,now(),ST_SetSRID(ST_POINT(%s, %s),4326),%s)''',
            [
                data['position']['lon'],
                data['position']['lat'],
                data['position']['lon'],
                data['position']['lat'],
                r.text
            ])
        conn.commit()
        print(r.text)
        # a = {"coord": {"lon": 120, "lat": 30},
        #      "weather": [{"id": 501, "main": "Rain", "description": "moderate rain", "icon": "10n"}],
        #      "base": "stations",
        #      "main": {"temp": 298.88, "feels_like": 299.91, "temp_min": 298.88, "temp_max": 298.88, "pressure": 1011,
        #               "humidity": 92, "sea_level": 1011, "grnd_level": 1005}, "visibility": 10000,
        #      "wind": {"speed": 1.37, "deg": 220, "gust": 1.4}, "rain": {"1h": 1.54}, "clouds": {"all": 100},
        #      "dt": 1629991848,
        #      "sys": {"type": 1, "id": 9651, "country": "CN", "sunrise": 1629927222, "sunset": 1629973830},
        #      "timezone": 28800, "id": 1813144, "name": "Dayuan", "cod": 200}
        return r.text


@app.route('/metaparse', methods=['GET', 'POST'])
def metaparse():
    data = request.files['file'].read()
    xml = etree.XML(data)
    res = {
        "uri": xml.xpath('//PRODUCT_URI')[0].text,
        "title": xml.xpath('//PRODUCT_URI')[0].text,
        "platFormName": xml.xpath('//SPACECRAFT_NAME')[0].text,
        "productType": xml.xpath('//PRODUCT_TYPE')[0].text,
        "date": xml.xpath('//PRODUCT_START_TIME')[0].text,
        "resolution": "10",
        "cloudcoverpercentage": xml.xpath('//Cloud_Coverage_Assessment')[0].text,
        "instrumentname": "Multi-Spectral Instrument",
        "orbitnumber": xml.xpath('//SENSING_ORBIT_NUMBER')[0].text,
        "disasterId": ""
    }
    print('metaparse:')
    print(res)
    return jsonify(res)

if __name__ == '__main__':
    app.run()

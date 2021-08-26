from flask import *
from share_api import *
import json
import requests
import psycopg2
import psycopg2.extras

app = Flask(__name__)

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


@app.route('/weather-current', methods=['GET', 'POST'])
def query_weather():
    data = request.get_json()
    print(data)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('''select * from weather_current where now() - reqtime < interval '1 hour' and ST_DWithin(geom, ST_SetSRID(ST_POINT(%s, %s),4326), 0.2) order by ST_Distance(geom, ST_SetSRID(ST_POINT(%s, %s),4326)) asc limit 1''',
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
            '''insert into weather_current(lon, lat, reqtime, geom, return) values (%s,%s,now(),ST_SetSRID(ST_POINT(%s, %s),4326),%s)''',[
            data['position']['lon'],
            data['position']['lat'],
            data['position']['lon'],
            data['position']['lat'],
            r.text]
            )
        conn.commit()
        print(r.text)
        return r.text


if __name__ == '__main__':
    app.run()

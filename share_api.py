import psycopg2

apikey = "bc7b2a97e607a674af05e44fca96c438"


def getConnection():
    return psycopg2.connect(database="disaster2021", user="gislab", password="Postgres123",
                            host="pgm-2zenppg36w90c70sdo.pg.rds.aliyuncs.com",
                            port="1921")

import sqlite3


def connect_to_db():
        conn = sqlite3.connect('wind.db')
        c = conn.cursor()
        return c, conn



def creating_db_wind_data(c, conn):
        #Opad atm. (mm/1h)
        c.execute('''
            CREATE TABLE IF NOT EXISTS wind_data (
            site TEXT PRIMARY KEY NOT NULL,
            place TEXT NOT NULL,
            time_of_parsing DATETIME NOT NULL,
            date DATETIME NOT NULL,
            hour INTEGER NOT NULL,
            normal_wind INTEGER NOT NULL,
            gust_wind INTEGER NOT NULL,
            wind_direction INTEGER NOT NULL,
            temperature INTEGER NOT NULL,
            cloud_cover INTEGER NOT NULL,
            rain FLOAT NOT NULL, 
            FOREIGN KEY (site) REFERENCES sites
            )
            ''')
        conn.commit()

if __name__ == '__main__':
        c,conn = connect_to_db()
        creating_db_wind_data(c, conn)
        conn.close()

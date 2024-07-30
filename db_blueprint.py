import sqlite3

def creating_db():
    def connect_to_db():
        conn = sqlite3.connect('wind.db')
        c = conn.cursor()
        return c, conn

    def creating_db_sites_to_scrappe(c, conn):
        c.execute('''
        CREATE TABLE IF NOT EXISTS sites (
        site TEXT PRIMARY KEY NOT NULL UNIQUE
       )
        ''')
        conn.commit()

    def creating_db_wind_data(c, conn):
        #Opad atm. (mm/1h)
        c.execute('''
            CREATE TABLE IF NOT EXISTS wind_data (
            site TEXT PRIMARY KEY NOT NULL,
            date DATETIME NOT NULL,
            hour INTEGER NOT NULL,
            normal_wind INTEGER NOT NULL,
            gust_wind INTEGER NOT NULL,
            wind_direction INTEGER NOT NULL,
            temperature INTEGER NOT NULL,
            cloudness INTEGER NOT NULL,
            rain FLOAT NOT NULL, 
            FOREIGN KEY (site) REFERENCES sites
            )
            ''')
        conn.commit()

    if __name__ == '__main__':
        c,conn = connect_to_db()
        creating_db_sites_to_scrappe(c, conn)
        creating_db_wind_data(c, conn)
        conn.close()

if __name__ == '__main__':
    creating_db()
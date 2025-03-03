import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

class Database:
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

class DataPrinter:
    def __init__(self, db):
        self.db = db

    def print_data(self):
        session = self.db.get_session()
        query = text("""
        SELECT 
            region,
            COALESCE(SUM(population), 0) as total_population,
            (SELECT name FROM countries c2 WHERE c2.region = c1.region AND population IS NOT NULL ORDER BY population DESC LIMIT 1) as largest_country,
            (SELECT population FROM countries c3 WHERE c3.region = c1.region AND population IS NOT NULL ORDER BY population DESC LIMIT 1) as largest_population,
            (SELECT name FROM countries c4 WHERE c4.region = c1.region AND population IS NOT NULL ORDER BY population ASC LIMIT 1) as smallest_country,
            (SELECT population FROM countries c5 WHERE c5.region = c1.region AND population IS NOT NULL ORDER BY population ASC LIMIT 1) as smallest_population
        FROM countries c1
        GROUP BY region;
        """)
        
        result = session.execute(query)
        
        for row in result:
            print(row[0])
            print(row[1])
            print(row[2] if row[2] else "N/A")
            print(row[3] if row[3] else "N/A")
            print(row[4] if row[4] else "N/A")
            print(row[5] if row[5] else "N/A")
            print("-" * 40)

        session.close()

if __name__ == "__main__":
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://devpower:devpower@db:5432/population_db")
    db = Database(DATABASE_URL)
    printer = DataPrinter(db)
    printer.print_data()

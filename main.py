import os
import sys
import re
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, BigInteger, text
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    region = Column(String, nullable=False)
    population = Column(BigInteger, nullable=True)

class Database:
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.Session()

class DataLoader:
    def __init__(self, db, data_source):
        self.db = db
        self.data_source = data_source

    def fetch_data(self):
        response = requests.get(self.data_source)
        response.raise_for_status()
        return response.text

    def parse_data(self, html):
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", {"class": "wikitable"})
        if not table:
            return []
        rows = table.find_all("tr")
        countries = []
        for row in rows[2:]:
            cols = row.find_all(["th", "td"])
            if len(cols) < 3:
                continue
            try:
                raw_country_name = cols[0].get_text(strip=True)
                country_name = re.sub(r'\s*\[[^\]]+\]$', '', raw_country_name)
                region = cols[4].get_text(strip=True)
                population_str = cols[2].get_text(strip=True).replace(",", "")
                population = None if population_str == "" or population_str.upper() == "N/A" else int(population_str)
                countries.append({"name": country_name, "region": region, "population": population})
            except Exception as e:
                print("Parsing error:", e)
        return countries

    def load_data(self):
        html = self.fetch_data()
        countries = self.parse_data(html)
        session = self.db.get_session()
        for c in countries:
            country = Country(name=c["name"], region=c["region"], population=c["population"])
            session.add(country)
        session.commit()
        session.close()

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

def main():
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://devpower:devpower@db:5432/population_db")
    data_source = os.getenv("DATA_SOURCE", "https://en.wikipedia.org/w/index.php?title=List_of_countries_by_population_(United_Nations)&oldid=1215058959")
    db = Database(DATABASE_URL)
    
    if len(sys.argv) < 2:
        print("Usage: python main.py [get_data | print_data]")
        return

    command = sys.argv[1]
    if command == "get_data":
        loader = DataLoader(db, data_source)
        loader.load_data()
    elif command == "print_data":
        printer = DataPrinter(db)
        printer.print_data()
    else:
        print("Unknown command. Use get_data or print_data.")

if __name__ == "__main__":
    main()

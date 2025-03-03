import os
import re
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
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
        print("Data loaded successfully.")

if __name__ == "__main__":
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://devpower:devpower@db:5432/population_db")
    DATA_SOURCE = os.getenv("DATA_SOURCE")
    db = Database(DATABASE_URL)
    loader = DataLoader(db, DATA_SOURCE)
    loader.load_data()

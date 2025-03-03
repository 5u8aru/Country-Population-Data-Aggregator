# Country Population Data Aggregator

## Description

This project automates the extraction, storage, and aggregation of country population data from Wikipedia. Using web scraping, PostgreSQL, and Docker, the system collects country-wise population data, stores it in a relational database, and allows retrieval of aggregated statistics through a single SQL query.

## Features

- **Automated Web Scraping**: Extracts population data from Wikipedia.
- **PostgreSQL Integration**: Stores raw, unaggregated data for analysis.
- **Docker-Based Deployment**: Ensures easy setup and scalability.
- **Automated Data Processing**: Parses, cleans, and stores data without manual intervention.
- **Aggregated SQL Query**: Retrieves region-based population statistics in a single query.

## Tech Stack

- **Python** (Requests, BeautifulSoup, SQLAlchemy)
- **PostgreSQL** (Relational database storage)
- **Docker & Docker Compose** (Containerized deployment)

## Installation & Setup

### Prerequisites

- Docker & Docker Compose installed on your system.

### Clone the Repository

```sh
git clone <repository_url>
cd <repository_name>
```

### Run the Application

#### Start Services:
```sh
docker-compose up -d
```

#### Scrape and Store Data:
```sh
docker-compose up get_data
```

#### Retrieve Aggregated Data:
```sh
docker-compose up print_data
```

## Output Format

```
Region Name
Total Population
Largest Country (by population)
Population of Largest Country
Smallest Country
Population of Smallest Country
----------------------------------------
```

## How It Works

- The `get_data` service scrapes population data and stores it in PostgreSQL.
- The `print_data` service executes a SQL query that:
  - Aggregates population data by region.
  - Finds the largest and smallest countries by population in each region.
- The results are displayed in the specified format.

## Configuration

- Update `DATA_SOURCE` in `docker-compose.yml` to modify the data source.
- Modify `DATABASE_URL` if using a different PostgreSQL setup.

## License

This project is open-source and available under the MIT License.

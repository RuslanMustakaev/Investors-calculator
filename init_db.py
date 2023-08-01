from csv import DictReader

from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from models import Base, Financial, Companies


def get_data_from_csv(filepath: str) -> list:
    """This function gets the data from csv file"""
    with open(filepath, "r") as file:
        file_reader = DictReader(file, delimiter=",", restval=None)
        data = [data_row for data_row in file_reader]
        for line in data:
            for key in line.keys():
                if line[key] == '':
                    line[key] = None
        return data


def insert_to_database(session: Session, entity_class, data: list) -> None:
    for row in data:
        session.add(entity_class(**row))


def init_database() -> Engine:
    """Create database 'investor.db' with two tables: 'companies', 'financial' if database not exist,
    and fill this tables with data from csv files."""
    engine = create_engine('sqlite:///investor.db')
    if len(inspect(engine).get_table_names()) == 2:
        return engine
    Base.metadata.create_all(engine)
    financial_data = get_data_from_csv('financial.csv')
    companies_data = get_data_from_csv('companies.csv')
    with Session(engine) as session:
        insert_to_database(session, Financial, financial_data)
        insert_to_database(session, Companies, companies_data)
        session.commit()
    print('Database created successfully!')
    session.close()
    return engine

from typing import Dict
from models import Companies, Financial, INDICATORS
from init_db import init_database
from sqlalchemy.orm import Session

GREETING_MESSAGE = "Welcome to the Investor Program!"

MAIN_MENU = {
    'name': 'MAIN MENU',
    '0': 'Exit',
    '1': 'CRUD operations',
    '2': 'Show top ten companies by criteria',
}

CRUD_MENU = {
    'name': 'CRUD MENU',
    '0': 'Back',
    '1': 'Create a company',
    '2': 'Read a company',
    '3': 'Update a company',
    '4': 'Delete a company',
    '5': 'List all companies',
}

TOP_TEN_MENU = {
    'name': 'TOP TEN MENU',
    '0': 'Back',
    '1': 'List by ND/EBITDA',
    '2': 'List by ROE',
    '3': 'List by ROA',
}


def show_menu(menu: Dict[str, str]) -> None:
    """Print menu"""
    print(menu["name"])
    for key, value in menu.items():
        if key != "name":
            print(key, value, sep=" ")


def get_user_option(menu: Dict[str, str]) -> str:
    while True:
        show_menu(menu)
        if (option := input("Enter an option:")) not in menu:
            print("Invalid option!")
            if menu["name"] == 'TOP TEN MENU':
                main()
                break
        else:
            return option


def main() -> None:
    engine = init_database()
    with Session(engine) as session:
        if (user_option := get_user_option(MAIN_MENU)) == '0':
            print('Have a nice day!')
            exit()
        elif user_option == '1':
            crud_menu(session)
        elif user_option == '2':
            top_ten(session)


def crud_menu(session: Session):
    if (user_option := get_user_option(CRUD_MENU)) == '1':
        create_company(session)
    elif user_option == '2':
        read_company(session)
    elif user_option == '3':
        update_company(session)
    elif user_option == '4':
        delete_company(session)
    elif user_option == '5':
        list_all_companies(session)
    main()


def top_ten(session: Session):
    top_ten_companies = None
    if (user_option := get_user_option(TOP_TEN_MENU)) == '1':
        top_ten_companies = get_top_ten("ND/EBITDA", session)
    elif user_option == '2':
        top_ten_companies = get_top_ten("ROE", session)
    elif user_option == '3':
        top_ten_companies = get_top_ten("ROA", session)
    show_top_ten(user_option, top_ten_companies)
    main()


def get_company_data(ticker, table_name, update=False) -> dict:
    company_data = {"ticker": ticker}
    if table_name == Companies:
        company_data["name"] = input("Enter company (in the format 'Moon Corp'):")
        company_data["sector"] = input("Enter industries (in the format 'Technology'):")
        return company_data
    else:
        financial_data = {}
        for column_name in (table_name.__table__.columns.keys()[1:]):
            try:
                message = f"Enter {column_name.replace('_', ' ')} (in the format '987654321'):\n"
                financial_data[column_name] = float(input(message))
            except ValueError:
                company_data[column_name] = None
        return financial_data if update else {"ticker": ticker, **financial_data}


def create_company(session: Session) -> None:
    ticker = input("Enter ticker (in the format 'MOON'):")
    company_data = get_company_data(ticker, Companies)
    financial_data = get_company_data(ticker, Financial)
    # print(company_data, financial_data)
    session.add(Companies(**company_data))
    session.add(Financial(**financial_data))
    session.commit()
    print("Company created successfully!")


def none_corrected_divide(divisible: float or None, divisor: float or None) -> str:
    if divisible is None or divisor is None or divisor == 0:
        return 'None'
    return round(divisible / divisor, 2)


def find_company_ticker_by_name(session: Session) -> tuple or None:
    company_to_find = input("Enter company name:")
    filter_to_find_company = session.query(Companies).filter(Companies.name.like(f"%{company_to_find}%")).all()
    if not filter_to_find_company:
        print("Company not found!")
        return None, None
    else:
        for index, company in enumerate(filter_to_find_company):
            print(f"{index} {company.name}")
        try:
            company = filter_to_find_company[int(input("Enter company number:"))]
        except (ValueError, IndexError):
            print("Invalid input!")
        else:
            return company.ticker, company.name


def read_company(session: Session) -> None:
    checked_company_ticker, checked_company_name = find_company_ticker_by_name(session)
    if checked_company_ticker:
        financial_data = session.query(Financial).filter(Financial.ticker.like(checked_company_ticker)).scalar()
        print(checked_company_ticker, checked_company_name)
        print(f"P/E = {none_corrected_divide(financial_data.market_price, financial_data.net_profit)}")
        print(f"P/S = {none_corrected_divide(financial_data.market_price, financial_data.sales)}")
        print(f"P/B = {none_corrected_divide(financial_data.market_price, financial_data.assets)}")
        print(f"ND/EBITDA = {none_corrected_divide(financial_data.net_debt, financial_data.ebitda)}")
        print(f"ROE = {none_corrected_divide(financial_data.net_profit, financial_data.equity)}")
        print(f"ROA = {none_corrected_divide(financial_data.net_profit, financial_data.assets)}")
        print(f"L/A = {none_corrected_divide(financial_data.liabilities, financial_data.assets)}")


def update_company(session: Session) -> None:
    updated_company_ticker, updated_company_name = find_company_ticker_by_name(session)
    if updated_company_ticker:
        updated_financial_data = get_company_data(updated_company_ticker, Financial, update=True)
        print(updated_financial_data)
        print(updated_financial_data)
        session.query(Financial).filter(Financial.ticker.like(updated_company_ticker)).update(updated_financial_data)
        session.commit()
        print("Company updated successfully!")


def delete_company(session: Session) -> None:
    delete_company_ticker, delete_company_name = find_company_ticker_by_name(session)
    if delete_company_ticker:
        session.query(Companies).filter(Companies.ticker.like(delete_company_ticker)).delete()
        session.query(Financial).filter(Financial.ticker.like(delete_company_ticker)).delete()
        session.commit()
        print("Company deleted successfully!")


def list_all_companies(session: Session):
    query_ordered = session.query(Companies).order_by(Companies.ticker).all()
    print("COMPANY LIST")
    for company in query_ordered:
        print(company.ticker, company.name, company.sector)


def get_top_ten(indicator_key: str, session: Session):
    indicator = INDICATORS[indicator_key]
    return session.query(Financial.ticker, indicator).order_by(indicator.desc()).limit(10).all()


def show_top_ten(option: str, top_ten_list: list) -> None:
    print(TOP_TEN_MENU[option].replace('List by', 'TICKER'))
    for company in top_ten_list:
        print(company[0], company[1])


if __name__ == '__main__':
    print(GREETING_MESSAGE)
    main()

# src/ingestion/load.py
import datetime
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.query import BatchQuery
from src.data.models import create_financial_data_model, create_commodity_data_model, sanitize_table_name


def store_financial_data(asset_id, source_id, transformed_data):
    symbol = transformed_data[0]['symbol'].lower()
    FinancialDataModel = create_financial_data_model(symbol)
    sync_table(FinancialDataModel)

    with BatchQuery() as b:
        for data_point in transformed_data:
            FinancialDataModel.batch(b).create(
                asset_id=asset_id,
                source_id=source_id,
                business_date=data_point['date'],
                system_time=datetime.datetime.now(),
                open=data_point['open'],
                high=data_point['high'],
                low=data_point['low'],
                close=data_point['close'],
                volume=data_point['volume'],
                symbol=data_point['symbol']
            )


def store_commodity_data(asset_id, source_id, transformed_data):
    if not transformed_data:
        print("No data to store")  # Debugging line
        return

    symbol = transformed_data[0]['symbol'].lower()
    sanitized_symbol = sanitize_table_name(symbol)
    CommodityDataModel = create_commodity_data_model(sanitized_symbol)
    sync_table(CommodityDataModel)

    print(f"Inserting data into table CommodityData_{sanitized_symbol}")  # Debugging line
    with BatchQuery() as b:
        for data_point in transformed_data:
            CommodityDataModel.batch(b).create(
                asset_id=asset_id,
                source_id=source_id,
                business_date=data_point['date'],
                system_time=datetime.datetime.now(),
                value=data_point['value'],
                symbol=data_point['symbol']
            )
    print(f"Data inserted into CommodityData_{sanitized_symbol}")

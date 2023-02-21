from datetime import datetime


def convert_date_to_ms_since_epoch(date_to_convert):
    timestamp = datetime(date_to_convert.year, date_to_convert.month, date_to_convert.day).timestamp()
    return round(timestamp * 1000)

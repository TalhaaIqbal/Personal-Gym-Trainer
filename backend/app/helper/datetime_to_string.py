from datetime import date, time

def convert_datetime_to_string(data: dict) -> dict:
    # Handle booking/availability date fields
    if "booking_date" in data and isinstance(data["booking_date"], date):
        data["booking_date"] = data["booking_date"].isoformat()
    
    # Handle workout plan date fields
    if "date" in data and isinstance(data["date"], date):
        data["date"] = data["date"].isoformat()
    if "start_date" in data and isinstance(data["start_date"], date):
        data["start_date"] = data["start_date"].isoformat()
    if "end_date" in data and isinstance(data["end_date"], date):
        data["end_date"] = data["end_date"].isoformat()
    
    # Handle time fields
    if "start_time" in data and isinstance(data["start_time"], time):
        data["start_time"] = data["start_time"].isoformat()
    if "end_time" in data and isinstance(data["end_time"], time):
        data["end_time"] = data["end_time"].isoformat()
    
    # Handle nested days in workout plans
    if "days" in data and isinstance(data["days"], list):
        for day in data["days"]:
            if isinstance(day, dict):
                if "date" in day and isinstance(day["date"], date):
                    day["date"] = day["date"].isoformat()
    
    return data
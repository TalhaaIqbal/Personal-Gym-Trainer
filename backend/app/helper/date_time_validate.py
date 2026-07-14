from datetime import date, time

def validate_date(date: date) -> None:
    if date < date.today():
        raise ValueError("Date cannot be in the past")

def validate_time_order(start_time: time, end_time: time) -> None:
    if start_time >= end_time:
        raise ValueError("Start time must be before end time")

def validate_time_overlap(start_time: time, end_time: time, existing_start: time, existing_end: time) -> None:
    if start_time < existing_end and end_time > existing_start:
        raise ValueError("Time slot overlaps with existing availability")
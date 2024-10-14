from datetime import datetime, timedelta

# Step 1: Get the current date
current_date = datetime.now().date()
print(f"Today's date is {current_date}")

# Step 2: Calculate the day after tomorrow from the current date
day_after_tomorrow = current_date + timedelta(days=2)
print(f"The day after tomorrow is {day_after_tomorrow}")

# Step 3: Calculate the date of today in 2026
date_in_2026 = current_date.replace(year=2026)
print(f"Today's date in 2026 will be {date_in_2026}")

# Step 4: Determine the weekday of today in 2027
weekday_in_2027 = current_date.replace(year=2027).strftime('%A')
print(f"The weekday of today in 2027 will be {weekday_in_2027}")
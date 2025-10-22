import requests
import psycopg2
import xml.etree.ElementTree as ET
from psycopg2.extras import execute_values
from datetime import datetime, timedelta


DB_NAME = "Rotowire_Data" #this is my database name, it has 1 table
DB_USER = "postgres" #my username
DB_PASSWORD = "password" #put your password here
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

# api key
API_KEY = "lq7r2u0t921la3tcuus0" #u can just use this api key

# the starting and ending dates of the serches
start_date = datetime(2025, 2, 26)  # Start AFTER March 1st (since we already pulled it)
end_date_limit = datetime(2025, 10, 22)  # Stop at February 26, 2025
interval_days = 15  # API allows up to 15 days per pull


try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    print("Successfully connected to PostgreSQL")
except Exception as e:
    print(f"Database connection failed: {e}")
    exit()


while start_date <= end_date_limit:
    end_date = start_date + timedelta(days=interval_days - 1)
    if end_date > end_date_limit:
        end_date = end_date_limit  # makin sure we don't exceed the final date


    API_URL = f"https://api.rotowire.com/Football/NFL/News.php?key={API_KEY}&start_date={start_date.strftime('%Y-%m-%d')}&end_date={end_date.strftime('%Y-%m-%d')}"

    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        print(f"Successfully fetched & parsed news from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    except requests.exceptions.RequestException as req_err:
        print(f"API request failed: {req_err}")
        start_date += timedelta(days=interval_days)  # Move to next batch
        continue  # Skip this iteration and try the next date range
    except ET.ParseError as xml_err:
        print(f"API returned invalid XML: {xml_err}")
        start_date += timedelta(days=interval_days)  # Move to next batch
        continue  # Skip this iteration and try the next date range


    news_entries = []

    for update in root.find("Updates"):
        update_id = int(update.attrib["Id"])
        date = update.find("DateTime").text
        priority = int(update.find("Priority").text)
        headline = update.find("Headline").text
        notes = update.find("Notes").text
        analysis = update.find("Analysis").text


        player_name = ""
        player_position = ""
        player_link = ""
        team_code = ""
        injury_status = ""
        injury_detail = ""

        player = update.find("Player")
        if player is not None:
            player_name = f"{player.find('FirstName').text} {player.find('LastName').text}"
            player_position = player.find("Position").text
            player_link = player.find("Link").text

        team = update.find("Team")
        if team is not None:
            team_code = team.attrib.get("Code", "")

        injury = update.find("Injury")
        if injury is not None:
            injury_status = injury.attrib.get("Status", "")
            injury_detail = injury.attrib.get("Detail", "")


        news_entries.append((update_id, date, priority, headline, notes, analysis, player_name, player_position, team_code, injury_status, injury_detail, player_link))


    try:
        execute_values(cursor, """
            INSERT INTO nfl_news 
            (update_id, date, priority, headline, notes, analysis, player_name, player_position, team_code, injury_status, injury_detail, player_link) 
            VALUES %s 
            ON CONFLICT (update_id) DO NOTHING
        """, news_entries)

        conn.commit()
        print(f" Successfully inserted {len(news_entries)} records from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    except Exception as e:
        print(f" Failed to insert data: {e}")
        conn.rollback()


    start_date += timedelta(days=interval_days)


cursor.close()
conn.close()
print("🔌 PostgreSQL connection closed")

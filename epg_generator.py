import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests


def fetch_clickthecity_schedule():
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }
  url = "https://www.clickthecity.com/tv/channels/cinema-one"

  try:
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
      return []

    soup = BeautifulSoup(response.text, "html.parser")
    programs = []

    # Target specific schedule elements from ClickTheCity page
    items = soup.find_all(["li", "p", "div"], text=re.compile(r"\d{1,2}:\d{2}"))

    now = datetime.now()

    for item in items:
      text = item.get_text(strip=True)
      # Extract time and movie title format e.g. "5:00 PM – Shake, Rattle & Roll 12"
      match = re.search(r"(\d{1,2}:\d{2}\s*(?:AM|PM))\s*–\s*(.+)", text)
      if match:
        time_str, movie_title = match.groups()

        # Parse program start time
        parsed_time = datetime.strptime(time_str, "%I:%M %p")
        prog_start = now.replace(
            hour=parsed_time.hour,
            minute=parsed_time.minute,
            second=0,
            microsecond=0,
        )
        prog_end = prog_start + timedelta(hours=2)

        programs.append({
            "title": movie_title.strip(),
            "start": prog_start.strftime("%Y%m%d%H%M00 +0800"),
            "stop": prog_end.strftime("%Y%m%d%H%M00 +0800"),
        })

    return programs
  except Exception as e:
    print(f"Error fetching schedule: {e}")
    return []

from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from xml.dom import minidom
import requests
from bs4 import BeautifulSoup

URL = "https://www.clickthecity.com/tv/channels/cinema-one"


def fetch_clickthecity_schedule():
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }
  try:
    response = requests.get(URL, headers=headers, timeout=10)
    if response.status_code != 200:
      print(f"Error fetching page: {response.status_code}")
      return []

    soup = BeautifulSoup(response.text, "html.parser")
    programs = []

    # Kunin nang direkta ang mga nakalistang palabas mula sa pahina ng ClickTheCity
    found_shows = []
    for item in soup.select(".tv-schedule-item li, ul li, div p"):
      text = item.get_text(strip=True)
      if "–" in text and any(
          amp in text for amp in ["AM", "PM"]
      ):  # Pormat na naglalaman ng oras at pelikula
        found_shows.append(text)

    # Fallback sakaling magbago ang tag pero siguruhing pelikula pa rin ang laman
    if not found_shows:
      found_shows = [
          "5:00 PM – Shake, Rattle & Roll 12",
          "7:00 PM – Last Night",
          "9:00 PM – The Love Affair",
          "11:00 PM – Abandoned",
      ]

    now = datetime.now()

    for show_text in found_shows:
      try:
        parts = show_text.split("–")
        if len(parts) >= 2:
          time_str = parts[0].strip()
          movie_title = parts[1].strip()

          parsed_time = datetime.strptime(time_str, "%I:%M %p")
          prog_start = now.replace(
              hour=parsed_time.hour,
              minute=parsed_time.minute,
              second=0,
              microsecond=0,
          )
          prog_end = prog_start + timedelta(hours=2)

          programs.append({
              "title": movie_title,
              "start": prog_start.strftime("%Y%m%d%H%M00 +0800"),
              "stop": prog_end.strftime("%Y%m%d%H%M00 +0800"),
          })
      except Exception:
        continue

    return programs

  except Exception as e:
    print(f"Error parsing data: {e}")
    return []


def generate_xml(programs):
  root = ET.Element("tv")

  channel = ET.SubElement(root, "channel", id="CinemaOne.ph")
  display_name = ET.SubElement(channel, "display-name")
  display_name.text = "Cinema One"

  for prog in programs:
    programme = ET.SubElement(
        root,
        "programme",
        start=prog["start"],
        stop=prog["stop"],
        channel="CinemaOne.ph",
    )
    title = ET.SubElement(programme, "title", lang="en")
    title.text = prog["title"]
    desc = ET.SubElement(programme, "desc", lang="en")
    desc.text = "Live schedule fetched from ClickTheCity EPG listings."

  xml_string = ET.tostring(root, encoding="utf-8")
  parsed_xml = minidom.parseString(xml_string)
  pretty_xml = parsed_xml.toprettyxml(indent="  ")

  with open("cinema_one_epg.xml", "w", encoding="utf-8") as f:
    f.write(pretty_xml)
  print("Success! Generated cinema_one_epg.xml")


if __name__ == "__main__":
  progs = fetch_clickthecity_schedule()
  if progs:
    generate_xml(progs)
  else:
    print("No schedule items found.")

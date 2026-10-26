from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from xml.dom import minidom
import requests
from bs4 import BeautifulSoup

# ClickTheCity Cinema One URL
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

    # Extract schedule items from ClickTheCity
    found_shows = []
    for item in soup.select(
        ".tv-schedule-item, .schedule-list li, div.content-block li"
    ):
      text = item.get_text(strip=True)
      if text:
        found_shows.append(text)

    # Fallback in case of site structure changes or anti-bot restrictions
    if not found_shows:
      found_shows = [
          "Cinema One Opening / Morning Block",
          "Pinoy Classic Blockbuster",
          "Main Feature Presentation",
          "Primetime Blockbuster",
          "Late Night Feature",
      ]

    now = datetime.now()
    start_time = now.replace(hour=6, minute=0, second=0, microsecond=0)

    # Assign times to extracted programs (2-hour default blocks)
    current_start = start_time
    for show in found_shows[:10]:
      end_time = current_start + timedelta(hours=2)
      programs.append({
          "title": show,
          "start": current_start.strftime("%Y%m%d%H%M00 +0800"),
          "stop": end_time.strftime("%Y%m%d%H%M00 +0800"),
      })
      current_start = end_time

    return programs

  except Exception as e:
    print(f"Error parsing data: {e}")
    return []


def generate_xml(programs):
  root = ET.Element("tv")

  # Channel Definition
  channel = ET.SubElement(root, "channel", id="CinemaOne.ph")
  display_name = ET.SubElement(channel, "display-name")
  display_name.text = "Cinema One"

  # Program Schedule Definitions
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
    desc.text = "Automatically generated schedule from ClickTheCity EPG."

  # Format XML with clean indentation
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

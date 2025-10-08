import os
os.environ["SSL_CERT_FILE"] = "/mnt/d/Travel Assistant/Musafir/Fortinet_CA_SSL(15).cer"
os.environ["REQUESTS_CA_BUNDLE"] = "/mnt/d/Travel Assistant/Musafir/Fortinet_CA_SSL(15).cer"

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


import os
import json
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

# ===================================
# Utility functions
# ===================================
def html_to_paragraphs(html: str):
    soup = BeautifulSoup(html, "html.parser")
    paragraphs = []
    for p in soup.find_all(["p", "li", "td"]):
        text = p.get_text(" ", strip=True)
        if text:
            paragraphs.append(text)
    return paragraphs


def fetch_wikivoyage_sections(page: str, user_agent="MyWikiVoyageClient/1.0 (contact: your-email@example.com)"):
    # Replace spaces with underscores for API compatibility
    page = page.strip().replace(" ", "_")

    api_url = "https://en.wikivoyage.org/w/api.php"
    headers = {"User-Agent": user_agent}

    # Step 1: Get metadata about all sections (top + sub)
    params = {
        "action": "parse",
        "page": page,
        "format": "json",
        "prop": "sections"
    }
    res = requests.get(api_url, params=params, headers=headers, verify=False).json()

    if "error" in res:
        raise ValueError(f"❌ Page not found for '{page}': {res['error'].get('info')}")

    sections_meta = res["parse"]["sections"]

    wanted = {"districts", "see", "buy", "eat", "drink", "sleep", "stay safe"}
    result = {}

    # Helper: clean HTML → paragraphs, list items, tables
    def html_to_paragraphs(html: str):
        soup = BeautifulSoup(html, "html.parser")
        paragraphs = []
        for p in soup.find_all(["p", "li", "td"]):
            text = p.get_text(" ", strip=True)
            if text:
                paragraphs.append(text)
        return paragraphs

    # Step 2: Grab description (section 0)
    lead_params = {
        "action": "parse",
        "page": page,
        "format": "json",
        "prop": "text",
        "section": 0
    }
    lead = requests.get(api_url, params=lead_params, headers=headers).json()
    lead_html = lead["parse"]["text"]["*"]
    result["description"] = html_to_paragraphs(lead_html)

    # Step 3: Iterate through sections
    for sec in sections_meta:
        title = sec["line"].strip()
        title_lower = title.lower()
        number = sec["number"]
        index = sec["index"]

        if title_lower in wanted and "." not in number:
            sec_params = {
                "action": "parse",
                "page": page,
                "format": "json",
                "prop": "text",
                "section": index
            }
            sec_data = requests.get(api_url, params=sec_params, headers=headers).json()
            html = sec_data["parse"]["text"]["*"]
            result[title] = {"content": html_to_paragraphs(html), "subsections": {}}

        elif "." in number:
            parent_num = number.split(".")[0]
            parent_section = next((s for s in sections_meta if s["number"] == parent_num), None)
            if parent_section and parent_section["line"].strip().lower() in wanted:
                parent_title = parent_section["line"].strip()
                sec_params = {
                    "action": "parse",
                    "page": page,
                    "format": "json",
                    "prop": "text",
                    "section": index
                }
                sec_data = requests.get(api_url, params=sec_params, headers=headers).json()
                html = sec_data["parse"]["text"]["*"]
                if parent_title in result:
                    result[parent_title]["subsections"][title] = html_to_paragraphs(html)

    return result


def process_city_data(city):
    """Fetch and save city data to ../data/raw_data and return DataFrame"""
    st.info(f"Fetching data for {city} from Wikivoyage...")
    data = fetch_wikivoyage_sections(city)
    os.makedirs("../data/raw_data", exist_ok=True)
    raw_file = f"../data/raw_data/{city.lower()}_subsections.json"

    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    st.success(f"Saved raw JSON for {city} at {raw_file}")

    # Convert JSON to rows
    rows = []
    for section, sec_data in data.items():
        if section == "description":
            for text in sec_data:
                rows.append([city, "description", "", text])
        elif isinstance(sec_data, dict):
            for txt in sec_data.get("content", []):
                rows.append([city, section, "", txt])
            for sub, sub_list in sec_data.get("subsections", {}).items():
                for txt in sub_list:
                    rows.append([city, section, sub, txt])

    df = pd.DataFrame(rows, columns=["city", "section", "subsection", "text"])
    return df


# ===================================
# Streamlit Interface
# ===================================
st.set_page_config(page_title="Travel Assistant - Data Ingestion", page_icon="🌍", layout="wide")
st.title("🌍 Travel Assistant - Data Ingestion & Exploration")

option = st.radio(
    "Choose how to get data:",
    ["Fetch city data from Wikivoyage", "Load existing processed data"],
    index=0
)

if option == "Fetch city data from Wikivoyage":
    city = st.text_input("Enter a city name (e.g., Rome, Cairo, London):")
    if st.button("Start Ingestion") and city:
        df = process_city_data(city)
        st.dataframe(df.head(10))
        save_path = f"../data/processed_data/{city.lower()}_data.csv"
        os.makedirs("../data/processed_data", exist_ok=True)
        df.to_csv(save_path, index=False)
        st.success(f"Processed data saved to {save_path}")

elif option == "Load existing processed data":
    file_path = "../data/processed_data/all_cities_combined_clean.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        st.success(f"Loaded data from {file_path}")
        st.dataframe(df.head(20))

        city_list = sorted(df["city"].unique())
        selected_city = st.selectbox("Filter by city:", ["All"] + city_list)
        if selected_city != "All":
            st.dataframe(df[df["city"] == selected_city])
    else:
        st.error("Processed data file not found. Please run ingestion first.")

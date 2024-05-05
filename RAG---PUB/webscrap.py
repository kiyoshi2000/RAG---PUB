import xml.etree.ElementTree as ET
import sqlite3
import requests
from bs4 import BeautifulSoup

# Function to parse XML sitemap and extract URLs
def parse_sitemap(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    urls = []
    
    for child in root:
        loc = child.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        urls.append(loc.text)
    
    return urls

# Function to scrape webpage title and extract text from <h> and <p> tags
def scrape_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else ""

            # Find all <h> and <p> tags and extract their text content
            h_elements = [tag.get_text().strip() for tag in soup.find_all('h')]
            p_elements = [tag.get_text().strip() for tag in soup.find_all('p')]

            # Join all <h> and <p> text content into a single HTML-like string
            html_content = '\n'.join(h_elements + p_elements)
            

            return title, html_content
        else:
            print(f"Failed to retrieve URL: {url}")
            return None, None
    except Exception as e:
        print(f"Error occurred while processing URL: {url}")
        print(e)
        return None, None

# Function to create SQLite database and table
def create_db_table(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Pages
                 (url TEXT PRIMARY KEY, title TEXT, html_content TEXT)''')  # Define the schema here
    conn.commit()
    conn.close()

# Function to insert data into SQLite database
def insert_into_db(db_name, url, title, html_content):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO Pages (url, title, html_content) VALUES (?,?,?)', (url, title, html_content))
    conn.commit()
    conn.close()

# Main function to process sitemap and store data in database
def main(xml_file, db_name):
    create_db_table(db_name)
    urls = parse_sitemap(xml_file)
    
    for url in urls:
        title, html_content = scrape_url(url)
        if title is not None and html_content is not None:
            insert_into_db(db_name, url, title, html_content)
            print(f"Stored: {url}")

if __name__ == "__main__":
    xml_file = "sitemap.xml"  # Path to your XML sitemap file
    db_name = "pagestest.db"      # SQLite database name
    
    main(xml_file, db_name)

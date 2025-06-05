import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_tw_market():
    url = "https://tw.stock.yahoo.com/"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    # 範例：找大盤指數
    index_info = soup.find("span", text="加權指數").find_parent().find_next_sibling()
    value = index_info.text

    print(f"{datetime.now()}: 台股大盤：{value}")
    
if __name__ == "__main__":
    fetch_tw_market()

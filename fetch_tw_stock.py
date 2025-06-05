import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

def is_valid_price(price_text):
    """验证价格格式是否正确"""
    try:
        # 移除所有逗号和空格
        cleaned_price = price_text.replace(',', '').strip()
        # 转换为浮点数进行验证
        float(cleaned_price)
        return True
    except ValueError:
        return False

def fetch_tw_market(max_retries=3, retry_delay=5):
    """
    获取台湾股市大盤指数
    max_retries: 最大重试次数
    retry_delay: 重试间隔（秒）
    """
    url = "https://tw.stock.yahoo.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive"
    }
    
    for attempt in range(max_retries):
        try:
            print(f"\n第 {attempt + 1} 次尝试获取数据")
            print(f"访问网址: {url}")
            
            res = requests.get(url, headers=headers, timeout=10)
            print(f"HTTP 状态码: {res.status_code}")
            
            if res.status_code != 200:
                print(f"错误：无法访问网页，状态码：{res.status_code}")
                if attempt < max_retries - 1:
                    print(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            print("网页内容解析完成")
            
            # 搜索策略1：通过 price-info 类和 Fz(32px) 类
            market_info = soup.find("div", {"class": "price-info"})
            if market_info:
                price = market_info.find("span", {"class": "Fz(32px)"})
                if price and is_valid_price(price.text):
                    print(f"\n{datetime.now()}: 台股大盘指数：{price.text}")
                    return price.text
            
            # 搜索策略2：查找包含特定文本的元素
            for element in soup.find_all(["span", "div"]):
                if "加權指數" in element.text:
                    parent = element.parent
                    price_element = parent.find("span", string=re.compile(r"^\d{1,3}(,\d{3})*(\.\d+)?$"))
                    if price_element and is_valid_price(price_element.text):
                        print(f"\n{datetime.now()}: 台股大盘指数：{price_element.text}")
                        return price_element.text
            
            # 搜索策略3：查找所有可能的价格元素
            print("\n未找到预期的价格元素，正在搜索所有可能的价格...")
            all_spans = soup.find_all("span")
            potential_prices = []
            
            for span in all_spans:
                if span.text and re.match(r"^\d{1,3}(,\d{3})*(\.\d+)?$", span.text.strip()):
                    potential_prices.append(span.text)
            
            if potential_prices:
                print("找到以下可能的价格值：")
                for i, price in enumerate(potential_prices[:5], 1):
                    print(f"{i}. {price}")
            else:
                print("未找到任何符合价格格式的值")
            
            if attempt < max_retries - 1:
                print(f"\n等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            
        except requests.exceptions.RequestException as e:
            print(f"网络请求错误：{str(e)}")
            if attempt < max_retries - 1:
                print(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
        except Exception as e:
            print(f"发生未预期的错误：{str(e)}")
            if attempt < max_retries - 1:
                print(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
    
    print("\n已达到最大重试次数，无法获取数据")
    return None

if __name__ == "__main__":
    result = fetch_tw_market()
    if result:
        print(f"\n成功获取大盘指数：{result}")
    else:
        print("\n无法获取大盘指数")

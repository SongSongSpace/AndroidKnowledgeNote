import requests
from google_play_scraper import app
from datetime import datetime

# ==================== 配置区域（请替换） ====================
APP_TOKEN = "LzA5bTng7aCXKMsvIIGcNy9BnGg"               # 多维表格ID
TABLE_ID = "tbl4UGCfNsbzsbSm"                         # 数据表ID
PERSONAL_BASE_TOKEN = "pt-NV_yWu0C-1L7tPZjf2dsd-ZJFKdfq_HkY0q48WmdAQAABIBFtMFMgqLCA2_Y"                     # 替换为你刚找到的授权码
# ========================================================

def add_record_to_bitable(app_name, country_code, country_name, rating, rating_count):
    """使用 PersonalBaseToken 写入多维表格"""
    # 关键：API 域名为 base-api.feishu.cn
    url = f"https://base-api.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {PERSONAL_BASE_TOKEN}",
        "Content-Type": "application/json"
    }
    timestamp = int(datetime.now().timestamp() * 1000)   # 毫秒时间戳
    data = {
        "fields": {
            "应用名称": app_name,
            "国家代码": country_code,
            "国家名称": country_name,
            "评分": rating,
            "评分数": rating_count,
            "抓取时间": timestamp
        }
    }
    print(f"📤 发送: {data}")
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"❌ 错误: {response.text}")
    response.raise_for_status()
    return response.json()

def main():
    # 示例：抓取一个应用一个国家
    app_id = "com.boost.universal.remote"
    app_name = "Universal TV Remote"
    country_code = "us"
    country_name = "United States"

    print(f"🌍 抓取 {app_name} - {country_name}")
    result = app(app_id, country=country_code, lang='en')
    rating = result.get('score')
    rating_count = result.get('ratings')
    print(f"✅ 抓取成功: 评分 {rating}, 评分数 {rating_count}")

    add_record_to_bitable(app_name, country_code, country_name, rating, rating_count)
    print("🎉 写入多维表格成功！")

if __name__ == "__main__":
    main()

from flask import Flask, jsonify, render_template, request
import os
import requests
import time
import math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from astral import moon
from astral import Observer

app = Flask(__name__)
WEATHER_CACHE_SECONDS = 300
MAX_CACHE_ENTRIES = 100
weather_cache = {}
image_cache = {}

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
WIKIMEDIA_URL = "https://commons.wikimedia.org/w/api.php"
CITY_ALIASES = {
    "台北": "Taipei",
    "臺北": "Taipei",
    "taipei": "Taipei",
    "高雄": "Kaohsiung",
    "台中": "Taichung",
    "臺中": "Taichung",
    "台南": "Tainan",
    "臺南": "Tainan",
    "新竹": "Hsinchu",
    "嘉義": "Chiayi",
    "嘉义": "Chiayi",
    "宜蘭": "Yilan",
    "宜兰": "Yilan",
    "花蓮": "Hualien",
    "花莲": "Hualien",
    "澳門": "Macau",
    "東京": "Tokyo",
    "とうきょう": "Tokyo",
    "도쿄": "Tokyo",
    "大阪": "Osaka",
    "首爾": "Seoul",
    "서울": "Seoul",
    "Séoul": "Seoul",
    "新加坡": "Singapore",
    "シンガポール": "Singapore",
    "싱가포르": "Singapore",
    "香港": "Hong Kong",
    "曼谷": "Bangkok",
    "吉隆坡": "Kuala Lumpur",
    "雅加達": "Jakarta",
    "雅加达": "Jakarta",
    "馬尼拉": "Manila",
    "釜山": "Busan",
    "北京": "Beijing",
    "上海": "Shanghai",
    "天津": "Tianjin",
    "南京": "Nanjing",
    "武漢": "Wuhan",
    "武汉": "Wuhan",
    "廈門": "Xiamen",
    "厦门": "Xiamen",
    "廣州": "Guangzhou",
    "广州": "Guangzhou",
    "深圳": "Shenzhen",
    "成都": "Chengdu",
    "重慶": "Chongqing",
    "重庆": "Chongqing",
    "西安": "Xi'an",
    "杭州": "Hangzhou",
    "鄭州": "Zhengzhou",
    "郑州": "Zhengzhou",
    "開封": "Kaifeng",
    "开封": "Kaifeng",
    "洛陽": "Luoyang",
    "洛阳": "Luoyang",
    "平頂山": "Pingdingshan",
    "平顶山": "Pingdingshan",
    "安陽": "Anyang",
    "安阳": "Anyang",
    "鶴壁": "Hebi",
    "鹤壁": "Hebi",
    "新鄉": "Xinxiang",
    "新乡": "Xinxiang",
    "焦作": "Jiaozuo",
    "濮陽": "Puyang",
    "濮阳": "Puyang",
    "許昌": "Xuchang",
    "许昌": "Xuchang",
    "漯河": "Luohe",
    "三門峽": "Sanmenxia",
    "三门峡": "Sanmenxia",
    "南陽": "Nanyang",
    "南阳": "Nanyang",
    "商丘": "Shangqiu",
    "信陽": "Xinyang",
    "信阳": "Xinyang",
    "周口": "Zhoukou",
    "駐馬店": "Zhumadian",
    "驻马店": "Zhumadian",
    "濟源": "Jiyuan",
    "济源": "Jiyuan",
    "倫敦": "London",
    "Londres": "London",
    "巴黎": "Paris",
    "París": "Paris",
    "パリ": "Paris",
    "柏林": "Berlin",
    "Берлин": "Berlin",
    "羅馬": "Rome",
    "Roma": "Rome",
    "ローマ": "Rome",
    "莫斯科": "Moscow",
    "紐約": "New York",
    "Nueva York": "New York",
    "Нью-Йорк": "New York",
    "洛杉磯": "Los Angeles",
    "Los Ángeles": "Los Angeles",
    "舊金山": "San Francisco",
    "多倫多": "Toronto",
    "溫哥華": "Vancouver",
    "雪梨": "Sydney",
    "Sídney": "Sydney",
    "シドニー": "Sydney",
    "墨爾本": "Melbourne",
    "奧克蘭": "Auckland",
    "杜拜": "Dubai",
    "دبي": "Dubai",
    "米蘭": "Milan",
    "Milán": "Milan",
    "馬德里": "Madrid",
    "阿姆斯特丹": "Amsterdam",
    "維也納": "Vienna",
    "開羅": "Cairo",
    "القاهرة": "Cairo",
    "芝加哥": "Chicago",
    "西雅圖": "Seattle",
    "波士頓": "Boston",
    "華盛頓": "Washington, D.C.",
    "聖保羅": "Sao Paulo",
    "里約熱內盧": "Rio de Janeiro",
    "利馬": "Lima",
    "布宜諾斯艾利斯": "Buenos Aires",
    "布拉格": "Prague",
    "蘇黎世": "Zurich",
    "斯德哥爾摩": "Stockholm",
    "伊斯坦堡": "Istanbul",
    "德里": "Delhi",
    "Nueva Delhi": "Delhi",
    "孟買": "Mumbai",
    "Bombay": "Mumbai",
    "胡志明市": "Ho Chi Minh City",
    "河內": "Hanoi",
    "Hanói": "Hanoi",
    "ハノイ": "Hanoi",
    "夏威夷": "Honolulu",
    "檀香山": "Honolulu",
    "拉斯維加斯": "Las Vegas",
    "邁阿密": "Miami",
    "哥本哈根": "Copenhagen",
    "赫爾辛基": "Helsinki",
    "奧斯陸": "Oslo",
    "華沙": "Warsaw",
    "布達佩斯": "Budapest",
    "雅典": "Athens",
    "里斯本": "Lisbon",
    "布魯塞爾": "Brussels",
    "慕尼黑": "Munich",
    "利雅德": "Riyadh",
    "多哈": "Doha",
    "開普敦": "Cape Town",
    "奈洛比": "Nairobi",
    "新德里": "New Delhi",
    "加德滿都": "Kathmandu",
    "可倫坡": "Colombo",
    "金邊": "Phnom Penh",
    "蒙特婁": "Montreal",
    "休士頓": "Houston",
    "丹佛": "Denver",
    "亞特蘭大": "Atlanta",
    "鳳凰城": "Phoenix",
    "波哥大": "Bogota",
    "聖地亞哥": "Santiago",
    "墨西哥城": "Mexico City",
    # United Kingdom city names in common Chinese, Japanese, Korean and Spanish forms.
    "伦敦": "London",
    "ロンドン": "London",
    "런던": "London",
    "Londres": "London",
    "لندن": "London",
    "Лондон": "London",
    "伯明翰": "Birmingham",
    "バーミンガム": "Birmingham",
    "버밍엄": "Birmingham",
    "Birmingham": "Birmingham",
    "برمنغهام": "Birmingham",
    "Бирмингем": "Birmingham",
    "曼彻斯特": "Manchester",
    "曼徹斯特": "Manchester",
    "マンチェスター": "Manchester",
    "맨체스터": "Manchester",
    "مانشستر": "Manchester",
    "Манчестер": "Manchester",
    "爱丁堡": "Edinburgh",
    "愛丁堡": "Edinburgh",
    "エディンバラ": "Edinburgh",
    "에든버러": "Edinburgh",
    "إدنبرة": "Edinburgh",
    "Эдинбург": "Edinburgh",
    "格拉斯哥": "Glasgow",
    "グラスゴー": "Glasgow",
    "글래스고": "Glasgow",
    "غلاسكو": "Glasgow",
    "Глазго": "Glasgow",
    "利物浦": "Liverpool",
    "リバプール": "Liverpool",
    "리버풀": "Liverpool",
    "ليفربول": "Liverpool",
    "Ливерпуль": "Liverpool",
    "布里斯托尔": "Bristol",
    "布里斯托": "Bristol",
    "ブリストル": "Bristol",
    "브리스틀": "Bristol",
    "بريستول": "Bristol",
    "Бристоль": "Bristol",
    "牛津": "Oxford",
    "牛津市": "Oxford",
    "オックスフォード": "Oxford",
    "옥스퍼드": "Oxford",
    "أكسفورد": "Oxford",
    "Оксфорд": "Oxford",
    "剑桥": "Cambridge",
    "劍橋": "Cambridge",
    "ケンブリッジ": "Cambridge",
    "케임브리지": "Cambridge",
    "كامبريدج": "Cambridge",
    "Кембридж": "Cambridge",
    "约克": "York",
    "約克": "York",
    "ヨーク": "York",
    "요크": "York",
    "يورك": "York",
    "Йорк": "York",
    "纽卡斯尔": "Newcastle upon Tyne",
    "紐卡斯爾": "Newcastle upon Tyne",
    "ニューカッスル": "Newcastle upon Tyne",
    "뉴캐슬": "Newcastle upon Tyne",
    "نيوكاسل": "Newcastle upon Tyne",
    "Ньюкасл": "Newcastle upon Tyne",
    "加的夫": "Cardiff",
    "卡迪夫": "Cardiff",
    "カーディフ": "Cardiff",
    "카디프": "Cardiff",
    "كارديف": "Cardiff",
    "Кардифф": "Cardiff",
    "贝尔法斯特": "Belfast",
    "貝爾法斯特": "Belfast",
    "ベルファスト": "Belfast",
    "벨파스트": "Belfast",
    "بلفاست": "Belfast",
    "Белфаст": "Belfast",
}
UK_CITIES = [
    "Bath", "Birmingham", "Bradford", "Brighton and Hove", "Bristol",
    "Cambridge", "Canterbury", "Carlisle", "Chelmsford", "Chester",
    "Chichester", "Coventry", "Derby", "Doncaster", "Dundee", "Durham",
    "Ely", "Exeter", "Glasgow", "Gloucester", "Hereford", "Kingston upon Hull",
    "Lancaster", "Leeds", "Leicester", "Lichfield", "Lincoln", "Lisburn",
    "Liverpool", "London", "Manchester", "Milton Keynes", "Newcastle upon Tyne",
    "Newport", "Norwich", "Nottingham", "Oxford", "Perth", "Peterborough",
    "Plymouth", "Portsmouth", "Preston", "Ripon", "Salford", "Salisbury",
    "Sheffield", "Southampton", "St Albans", "St Asaph", "St Davids",
    "Stirling", "Sunderland", "Swansea", "Truro", "Wakefield",
    "Wells", "Westminster", "Winchester", "Wolverhampton", "Worcester",
    "York", "Armagh", "Bangor", "Belfast", "Wrexham", "Inverness",
]
WEATHER_CODES = {
    0: "晴朗",
    1: "大致晴朗",
    2: "局部多雲",
    3: "陰天",
    45: "有霧",
    48: "霧凇",
    51: "毛毛雨",
    53: "毛毛雨",
    55: "毛毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    80: "陣雨",
    81: "陣雨",
    82: "強陣雨",
    95: "雷雨",
    96: "雷雨伴隨冰雹",
    99: "雷雨伴隨冰雹",
}


def wind_description(speed):
    if speed < 1:
        return "無風"
    if speed < 6:
        return "微風"
    if speed < 12:
        return "輕風"
    if speed < 20:
        return "和風"
    if speed < 29:
        return "強風"
    if speed < 39:
        return "烈風"
    return "暴風"


def wind_direction(degrees):
    directions = ("北", "東北", "東", "東南", "南", "西南", "西", "西北")
    return directions[round(degrees / 45) % 8]


def optional_wind_direction(degrees):
    return wind_direction(degrees) if degrees is not None else "無資料"


def moon_details(latitude, longitude, timezone_name):
    try:
        local_zone = ZoneInfo(timezone_name)
    except (KeyError, ValueError):
        local_zone = timezone.utc
    now_utc = datetime.now(timezone.utc)
    local_date = now_utc.astimezone(local_zone).date()
    observer = Observer(latitude=latitude, longitude=longitude)
    try:
        moonset = moon.moonset(observer, date=local_date, tzinfo=local_zone)
        moonset_text = moonset.strftime("%H:%M")
    except (ValueError, KeyError):
        moonset_text = "今日不可見"
    phase = moon.phase(local_date)
    illumination = round((1 - math.cos(2 * math.pi * phase / 29.53)) / 2 * 100)
    candidates = []
    for day_offset in range(1, 40):
        candidate_date = local_date.fromordinal(local_date.toordinal() + day_offset)
        candidate_phase = moon.phase(candidate_date)
        if 14 <= candidate_phase <= 21:
            candidates.append((abs(candidate_phase - 14.765), candidate_date))
    next_full_date = min(candidates)[1] if candidates else local_date
    return {
        "illumination": illumination,
        "moonset": moonset_text,
        "next_full_moon": next_full_date.strftime("%Y-%m-%d"),
    }


def get_json(url, params):
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def find_locations(city):
    search_city = CITY_ALIASES.get(city, CITY_ALIASES.get(city.casefold(), city))
    queries = [(search_city, "en")]
    if search_city != city:
        queries.append((city, "zh"))
    else:
        queries.extend((city, language) for language in ("zh", "ja", "ko", "fr", "es"))

    seen = set()
    for query, language in queries:
        locations = get_json(
            GEOCODING_URL,
            {"name": query, "count": 5, "language": language, "format": "json"},
        ).get("results", [])
        unique_locations = []
        for location in locations:
            key = (location.get("latitude"), location.get("longitude"))
            if key not in seen:
                seen.add(key)
                unique_locations.append(location)
        if unique_locations:
            return unique_locations
    return []


def get_cached_weather(city):
    cache_key = city.casefold()
    cached = weather_cache.get(cache_key)
    if cached and time.monotonic() - cached["created_at"] < WEATHER_CACHE_SECONDS:
        return cached["data"]
    return None


def cache_weather(city, data):
    if len(weather_cache) >= MAX_CACHE_ENTRIES:
        oldest_city = min(weather_cache, key=lambda key: weather_cache[key]["created_at"])
        weather_cache.pop(oldest_city, None)
    weather_cache[city.casefold()] = {
        "created_at": time.monotonic(),
        "data": data,
    }


def get_city_image(city, country):
    cache_key = f"{city}|{country}".casefold()
    cached = image_cache.get(cache_key)
    if cached is not None:
        return cached
    try:
        response = requests.get(
            WIKIMEDIA_URL,
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": f"{city} {country} city",
                "gsrnamespace": 6,
                "gsrlimit": 1,
                "prop": "imageinfo",
                "iiprop": "url",
                "iiurlwidth": 1200,
                "format": "json",
            },
            headers={"User-Agent": "CityWeatherDesk/1.0"},
            timeout=6,
        )
        response.raise_for_status()
        pages = response.json().get("query", {}).get("pages", {})
        page = next(iter(pages.values()), {})
        image_info = page.get("imageinfo", [{}])[0]
        image_url = image_info.get("thumburl") or image_info.get("url")
        image_cache[cache_key] = image_url
        return image_url
    except (requests.RequestException, KeyError, TypeError, ValueError):
        image_cache[cache_key] = None
        return None


@app.get("/")
def index():
    return render_template("index.html", uk_cities=UK_CITIES)


@app.get("/favicon.ico")
def favicon():
    return "", 204


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "city-weather-desk"})


@app.errorhandler(404)
def not_found(error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "找不到這個 API 路徑。"}), 404
    return "找不到頁面", 404


@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "伺服器暫時發生錯誤，請稍後再試。"}), 500
    return "伺服器暫時發生錯誤", 500


@app.get("/api/weather")
def weather():
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "請輸入城市名稱。"}), 400
    if len(city) > 80:
        return jsonify({"error": "城市名稱不可超過 80 個字元。"}), 400

    try:
        cached = None if request.args.get("refresh") == "1" else get_cached_weather(city)
        if cached:
            return jsonify(cached)

        locations = find_locations(city)
        if not locations:
            return jsonify({"error": f"找不到「{city}」，請嘗試英文城市名稱。"}), 404

        location = locations[0]
        forecast = get_json(
            WEATHER_URL,
            {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m,visibility,surface_pressure",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,temperature_2m_mean,uv_index_max,sunrise,sunset",
                "timezone": "auto",
                "forecast_days": 5,
            },
        )
        current = forecast["current"]
        units = forecast["current_units"]
        daily = forecast["daily"]
        moon_data = moon_details(
            location["latitude"],
            location["longitude"],
            forecast["timezone"],
        )
        data = {
                "location": {
                    "name": location["name"],
                    "country": location.get("country", ""),
                    "admin1": location.get("admin1", ""),
                    "image_url": None,
                    "timezone": forecast["timezone"],
                },
                "current": {
                    "temperature": current["temperature_2m"],
                    "temperature_unit": units["temperature_2m"],
                    "apparent_temperature": current["apparent_temperature"],
                    "humidity": current["relative_humidity_2m"],
                    "wind_speed": current["wind_speed_10m"],
                    "wind_unit": units["wind_speed_10m"],
                    "wind_direction": current["wind_direction_10m"],
                    "wind_direction_text": optional_wind_direction(current.get("wind_direction_10m")),
                    "wind_gusts": current["wind_gusts_10m"],
                    "wind_gusts_unit": units["wind_gusts_10m"],
                    "wind_type": wind_description(current["wind_speed_10m"]),
                    "visibility": current["visibility"],
                    "visibility_unit": units["visibility"],
                    "pressure": current["surface_pressure"],
                    "pressure_unit": units["surface_pressure"],
                    "description": WEATHER_CODES.get(current["weather_code"], "天氣資料"),
                },
                "astronomy": moon_data,
                "daily": [
                    {
                        "date": date,
                        "description": WEATHER_CODES.get(code, "天氣資料"),
                        "max": max_temp,
                        "min": min_temp,
                        "mean": mean_temp,
                        "uv_index": uv_index,
                        "sunrise": sunrise,
                        "sunset": sunset,
                        "unit": forecast["daily_units"]["temperature_2m_max"],
                    }
                    for date, code, max_temp, min_temp, mean_temp, uv_index, sunrise, sunset in zip(
                        daily["time"],
                        daily["weather_code"],
                        daily["temperature_2m_max"],
                        daily["temperature_2m_min"],
                        daily["temperature_2m_mean"],
                        daily["uv_index_max"],
                        daily["sunrise"],
                        daily["sunset"],
                    )
                ],
            }
        cache_weather(city, data)
        return jsonify(data)
    except requests.RequestException:
        return jsonify({"error": "暫時無法連線到天氣服務，請稍後再試。"}), 502
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "天氣服務回傳了無法解析的資料。"}), 502


@app.get("/api/city-image")
def city_image():
    city = request.args.get("city", "").strip()
    if not city or len(city) > 80:
        return jsonify({"image_url": None})
    image_city = CITY_ALIASES.get(city, CITY_ALIASES.get(city.casefold(), city))
    image_url = get_city_image(image_city, "")
    return jsonify({"image_url": image_url})


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    app.run(host=host, port=port, debug=debug, use_reloader=False)

import pytz

product_timezone = {
    'HSI': pytz.timezone('Asia/Hong_Kong'),  # Heng Seng
    'HSCE': pytz.timezone('Asia/Hong_Kong'),  # Hang Seng China Enterprises Index
    'IF300': pytz.timezone('Asia/Hong_Kong'),  # Shanghai and Shenzhen index
    'S2SFC': pytz.timezone('Asia/Hong_Kong'),  # A50
    'O1GC': pytz.timezone('America/New_York'),  # Gold
    'M1EC': pytz.timezone('America/Chicago'),  # Euro
    'B1YM': pytz.timezone('America/Chicago'),  # Mini Dow Jones
    'N1CL': pytz.timezone('America/New_York'),  # Oil
    'WTX': pytz.timezone('Asia/Taipei'),  # Taiwan
    'M1NQ': pytz.timezone('America/Chicago'),  # NasDaq
    'M1ES': pytz.timezone('America/Chicago'),  # SP500
}

product_name = {
    'HSI': "亞洲期指",  # Heng Seng
    'HSCE': "亞企期指",  # Hang Seng China Enterprises Index
    'IF300': "滬深期指",  # Shanghai and Shenzhen index
    'S2SFC': "A50",  # A50
    'O1GC': "紐約期金",  # Gold
    'M1EC': "歐元期貨",  # Euro
    'B1YM': "迷你道瓊",  # Mini Dow Jones
    'N1CL': "小輕原油",  # Oil
    'WTX': "台灣期指",  # Taiwan
    'M1NQ': "NasDaq",  # NasDaq
    'M1ES': "SP500",  # SP500
}

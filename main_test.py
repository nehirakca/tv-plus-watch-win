from src.data_loader import load_all_data
from src.metrics_engine import get_user_state

users, activity, shows, episodes = load_all_data()

# 2. Örnek bir kullanıcı ve tarih için metrikleri hesapla
test_user = users.iloc[0]['user_id']
test_date = "2026-03-12" 

state = get_user_state(test_user, test_date, activity)
print(f"Kullanici Durumu ({test_user}):", state)
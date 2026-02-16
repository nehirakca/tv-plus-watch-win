from src.data_loader import load_all_data
from src.metrics_engine import generate_all_user_states
from src.ledger_manager import LedgerManager
from src.metrics_engine import enrich_activity_with_names
import pandas as pd

# 1. Hazırlık
AS_OF_DATE = "2026-03-12" # Case örneğindeki tarih 
users, activity, shows, episodes = load_all_data()
ledger = LedgerManager()

# 2. Metrik Üretimi
print("Metrikler hesaplanıyor...")
all_user_states = generate_all_user_states(AS_OF_DATE, users, activity)

# 3. Kural Motoru için Hazırlık

print("Kullanıcı durumları hazır!")
print(all_user_states.head())

# Katalogla zenginleştirilmiş aktivite tablosu
enriched_activity = enrich_activity_with_names(activity, shows)

# 3. Üye'nin (UI) dashboard'da kullanıcı detaylarında göstermesi için kaydet
enriched_activity.to_csv('outputs/enriched_activity_history.csv', index=False)

print("Bonus: Zenginleştirilmiş aktivite verisi 'outputs/' klasörüne kaydedildi!")

# İleride 2. Üye buraya kendi fonksiyonunu ekleyecek:
# awards = rules_engine.evaluate_challenges(all_user_states)
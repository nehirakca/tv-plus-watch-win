import pandas as pd
import os
from src.data_loader import load_all_data
from src.metrics_engine import generate_all_user_states, enrich_activity_with_names
from src.rules_engine import evaluate_challenges, check_badges, what_if_simulation
from src.ledger_manager import LedgerManager

def main():
    # 0. Çıktı Klasörü Kontrolü
    if not os.path.exists('outputs'):
        os.makedirs('outputs')

    # 1. Verileri Yükleme [cite: 16-20, 47]
    print("Veriler yükleniyor...")
    users, activity, shows, episodes = load_all_data()
    challenges = pd.read_csv('data/challenges.csv')
    
    # Case'de belirtilen referans tarihi [cite: 32]
    AS_OF_DATE = "2026-03-12" 
    ledger = LedgerManager()

    # 2. Metrik Üretimi (1. Üye Görevi) [cite: 31-45]
    print(f"{AS_OF_DATE} tarihi için metrikler hesaplanıyor...")
    all_user_states = generate_all_user_states(AS_OF_DATE, users, activity)
    print("Kullanıcı durumları (today/7d/streak) hazır!")

    # 3. Kural Motoru ve Karar Mekanizması (2. Üye Görevi) [cite: 46, 64-69]
    print("Görev koşulları ve öncelikler kontrol ediliyor...")
    # Priority kuralına göre tetiklenenlerden en yüksek öncelikliyi seçer [cite: 66-67]
    challenge_awards = evaluate_challenges(all_user_states, challenges)
    # Bildirim üretimi
    notifications = []
    for idx, row in challenge_awards.iterrows():
        notif = {
            'notification_id': str(idx),
            'user_id': row['user_id'],
            'channel': 'BiP',
            'message': f"Tebrikler! {row['selected_challenge']} challenge ödülünü kazandınız.",
            'sent_at': row['timestamp']
        }
        notifications.append(notif)
    notifications_df = pd.DataFrame(notifications)

    # 4. Puanları Ledger'a İşleme [cite: 79-87]
    print("Puan hareketleri ledger'a kaydediliyor...")
    for idx, row in challenge_awards.iterrows():
        ledger.add_entry(
            user_id=row['user_id'],
            points=row['reward_points'], # Sadece seçilen ödülün puanı [cite: 69]
            source='CHALLENGE_REWARD',
            source_ref=row['award_id']
        )

    # 5. Rozetleri Hesaplama [cite: 96-101]
    print("Toplam puanlar üzerinden rozet kontrolleri yapılıyor...")
    all_badges_list = []
    for user_id in users['user_id']:
        total_p = ledger.get_total_points(user_id)
        u_badges = check_badges(user_id, total_p)
        if not u_badges.empty:
            all_badges_list.append(u_badges)

    if all_badges_list:
        badge_awards_df = pd.concat(all_badges_list, ignore_index=True)
    else:
        badge_awards_df = pd.DataFrame(columns=['user_id', 'badge_id', 'badge_name'])

    # 6. Bonus: Zenginleştirilmiş Aktivite Verisi (UI için) [cite: 118]
    print("Bonus: İçerik isimleri aktivite geçmişine ekleniyor...")
    enriched_activity = enrich_activity_with_names(activity, shows)
    enriched_activity.to_csv('outputs/enriched_activity_history.csv', index=False)

    # 7. Tüm Çıktıları Kaydetme [cite: 70, 80, 102]
    ledger.save_outputs(challenge_awards, badge_awards_df, notifications_df)
    
    # 8. Bonus: Backend What-if Simülasyonu Örneği
    print("What-if simülasyonu örneği:")
    sample_user_id = users['user_id'].iloc[0]
    extra_minutes = 30
    result = what_if_simulation(sample_user_id, extra_minutes, AS_OF_DATE, users, activity, challenges)
    print(f"Kullanıcı: {sample_user_id}, Ek İzleme: {extra_minutes} dk")
    print(f"Tetiklenen Challenge'lar: {result['triggered_challenges']}")
    print(f"Seçilen Challenge: {result['selected_challenge']}")
    print(f"Suppressed Challenge'lar: {result['suppressed_challenges']}")
    print(f"Kazanılacak Rozetler: {result['badges']}")

    print("\n" + "="*30)
    print("✅ İŞLEM BAŞARIYLA TAMAMLANDI!")
    print("Sonuçlar 'outputs/' klasörüne kaydedildi.")
    print("="*30)

if __name__ == "__main__":
    main()
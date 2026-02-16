# Backend What-if simülasyonu fonksiyonu
def what_if_simulation(user_id, extra_minutes, as_of_date, users_df, activity_df, challenges_df):
    """
    Kullanıcıya ek izleme süresi ekleyerek tetiklenen challenge ve rozetleri hesaplar.
    """
    # Kullanıcı state'ini üret
    from src.metrics_engine import get_user_state
    user_state = get_user_state(user_id, as_of_date, activity_df)
    # Ek izleme süresi ekle
    user_state['watch_minutes_today'] += extra_minutes
    user_state['watch_minutes_7d'] += extra_minutes
    # Challenge tetikleme
    triggered_ids = []
    challenges_df['challenge_id'] = challenges_df['challenge_id'].astype(str).str.strip()
    active_challenges = challenges_df[challenges_df['is_active'] == True]
    ch_map = active_challenges.set_index('challenge_id').to_dict('index')
    if 'C-01' in ch_map and user_state['watch_minutes_today'] >= 60:
        triggered_ids.append('C-01')
    if 'C-02' in ch_map and user_state['episodes_completed_today'] >= 2:
        triggered_ids.append('C-02')
    if 'C-03' in ch_map and user_state['unique_genres_today'] >= 2:
        triggered_ids.append('C-03')
    if 'C-05' in ch_map and user_state['watch_streak_days'] >= 3:
        triggered_ids.append('C-05')
    if 'C-06' in ch_map and user_state['watch_minutes_7d'] >= 600:
        triggered_ids.append('C-06')
    # Priority kuralı
    triggered_data = []
    for tid in triggered_ids:
        temp_info = ch_map[tid].copy()
        temp_info['challenge_id'] = tid
        triggered_data.append(temp_info)
    triggered_df = pd.DataFrame(triggered_data).sort_values('priority') if triggered_data else pd.DataFrame()
    selected_challenge = triggered_df.iloc[0]['challenge_id'] if not triggered_df.empty else None
    suppressed_challenges = triggered_df.iloc[1:]['challenge_id'].tolist() if len(triggered_df) > 1 else []
    # Rozet hesaplama
    from src.rules_engine import check_badges
    total_points = user_state['watch_minutes_today'] # Örnek: puan = izleme süresi (veya ledger'dan alınabilir)
    badges_df = check_badges(user_id, total_points)
    badge_names = badges_df['badge_name'].tolist() if not badges_df.empty else []
    return {
        'triggered_challenges': triggered_ids,
        'selected_challenge': selected_challenge,
        'suppressed_challenges': suppressed_challenges,
        'badges': badge_names
    }
import pandas as pd
import uuid
from datetime import datetime

def evaluate_challenges(all_user_states, challenges_df):
    """Metrikleri görev koşullarıyla karşılaştırır."""
    awards_list = []
    
    # ID'leri temizle (boşlukları sil)
    challenges_df['challenge_id'] = challenges_df['challenge_id'].astype(str).str.strip()
    active_challenges = challenges_df[challenges_df['is_active'] == True]
    
    # Hızlı erişim için sözlük (Map)
    ch_map = active_challenges.set_index('challenge_id').to_dict('index')

    for index, user_state in all_user_states.iterrows():
        triggered_ids = []
        
        # 1. KOŞUL KONTROLLERİ (Dosyadaki C-01 formatına göre) [cite: 57-63]
        # Günlük İzleme (60+ dk)
        if 'C-01' in ch_map and user_state['watch_minutes_today'] >= 60:
            triggered_ids.append('C-01')
        
        # Bölüm Bitirici (2+ bölüm)
        if 'C-02' in ch_map and user_state['episodes_completed_today'] >= 2:
            triggered_ids.append('C-02')
            
        # Tür Avcısı (2+ tür)
        if 'C-03' in ch_map and user_state['unique_genres_today'] >= 2:
            triggered_ids.append('C-03')

        # Streak Serisi (3+ gün)
        if 'C-05' in ch_map and user_state['watch_streak_days'] >= 3:
            triggered_ids.append('C-05')

        # Haftalık Binge (600+ dk)
        if 'C-06' in ch_map and user_state['watch_minutes_7d'] >= 600:
            triggered_ids.append('C-06')

        # 2. ÇAKIŞMA YÖNETİMİ (Priority Kuralı) [cite: 65-69]
        if triggered_ids:
            triggered_data = []
            for tid in triggered_ids:
                temp_info = ch_map[tid].copy()
                temp_info['challenge_id'] = tid
                triggered_data.append(temp_info)
            
            # Priority'ye göre sırala (1 en yüksek öncelik) [cite: 67]
            triggered_df = pd.DataFrame(triggered_data).sort_values('priority')
            
            selected = triggered_df.iloc[0]
            suppressed = triggered_df.iloc[1:]['challenge_id'].tolist() if len(triggered_df) > 1 else []
            
            award = {
                'award_id': str(uuid.uuid4()),
                'user_id': user_state['user_id'],
                'as_of_date': user_state['as_of_date'],
                'triggered_challenges': "|".join(triggered_df['challenge_id'].tolist()),
                'selected_challenge': selected['challenge_id'],
                'reward_points': selected['reward_points'], # Sadece seçilen ödülün puanı verilir
                'suppressed_challenges': "|".join(suppressed),
                'timestamp': datetime.now()
            }
            awards_list.append(award)
            
    return pd.DataFrame(awards_list)

def check_badges(user_id, total_points):
    """Puan eşiklerine göre rozet ataması yapar [cite: 97, 99-101]."""
    badges = []
    now = datetime.now()
    # Baremler: 300, 850, 1500 [cite: 99-101]
    if total_points >= 1500:
        badges.append({'user_id': user_id, 'badge_id': 'B3', 'badge_name': 'Altın İzleyici', 'awarded_at': now})
    elif total_points >= 850:
        badges.append({'user_id': user_id, 'badge_id': 'B2', 'badge_name': 'Gümüş İzleyici', 'awarded_at': now})
    elif total_points >= 300:
        badges.append({'user_id': user_id, 'badge_id': 'B1', 'badge_name': 'Bronz İzleyici', 'awarded_at': now})
    return pd.DataFrame(badges)
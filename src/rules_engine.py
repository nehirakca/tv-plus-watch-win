import pandas as pd
import uuid
from datetime import datetime

def evaluate_challenges(all_user_states, challenges_df):
    """Metrikleri görev koşullarıyla karşılaştırır[cite: 46]."""
    awards_list = []
    
    # Sadece aktif görevleri al 
    active_challenges = challenges_df[challenges_df['is_active'] == True]

    # Hızlı erişim için challenge_id'yi index yapalım
    ch_map = active_challenges.set_index('challenge_id').to_dict('index')

    for index, user_state in all_user_states.iterrows():
        triggered = []
        
        # 1. KOŞUL KONTROLLERİ [cite: 57-63]
        # Günlük İzleme (60+ dk) [cite: 57]
        if 'C1' in ch_map and user_state['watch_minutes_today'] >= 60:
            triggered.append(pd.Series(ch_map['C1']).rename('C1'))
        
        # Bölüm Bitirici (2+ bölüm) [cite: 58]
        if 'C2' in ch_map and user_state['episodes_completed_today'] >= 2:
            triggered.append(pd.Series(ch_map['C2']).rename('C2'))
            
        # Tür Avcısı (2+ tür) [cite: 59]
        if 'C3' in ch_map and user_state['unique_genres_today'] >= 2:
            triggered.append(pd.Series(ch_map['C3']).rename('C3'))
            
        # Watch Party (45+ dk) [cite: 60]
        if 'C4' in ch_map and user_state['watch_party_minutes_today'] >= 45:
             triggered.append(pd.Series(ch_map['C4']).rename('C4'))

        # Streak Serisi (3+ gün) [cite: 61]
        if 'C5' in ch_map and user_state['watch_streak_days'] >= 3:
            triggered.append(pd.Series(ch_map['C5']).rename('C5'))

        # Haftalık Binge (600+ dk) [cite: 62]
        if 'C6' in ch_map and user_state['watch_minutes_7d'] >= 600:
            triggered.append(pd.Series(ch_map['C6']).rename('C6'))

        # 2. ÇAKIŞMA YÖNETİMİ (Priority Kuralı) [cite: 64-69]
        if triggered:
            # Tetiklenenleri priority'ye göre sırala (1 en yüksek öncelik) 
            triggered_df = pd.DataFrame(triggered).sort_values('priority')
            
            selected = triggered_df.iloc[0] # En küçük priority seçilir 
            suppressed = triggered_df.iloc[1:]['challenge_id'].tolist() if len(triggered_df) > 1 else []
            
            award = {
                'award_id': str(uuid.uuid4()),
                'user_id': user_state['user_id'],
                'as_of_date': user_state['as_of_date'],
                'triggered_challenges': "|".join(triggered_df.index.tolist()),
                'selected_challenge': selected.name,
                'reward_points': selected['reward_points'],
                'suppressed_challenges': "|".join(suppressed), 
                'timestamp': datetime.now()
            }
            awards_list.append(award)
            
    return pd.DataFrame(awards_list)

def check_badges(user_id, total_points):
    """Puan eşiklerine göre rozet ataması yapar [cite: 96-101]."""
    badges = []
    # Rozet baremleri: 300, 850, 1500 [cite: 99-101]
    if total_points >= 1500:
        badges.append({'user_id': user_id, 'badge_id': 'B3', 'badge_name': 'Altın İzleyici'})
    elif total_points >= 850:
        badges.append({'user_id': user_id, 'badge_id': 'B2', 'badge_name': 'Gümüş İzleyici'})
    elif total_points >= 300:
        badges.append({'user_id': user_id, 'badge_id': 'B1', 'badge_name': 'Bronz İzleyici'})
    
    return pd.DataFrame(badges)
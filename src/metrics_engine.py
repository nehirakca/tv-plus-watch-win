import pandas as pd
from datetime import timedelta

def get_user_state(user_id, as_of_date, activity_df):
    as_of_date = pd.to_datetime(as_of_date)
    
    user_history = activity_df[
        (activity_df['user_id'] == user_id) & 
        (activity_df['date'] <= as_of_date)
    ].sort_values('date', ascending=False)


    today_data = user_history[user_history['date'] == as_of_date]
    
    metrics = {
        "user_id": user_id,
        "as_of_date": as_of_date,
        "watch_minutes_today": today_data['watch_minutes'].sum() if not today_data.empty else 0,
        "episodes_completed_today": today_data['episodes_completed'].sum() if not today_data.empty else 0,
        "unique_genres_today": today_data['unique_genres'].sum() if not today_data.empty else 0,
        "watch_party_minutes_today": today_data['watch_party_minutes'].sum() if not today_data.empty else 0,
        "ratings_today": today_data['ratings'].sum() if not today_data.empty else 0,
    }

    seven_days_ago = as_of_date - timedelta(days=6)
    last_7d_df = user_history[user_history['date'] >= seven_days_ago]
    
    metrics["watch_minutes_7d"] = last_7d_df['watch_minutes'].sum()
    metrics["episodes_completed_7d"] = last_7d_df['episodes_completed'].sum()
    metrics["ratings_7d"] = last_7d_df['ratings'].sum()

    streak = 0
    current_check_date = as_of_date
    
    daily_watch_map = user_history.set_index('date')['watch_minutes'].to_dict()

    while current_check_date in daily_watch_map:
        if daily_watch_map[current_check_date] >= 30:
            streak += 1
            current_check_date -= timedelta(days=1)
        else:
            break
    
    metrics["watch_streak_days"] = streak
    return metrics

def enrich_activity_with_names(activity_df, shows_df):
    """ID listelerini okunabilir isim listelerine dönüştürür."""
    show_map = shows_df.set_index('show_id')['show_name'].to_dict()
    
    def map_ids_to_names(id_string):
        if pd.isna(id_string) or id_string == "":
            return "İzleme Yok"
        ids = str(id_string).split('|')
        # ID katalogda yoksa ID'nin kendisini bırak, varsa ismini al
        names = [show_map.get(show_id, show_id) for show_id in ids]
        return ", ".join(names)

    enriched_df = activity_df.copy()
    enriched_df['watched_show_names'] = enriched_df['shows_watched'].apply(map_ids_to_names)
    return enriched_df

def generate_all_user_states(as_of_date, users_df, activity_df):
    all_states = []
    for user_id in users_df['user_id']:
        state = get_user_state(user_id, as_of_date, activity_df)
        all_states.append(state)
    
    # Tüm kullanıcı durumlarını bir DataFrame'de topla
    return pd.DataFrame(all_states)

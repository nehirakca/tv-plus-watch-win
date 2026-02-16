import pandas as pd 

# Tüm temel veri kaynaklarını okuyup analiz için hazırlar.

# Kullanıcı, aktivite, içerik ve bölüm verilerini okuyup dataframe olarak döndürür.
def load_all_data():
    users = pd.read_csv("data/users.csv")
    activity = pd.read_csv("data/activity_events.csv",parse_dates=["date"])
    shows = pd.read_csv("data/shows.csv")
    episodes = pd.read_csv("data/episodes.csv")

    return users, activity, shows, episodes 

def get_catalog_maps(shows_df):
    """Show ID'lerini isimlere eşleyen bir sözlük döner."""
    # show_id -> show_name eşleyen bir sözlük üretir.
    return shows_df.set_index('show_id')['show_name'].to_dict()
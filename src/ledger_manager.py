import pandas as pd
import uuid
from datetime import datetime

# Puan hareketlerini(ledger) yönetir ve ödül/rozet kayıtlarını dosyaya kaydeder.

class LedgerManager:
    def __init__(self):
        self.ledger_columns = [
            'ledger_id', 'user_id', 'points_delta', 
            'source', 'source_ref', 'created_at'
        ]
        # Eğer outputs/points_ledger.csv varsa onu yükle, yoksa boş başlat
        import os
        ledger_path = 'outputs/points_ledger.csv'
        if os.path.exists(ledger_path):
            self.ledger_df = pd.read_csv(ledger_path)
        else:
            self.ledger_df = pd.DataFrame(columns=self.ledger_columns)

    # Bir kullanıcıya puan ekler, kaynağını ve referansını(örn.challenge ödülü) kaydeder.
    def add_entry(self, user_id, points, source, source_ref):
        # Puan hareketlerini ledger mantığı ile kaydeder.
        new_entry = {
            'ledger_id': str(uuid.uuid4()),
            'user_id': user_id,
            'points_delta': points,
            'source': source, 
            'source_ref': source_ref, 
            'created_at': datetime.now()
        }
        self.ledger_df = pd.concat([self.ledger_df, pd.DataFrame([new_entry])], ignore_index=True)

    # Bir kullanıcının toplam puanını ledger üzerinden hesaplar.
    def get_total_points(self, user_id):
        # Toplam puanları ledger üzerinden türetir.
        user_ledger = self.ledger_df[self.ledger_df['user_id'] == user_id]
        return user_ledger['points_delta'].sum()

    # Puan defteri, challenge ödülleri ve rozet ödüllerini CSV olarak outputs klasörüne kaydeder.
    def save_outputs(self, challenge_awards_df, badge_awards_df):
        # Hesaplanan ödülleri ve puan defterini diske kaydeder.

        import os
        if not os.path.exists('outputs'):
            os.makedirs('outputs')
            
        # Puan defterini kaydet 
        self.ledger_df.to_csv('outputs/points_ledger.csv', index=False)
        
        # Challenge ödüllerini kaydet
        challenge_awards_df.to_csv('outputs/challenge_awards.csv', index=False)
        
        # Rozet ödüllerini kaydet 
        badge_awards_df.to_csv('outputs/badge_awards.csv', index=False)
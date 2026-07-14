import pandas as pd
import numpy as np
from scipy import stats

from check import Check

class OutliersCheck(Check):
    """Проверка выбросов"""
    
    def run(self, columns, params=None):
        params = params or {}
        threshold = params.get('threshold', self.config.OUTLIER_THRESHOLD)
        min_score = params.get('min_score', self.config.OUTLIER_MIN_SCORE)
        max_score = params.get('max_score', self.config.OUTLIER_MAX_SCORE)
        
        for column in columns:
            if column not in self.df.columns:
                print(f"!  Колонка '{column}' не найдена, пропускаем проверку выбросов")
                continue
            
            data = self.df[column].dropna()
            if len(data) < 5:
                continue
            
            z_scores = np.abs(stats.zscore(data))
            outlier_indices = data.index[z_scores > threshold]
            
            if len(outlier_indices) > 0:
                print(f"!  Найдено {len(outlier_indices)} выбросов в колонке {column}")
                for idx in outlier_indices:
                    value = data[idx]
                    mean_val = data.mean()
                    z_score = z_scores[idx]
                    score = min(min_score + (z_score - threshold) / 2, max_score)
                    self._add_risk([idx], round(score, 1), 
                                  f"Выброс в {column}: {value} (среднее {mean_val:.1f})")
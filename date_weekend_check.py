import pandas as pd
from check import Check

class DateWeekendCheck(Check):
    """Проверка отчетов в выходные"""
    
    def run(self, columns, params=None):
        params = params or {}
        threshold = params.get('threshold', self.config.WEEKEND_THRESHOLD)
        score = params.get('score', self.config.WEEKEND_SCORE)
        high_score = params.get('high_score', self.config.WEEKEND_HIGH_SCORE)
        min_records = params.get('min_records', self.config.CONSTANT_MIN_RECORDS)
        
        manager_col = self._find_manager_column()
        
        for column in columns:
            if column not in self.df.columns:
                print(f"!  Колонка '{column}' не найдена, пропускаем проверку дат")
                continue
            
            dates = pd.to_datetime(self.df[column], errors='coerce')
            
            if manager_col is None:
                weekend_count = (dates.dt.dayofweek >= 5).sum()
                weekend_percent = weekend_count / len(self.df) * 100
                if weekend_percent > threshold:
                    print(f"!  {weekend_count} записей ({weekend_percent:.1f}%) в выходные")
                    weekend_indices = self.df.index[dates.dt.dayofweek >= 5]
                    self._add_risk(weekend_indices.tolist(), score, 
                                  "Отчет в выходной день")
            else:
                for manager, group in self.df.groupby(manager_col):
                    if len(group) < min_records:
                        continue
                    group_dates = pd.to_datetime(group[column], errors='coerce')
                    weekend_percent = (group_dates.dt.dayofweek >= 5).mean() * 100
                    
                    if weekend_percent > threshold:
                        print(f"!  Менеджер {manager}: {weekend_percent:.1f}% отчетов в выходные")
                        self._add_risk(group.index.tolist(), high_score, 
                                      f"Слишком много отчетов в выходные ({weekend_percent:.1f}%)")
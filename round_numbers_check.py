from check import Check

class RoundNumbersCheck(Check):    
    def run(self, columns, params=None):
        params = params or {}
        threshold = params.get('threshold', self.config.ROUND_NUMBERS_THRESHOLD)
        score = params.get('score', self.config.ROUND_NUMBERS_SCORE)
        min_records = params.get('min_records', self.config.LOW_VARIATION_MIN_RECORDS)
        
        manager_col = self._find_manager_column()
        if manager_col is None:
            return
        
        for column in columns:
            if column not in self.df.columns:
                print(f"!  Колонка '{column}' не найдена, пропускаем проверку круглых чисел")
                continue
            
            for manager, group in self.df.groupby(manager_col):
                if len(group) < min_records:
                    continue
                
                values = group[column]
                round_percent = (values % 100 == 0).mean() * 100
                if round_percent > threshold:
                    print(f"!  Менеджер {manager}: {round_percent:.1f}% значений {column} кратны 100")
                    self._add_risk(group.index.tolist(), score, 
                                  f"{round_percent:.1f}% значений {column} кратны 100")
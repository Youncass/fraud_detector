from check import Check

class LowVariationCheck(Check):
    def run(self, columns, params=None):
        params = params or {}
        min_records = params.get('min_records', self.config.LOW_VARIATION_MIN_RECORDS)
        threshold = params.get('threshold', self.config.LOW_VARIATION_THRESHOLD)
        score = params.get('score', self.config.LOW_VARIATION_SCORE)
        
        manager_col = self._find_manager_column()
        if manager_col is None:
            return
        
        for column in columns:
            if column not in self.df.columns:
                print(f"!  Колонка '{column}' не найдена, пропускаем проверку вариации")
                continue
            
            for manager, group in self.df.groupby(manager_col):
                if len(group) < min_records:
                    continue
                
                values = group[column]
                std = values.std()
                mean = values.mean()
                if mean != 0 and std / mean < threshold:
                    print(f"!  Менеджер {manager}: слишком маленькая вариация {column} (std={std:.2f})")
                    self._add_risk(group.index.tolist(), score, 
                                  f"Слишком маленькая вариация {column}")
from check import Check

class LogicalCorrelationCheck(Check):
    """Проверка логической корреляции между колонками"""
    
    def run(self, columns, params=None):
        params = params or {}
        min_correlation = params.get('min_correlation', self.config.LOGICAL_CORRELATION_THRESHOLD)
        score = params.get('score', self.config.LOGICAL_SCORE)
        global_score = params.get('global_score', self.config.LOGICAL_GLOBAL_SCORE)
        
        if len(columns) < 2:
            print(f"!  Для корреляции нужно минимум 2 колонки")
            return
        
        col1, col2 = columns[0], columns[1]
        
        if col1 not in self.df.columns or col2 not in self.df.columns:
            print(f"!  Колонки '{col1}' или '{col2}' не найдены, пропускаем проверку")
            return
        
        manager_col = self._find_manager_column()
        
        if manager_col:
            for manager, group in self.df.groupby(manager_col):
                if len(group) < 5:
                    continue
                
                clean_group = group[[col1, col2]].dropna()
                if len(clean_group) < 5:
                    continue
                
                corr = clean_group[col1].corr(clean_group[col2])
                if corr < min_correlation:
                    print(f"!  Менеджер {manager}: нелогичная связь {col1}-{col2} (корр={corr:.2f})")
                    self._add_risk(group.index.tolist(), score, 
                                  f"Нелогичная связь {col1} и {col2}")
        else:
            clean_data = self.df[[col1, col2]].dropna()
            if len(clean_data) >= 5:
                corr = clean_data[col1].corr(clean_data[col2])
                if corr < min_correlation:
                    print(f"!  Нелогичная связь между {col1} и {col2} (корр={corr:.2f})")
                    self._add_risk(self.df.index.tolist(), global_score, 
                                  f"Нелогичная связь {col1} и {col2}")
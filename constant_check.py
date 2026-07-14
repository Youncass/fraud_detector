from check import Check

class ConstantCheck(Check):    
    def run(self, columns, params=None):
        params = params or {}
        min_records = params.get('min_records', self.config.CONSTANT_MIN_RECORDS)
        score = params.get('score', self.config.CONSTANT_SCORE)
        
        manager_col = self._find_manager_column()
        if manager_col is None:
            return
        
        for column in columns:
            if column not in self.df.columns:
                print(f"!  Колонка '{column}' не найдена, пропускаем проверку констант")
                continue
            
            for manager, group in self.df.groupby(manager_col):
                if len(group) < min_records:
                    continue
                
                values = group[column]
                if values.nunique() == 1:
                    print(f"!  Менеджер {manager}: все значения {column} одинаковые ({values.iloc[0]})")
                    self._add_risk(group.index.tolist(), score, 
                                  f"Все {column} одинаковые: {values.iloc[0]}")
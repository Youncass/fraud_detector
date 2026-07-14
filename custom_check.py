from check import Check

class CustomCheck(Check):
    """Пользовательская проверка с произвольной функцией"""
    
    def run(self, columns, params=None):
        params = params or {}
        func = params.get('func')
        score = params.get('score', 1.0)
        reason = params.get('reason', 'Нарушение пользовательского правила')
        
        if not callable(func):
            print(f"!  Пользовательская проверка: func должна быть функцией")
            return
        
        for column in columns:
            if column not in self.df.columns:
                print(f"!  Колонка '{column}' не найдена, пропускаем пользовательскую проверку")
                continue
            
            try:
                mask = self.df[column].apply(func)
                violation_indices = self.df.index[mask]
                
                if len(violation_indices) > 0:
                    print(f"!  Пользовательская проверка '{column}': {len(violation_indices)} нарушений")
                    for idx in violation_indices:
                        value = self.df.loc[idx, column]
                        self._add_risk([idx], score, f"{reason}: {value}")
            except Exception as e:
                print(f"!  Ошибка в пользовательской проверке '{column}': {e}")

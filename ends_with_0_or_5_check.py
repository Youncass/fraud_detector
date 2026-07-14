from check import Check

class EndsWith0or5Check(Check):
    """Проверка на числа, оканчивающиеся на 0 или 5"""
    
    def run(self, columns, params=None):
        params = params or {}
        threshold = params.get('threshold', self.config.ENDS_WITH_0_OR_5_THRESHOLD)
        score = params.get('score', self.config.ENDS_WITH_0_OR_5_SCORE)
        min_records = 10
        
        for column in columns:
            if column not in self.df.columns:
                print(f"!  Колонка '{column}' не найдена, пропускаем проверку")
                continue
            
            data = self.df[column].dropna()
            if len(data) < min_records:
                continue
            
            ends_with_0_or_5 = ((data % 5 == 0) | (data % 10 == 0)).mean() * 100
            if ends_with_0_or_5 > threshold:
                print(f"!  {ends_with_0_or_5:.1f}% значений {column} оканчиваются на 0 или 5")
                mask = (data % 5 == 0) | (data % 10 == 0)
                indices = data.index[mask]
                self._add_risk(indices.tolist(), score, 
                              f"Подозрительно круглое число в {column}")
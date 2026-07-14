from check import Check

class BenfordCheck(Check):
    def run(self, columns, params=None):
        params = params or {}
        deviation_threshold = params.get('deviation_threshold', self.config.BENFORD_DEVIATION_THRESHOLD)
        score = params.get('score', self.config.BENFORD_SCORE)
        min_records = params.get('min_records', self.config.BENFORD_MIN_RECORDS)
        
        for column in columns:
            if column not in self.df.columns:
                print(f"!  Колонка '{column}' не найдена, пропускаем проверку Бенфорда")
                continue
            
            data = self.df[self.df[column] > 0][column]
            if len(data) < min_records:
                continue
            
            first_digits = data.astype(str).str[0].astype(int)
            observed = first_digits.value_counts(normalize=True).sort_index()
            
            expected = {1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097, 
                       5: 0.079, 6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046}
            
            deviation = 0
            for digit in range(1, 10):
                obs = observed.get(digit, 0)
                exp = expected[digit]
                deviation += abs(obs - exp)
            
            if deviation > deviation_threshold:
                print(f"!  Закон Бенфорда нарушен в колонке {column}: отклонение {deviation*100:.1f}%")
                self._add_risk(self.df.index.tolist(), score, 
                              f"Нарушение закона Бенфорда в {column}")
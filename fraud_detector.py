import pandas as pd
import numpy as np

from checks.benford_check import BenfordCheck
from checks.outliers_check import OutliersCheck
from checks.constant_check import ConstantCheck
from checks.low_variation_check import LowVariationCheck
from checks.round_numbers_check import RoundNumbersCheck
from checks.ends_with_0_or_5_check import EndsWith0or5Check
from checks.date_weekend_check import DateWeekendCheck
from checks.logical_correlation_check import LogicalCorrelationCheck
from checks.custom_check import CustomCheck

CHECK_REGISTRY = {
    'benford': BenfordCheck,
    'outliers': OutliersCheck,
    'constant': ConstantCheck,
    'low_variation': LowVariationCheck,
    'round_numbers': RoundNumbersCheck,
    'ends_with_0_or_5': EndsWith0or5Check,
    'date_weekend': DateWeekendCheck,
    'logical_correlation': LogicalCorrelationCheck,
    'custom': CustomCheck,
}

AUTO_RULES = {
    'outliers': {
        'column_filter': lambda col, df: col in df.select_dtypes(include=[np.number]).columns,
        'params': {}
    },
    'constant': {
        'column_filter': lambda col, df: col in df.select_dtypes(include=[np.number]).columns,
        'params': {}
    },
    'low_variation': {
        'column_filter': lambda col, df: col in df.select_dtypes(include=[np.number]).columns,
        'params': {}
    },
    'round_numbers': {
        'column_filter': lambda col, df: col in df.select_dtypes(include=[np.number]).columns,
        'params': {}
    },
    'ends_with_0_or_5': {
        'column_filter': lambda col, df: col in df.select_dtypes(include=[np.number]).columns,
        'params': {}
    },
    'date_weekend': {
        'column_filter': lambda col, df: 'date' in col.lower() or 'дата' in col.lower(),
        'params': {}
    },
    'logical_correlation': {
        'column_filter': None, # Специальная обработка
        'params': {}
    },
}

class FraudDetector:
    def __init__(self, df, config):
        self.df = df.copy()
        self.config = config
        self.column_types = self._detect_column_types()
        self.risk_scores = pd.Series([0.0] * len(self.df))
        self.risk_reasons = pd.Series([''] * len(self.df))
        
    def _detect_column_types(self):
        types = {'numeric': [], 'text': [], 'date': [], 'id': []}
        
        for col in self.df.columns:
            col_lower = col.lower()
            if any(key in col_lower for key in self.config.ID_KEYWORDS):
                types['id'].append(col)
            elif any(key in col_lower for key in self.config.DATE_KEYWORDS):
                types['date'].append(col)
            elif pd.api.types.is_numeric_dtype(self.df[col]):
                types['numeric'].append(col)
            else:
                types['text'].append(col)
                
        return types
    
    def _add_risk(self, indices, score, reason):
        if not isinstance(indices, (list, pd.Index)):
            indices = [indices]
        
        for idx in indices:
            self.risk_scores[idx] = float(self.risk_scores[idx]) + float(score)
            if self.risk_reasons[idx]:
                if reason not in self.risk_reasons[idx]:
                    self.risk_reasons[idx] += f"; {reason}"
            else:
                self.risk_reasons[idx] = reason
    
    def _find_manager_column(self):
        for col in self.column_types['id']:
            if any(key in col.lower() for key in self.config.MANAGER_KEYWORDS):
                return col
        return None
    
    def _get_columns_for_auto_rule(self, rule_config):
        column_filter = rule_config.get('column_filter')
        
        if column_filter is None:
            return []
        
        if callable(column_filter):
            return [col for col in self.df.columns if column_filter(col, self.df)]
        
        return []
    
    def _run_check(self, check_name, columns, params=None):
        """Запуск конкретной проверки для указанных колонок"""
        if check_name not in CHECK_REGISTRY:
            print(f"!  Проверка '{check_name}' не найдена")
            return
        
        check_class = CHECK_REGISTRY[check_name]
        check_instance = check_class(self)
        check_instance.run(columns, params or {})
    
    def _run_auto_checks(self):
        print("Запуск автоматических проверок...")
        
        for rule_name, rule_config in AUTO_RULES.items():
            if rule_name == 'logical_correlation':
                continue
            
            columns = self._get_columns_for_auto_rule(rule_config)
            if columns:
                params = rule_config.get('params', {})
                print(f"   → {rule_name}: {len(columns)} колонок")
                self._run_check(rule_name, columns, params)
        
        self._run_logical_correlation_auto()
    
    def _run_logical_correlation_auto(self):
        numeric_cols = self.column_types['numeric']
        if len(numeric_cols) < 2:
            return
        
        logical_pairs = []
        for col1 in numeric_cols:
            for col2 in numeric_cols:
                if col1 >= col2:
                    continue
                for pair_def in self.config.LOGICAL_PAIRS:
                    if (any(key in col1.lower() for key in pair_def[0]) and 
                        any(key in col2.lower() for key in pair_def[1])):
                        logical_pairs.append((col1, col2))
                        break
        
        if logical_pairs:
            print(f"   → logical_correlation: {len(logical_pairs)} пар колонок")
            for col1, col2 in logical_pairs:
                self._run_check('logical_correlation', [col1, col2])
    
    def _run_custom_rules(self):
        if not hasattr(self.config, 'CUSTOM_RULES'):
            return
        
        print("Запуск пользовательских правил...")
        
        for rule_name, rule_config in self.config.CUSTOM_RULES.items():
            check_name = rule_config.get('check')
            columns = rule_config.get('columns', [])
            params = rule_config.get('params', {})
            
            if not columns:
                print(f"!  Правило '{rule_name}': не указаны колонки")
                continue
            
            print(f"-> {rule_name}: {check_name} для {len(columns)} колонок")
            self._run_check(check_name, columns, params)
    
    def analyze(self):
        print("Запуск анализа данных...")
        print(f"Обнаружено колонок: {len(self.df.columns)}")
        print(f"Числовых: {len(self.column_types['numeric'])}")
        print(f"Текстовых: {len(self.column_types['text'])}")
        print(f"Дата-колонок: {len(self.column_types['date'])}")
        print(f"ID-колонок: {len(self.column_types['id'])}")
        print("-" * 50)
        
        self._run_auto_checks()
        self._run_custom_rules()
        
        self.df['Risk_Score'] = np.round(self.risk_scores, 2)
        self.df['Risk_Reasons'] = self.risk_reasons
        
        self.df['Status'] = self.df['Risk_Score'].apply(
            lambda x: '*  ФЕЙК' if x >= self.config.FAKE_THRESHOLD else 
                      ('!  ПОДОЗРИТЕЛЬНО' if x >= self.config.SUSPICIOUS_THRESHOLD else ':) ОК')
        )
        
        print("-" * 50)
        print(f":) Анализ завершен!")
        print(f"Распределение статусов:")
        print(self.df['Status'].value_counts())
        print(f"\nСредний риск: {self.df['Risk_Score'].mean():.2f}")
        print(f"Максимальный риск: {self.df['Risk_Score'].max():.2f}")
        
        manager_col = self._find_manager_column()
        if manager_col:
            print("\nТОП-3 подозрительных менеджера:")
            manager_stats = self.df.groupby(manager_col)['Risk_Score'].mean().sort_values(ascending=False)
            print(manager_stats.head(3))
        
        return self.df
    
    def generate_report(self, output_path='fraud_report.xlsx'):
        result_df = self.df.sort_values('Risk_Score', ascending=False)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            result_df.to_excel(writer, sheet_name='Результаты', index=False)
            
            summary = pd.DataFrame({
                'Метрика': ['Всего записей', 'ОК', 'Подозрительно', 'Фейк'],
                'Значение': [
                    len(result_df),
                    len(result_df[result_df['Status'] == ':) ОК']),
                    len(result_df[result_df['Status'] == '!  ПОДОЗРИТЕЛЬНО']),
                    len(result_df[result_df['Status'] == '*  ФЕЙК'])
                ]
            })
            summary.to_excel(writer, sheet_name='Сводка', index=False)
            
            manager_col = self._find_manager_column()
            if manager_col:
                manager_summary = result_df.groupby(manager_col).agg({
                    'Risk_Score': ['mean', 'max', 'count'],
                    'Status': lambda x: (x == '*  ФЕЙК').sum()
                }).round(2)
                manager_summary.columns = ['Средний_риск', 'Макс_риск', 'Кол-во_отчетов', 'Фейков']
                manager_summary = manager_summary.sort_values('Средний_риск', ascending=False)
                manager_summary.to_excel(writer, sheet_name='Менеджеры')
        
        print(f"Отчет сохранен в: {output_path}")

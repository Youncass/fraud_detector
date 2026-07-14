class DetectionConfig:
    OUTLIER_THRESHOLD = 2.5
    OUTLIER_MIN_SCORE = 1.0
    OUTLIER_MAX_SCORE = 3.0
    
    CONSTANT_MIN_RECORDS = 3
    CONSTANT_SCORE = 3.0
    LOW_VARIATION_MIN_RECORDS = 5
    LOW_VARIATION_THRESHOLD = 0.05
    LOW_VARIATION_SCORE = 2.0
    ROUND_NUMBERS_THRESHOLD = 50
    ROUND_NUMBERS_SCORE = 1.5
    ENDS_WITH_0_OR_5_THRESHOLD = 70
    ENDS_WITH_0_OR_5_SCORE = 1.0
    
    WEEKEND_THRESHOLD = 30
    WEEKEND_SCORE = 1.5
    WEEKEND_HIGH_SCORE = 2.0
    
    LOGICAL_CORRELATION_THRESHOLD = 0.1
    LOGICAL_SCORE = 2.0
    LOGICAL_GLOBAL_SCORE = 1.5
    
    BENFORD_DEVIATION_THRESHOLD = 0.10
    BENFORD_SCORE = 0.5
    BENFORD_MIN_RECORDS = 10
    
    SUSPICIOUS_THRESHOLD = 1.5
    FAKE_THRESHOLD = 4.0
    
    ID_KEYWORDS = ['id', 'код', 'номер', 'фио', 'имя', 'фамилия', 'менеджер', 'торг']
    DATE_KEYWORDS = ['date', 'дата', 'время']
    MANAGER_KEYWORDS = ['менеджер', 'торг', 'фио', 'имя']
    BENFORD_KEYWORDS = ['сумм', 'продаж', 'выручка', 'доход']
    
    LOGICAL_PAIRS = [
        (['пробег', 'километр', 'км'], ['расход', 'топливо', 'бензин', 'литр']),
        (['сумм', 'продаж', 'выручка'], ['количеств', 'визит', 'чек', 'единиц']),
        (['сумм', 'продаж', 'выручка'], ['пробег', 'километр', 'км']),
    ]
    
    # ========== ПОЛЬЗОВАТЕЛЬСКИЕ ПРАВИЛА ==========
    # Формат: {
    #   'check_name': {
    #       'columns': ['col1', 'col2', ...],  # список колонок для проверки
    #       'params': {...}                     # параметры для проверки (переопределяют стандартные)
    #   }
    # }
    #
    # Доступные проверки:
    #   - benford: Закон Бенфорда
    #   - outliers: Выбросы
    #   - constant: Однообразие значений
    #   - low_variation: Малая вариация
    #   - round_numbers: Круглые числа (кратные 100)
    #   - ends_with_0_or_5: Числа, оканчивающиеся на 0 или 5
    #   - date_weekend: Отчеты в выходные
    #   - logical_correlation: Логическая связь между колонками
    #   - custom: Пользовательская функция
    
    CUSTOM_RULES = { # Примеры:
        'benford_sales': {
            'check': 'benford',
            'columns': ['Сумма_продаж'],
            'params': {
                'deviation_threshold': 0.08,
                'score': 1.0
            }
        },
        'outliers_sales': {
            'check': 'outliers',
            'columns': ['Сумма_продаж'],
            'params': {
                'threshold': 3.0,
                'score': 2.0
            }
        },
        'visits_range': {
            'check': 'custom',
            'columns': ['Количество_визитов'],
            'params': {
                'func': lambda x: (x < 1) | (x > 30),
                'score': 2.0,
                'reason': 'Нереалистичное количество визитов'
            }
        },
        'correlation_mileage_fuel': {
            'check': 'logical_correlation',
            'columns': ['Пробег_авто', 'Расход_топлива'],
            'params': {
                'min_correlation': 0.3,
                'score': 2.0
            }
        },
        'non_negative_sales': {
            'check': 'custom',
            'columns': ['Сумма_продаж'],
            'params': {
                'func': lambda x: x < 0,
                'score': 3.0,
                'reason': 'Отрицательная сумма продаж'
            }
        }
    }

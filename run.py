import pandas as pd
import numpy as np

from detection_config import DetectionConfig
from fraud_detector import FraudDetector


def create_test_data(use_anomalies):
    np.random.seed(42)
    
    managers = ['Иванов', 'Петров', 'Сидоров', 'Козлов', 'Смирнов']
    n_per_manager = 20
    
    data = []
    for i, manager in enumerate(managers):
        for j in range(n_per_manager):
            mileage = np.random.normal(500, 50)
            row = {
                'Менеджер': manager,
                'Дата_отчета': pd.Timestamp('2024-01-01') + pd.Timedelta(days=i*n_per_manager + j),
                'Сумма_продаж': int(np.random.normal(1000, 200)),
                'Количество_визитов': int(np.random.poisson(10)),
                'Пробег_авто': int(mileage),
                'Расход_топлива': int(mileage / 20 + np.random.normal(20, 3))
            }

            if use_anomalies:
                if manager == 'Иванов':
                    row['Сумма_продаж'] = 1000
                elif manager == 'Петров' and j < 5:
                    row['Сумма_продаж'] = np.random.choice([10000, 8000])
                elif manager == 'Сидоров':
                    row['Дата_отчета'] = pd.Timestamp('2024-01-06') + pd.Timedelta(weeks=j)
                elif manager == 'Козлов':
                    row['Количество_визитов'] = 15
                elif manager == 'Смирнов' and j < 5:
                    row['Пробег_авто'] = np.random.choice([1000, 1200])
                    row['Расход_топлива'] = 40
            data.append(row)
    
    return pd.DataFrame(data)


if __name__ == "__main__":
    USE_ANOMALIES = True
    
    if USE_ANOMALIES:
        print("Генерация данных С АНОМАЛИЯМИ...")
    else:
        print("📝 Генерация ЧИСТЫХ данных...")
    df = create_test_data(USE_ANOMALIES)
    
    print(f"Создано {len(df)} записей")
    
    detector = FraudDetector(df, DetectionConfig())
    results = detector.analyze()
    detector.generate_report('fraud_report.xlsx')
    
    print("\n*  ПОДОЗРИТЕЛЬНЫЕ ОТЧЕТЫ:")
    suspicious = results[results['Risk_Score'] >= 1.5].sort_values('Risk_Score', ascending=False)
    
    if len(suspicious) > 0:
        print(suspicious[['Менеджер', 'Дата_отчета', 'Сумма_продаж', 
                         'Количество_визитов', 'Risk_Score', 'Risk_Reasons', 'Status']].head(10))
    else:
        print(":) Подозрительных отчетов не найдено!")

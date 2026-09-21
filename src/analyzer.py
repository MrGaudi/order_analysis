import os
import logging
import pandas as pd
import config


class OrderAnalyzer:
    def __init__(self):
        os.makedirs(config.LOGS_DIR, exist_ok=True)
        os.makedirs(config.REPORTS_DIR, exist_ok=True)

        logging.basicConfig(
            filename=os.path.join(config.LOGS_DIR, "errors.log"),
            level=logging.ERROR,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        self.logger = logging.getLogger(__name__)

    def load_file(self, file_path):
        try:
            return pd.read_csv(file_path)
        except Exception as error:
            self.logger.error(f"Ошибка при чтении файла {file_path}: {error}")
            return None

    def filter_delivered(self, df):
        return df[df[config.STATUS_COLUMN] == config.DELIVERED_STATUS]

    def calculate_metrics(self, df):
        total_sum = df["total_amount"].sum()
        avg_bill = df["total_amount"].mean()
        total_count = len(df)

        return {
            "total_revenue": total_sum,
            "average_check": avg_bill,
            "order_count": total_count
        }

    def process_file(self, file_path):
        try:
            df = self.load_file(file_path)

            if df is None:
                return None

            df = self.filter_delivered(df)

            metrics = self.calculate_metrics(df)

            metrics["file_name"] = os.path.basename(file_path)

            return metrics

        except Exception as error:
            self.logger.error(f"Ошибка при обработке файла {file_path}: {error}")
            return None

    def process_all_files(self):

        files = os.listdir(config.DATA_DIR)

        results = []

        processed_count = 0
        error_count = 0

        for file_name in files:
            if file_name.endswith(".csv"):

                file_path = os.path.join(config.DATA_DIR, file_name)
                metrics = self.process_file(file_path)

                if metrics is not None:
                    results.append(metrics)
                    processed_count += 1
                else:
                    error_count += 1

        df_results = pd.DataFrame(results)

        df_results.to_csv(os.path.join(config.REPORTS_DIR, config.REPORT_FILE), index=False)

        print(f"Обработано файлов: {processed_count}")
        print(f"Файлов с ошибками: {error_count}")


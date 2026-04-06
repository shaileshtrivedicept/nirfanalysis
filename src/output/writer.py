import pandas as pd
import json
import os

class DatasetWriter:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def export_csv(self, data, filename):
        """
        Export data to CSV.
        """
        if not data:
            return
        df = pd.DataFrame(data)
        file_path = os.path.join(self.output_dir, filename)
        df.to_csv(file_path, index=False)

    def export_json(self, data, filename):
        """
        Export data to JSON.
        """
        if not data:
            return
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def save_log(self, log_content, filename):
        """
        Save processing log.
        """
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, 'w') as f:
            f.write(log_content)

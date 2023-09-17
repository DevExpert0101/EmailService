import csv
import io

from django.core.files import File


def create_exported_csv(file_name, headers, rows):
    f = io.StringIO()
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)
    return File(io.BytesIO(f.getvalue().encode()), name=file_name)

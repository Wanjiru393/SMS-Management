import csv
from django.core.management.base import BaseCommand
from sms_management.models import CustomerInformation
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = 'Import customers from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        try:
            with open(csv_file_path, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)  # Get the header row

                # Mapping fields dynamically based on the CSV header
                field_mapping = {
                    'full_name': header[0],
                    'contact': header[1],
                    'acc_number': header[2] if len(header) > 2 else None
                }

                for row in reader:
                    customer_data = {}
                    for field, index in field_mapping.items():
                        customer_data[field] = row[header.index(index)]

                    try:
                        _, created = CustomerInformation.objects.get_or_create(**customer_data)
                    except ValidationError as e:
                        self.stdout.write(self.style.ERROR(f"Validation error for row {row}: {e}"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file_path}"))
        except csv.Error:
            self.stdout.write(self.style.ERROR(f"Error reading CSV file: {csv_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An unexpected error occurred: {e}"))

        

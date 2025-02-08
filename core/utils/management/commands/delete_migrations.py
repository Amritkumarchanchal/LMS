import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Delete all migration files in the core apps."

    def handle(self, *args, **kwargs):
        # Get the project root (where manage.py is located)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        core_path = os.path.join(project_root, "../")  # Target the core folder
        print(core_path)

        # Ensure the core directory exists
        if not os.path.exists(core_path):
            self.stderr.write("Core folder not found.")
            return

        # Loop through each app folder in core
        for app_name in os.listdir(core_path):
            app_path = os.path.join(core_path, app_name)
            if os.path.isdir(app_path):  # Ensure it's a directory
                migrations_path = os.path.join(app_path, "migrations")
                if os.path.exists(migrations_path):
                    # Delete all migration files except __init__.py
                    for migration_file in os.listdir(migrations_path):
                        if migration_file != "__init__.py" and migration_file.endswith(".py"):
                            file_path = os.path.join(migrations_path, migration_file)
                            os.remove(file_path)
                            self.stdout.write(f"Deleted: {file_path}")
        self.stdout.write("All migration files in core apps deleted successfully.")

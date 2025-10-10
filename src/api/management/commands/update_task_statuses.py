# src/api/management/commands/update_task_statuses.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Task

class Command(BaseCommand):
    help = 'Updates the status of overdue tasks from "ongoing" to "completed".'

    def handle(self, *args, **options):
        now = timezone.now()
        self.stdout.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Running task status update...")
        
        overdue_tasks = Task.objects.filter(status='ongoing', dueDate__lt=now)
        task_count = overdue_tasks.count()

        if task_count > 0:
            rows_updated = overdue_tasks.update(status='completed')
            success_message = self.style.SUCCESS(f'Successfully updated {rows_updated} task(s) to "completed".')
            self.stdout.write(success_message)
        else:
            no_tasks_message = self.style.NOTICE('No overdue tasks found to update.')
            self.stdout.write(no_tasks_message)
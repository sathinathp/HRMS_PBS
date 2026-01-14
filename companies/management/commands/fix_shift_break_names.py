from django.core.management.base import BaseCommand
from companies.models import ShiftBreak
import re


class Command(BaseCommand):
    help = 'Fix shift break names that contain template syntax or time information'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Checking for shift breaks with template syntax or time in names...")
        
        # Find breaks with curly braces or time patterns in the name
        breaks_to_fix = ShiftBreak.objects.all()
        fixed_count = 0
        
        for break_obj in breaks_to_fix:
            original_name = break_obj.name
            
            # Check if name contains template syntax
            if '{{' in original_name or '}}' in original_name:
                # Extract just the break name (before the colon or template syntax)
                clean_name = original_name.split(':')[0].strip()
                clean_name = re.sub(r'\{\{.*?\}\}', '', clean_name).strip()
                clean_name = re.sub(r'\s+', ' ', clean_name)  # Remove extra spaces
                
                if clean_name and clean_name != original_name:
                    self.stdout.write(
                        f"  Fixing: '{original_name}' -> '{clean_name}'"
                    )
                    break_obj.name = clean_name
                    break_obj.save()
                    fixed_count += 1
            
            # Check if name contains time information (e.g., "Morning Break: 10:45 - 11:00")
            elif ':' in original_name and any(char.isdigit() for char in original_name):
                # Extract just the break name (before the colon)
                clean_name = original_name.split(':')[0].strip()
                
                if clean_name and clean_name != original_name:
                    self.stdout.write(
                        f"  Fixing: '{original_name}' -> '{clean_name}'"
                    )
                    break_obj.name = clean_name
                    break_obj.save()
                    fixed_count += 1
        
        if fixed_count == 0:
            self.stdout.write(self.style.SUCCESS("✅ No issues found - all break names are clean"))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Fixed {fixed_count} shift break name(s)")
            )
            self.stdout.write("\nℹ️  Break times are now displayed from the start_time and end_time fields")

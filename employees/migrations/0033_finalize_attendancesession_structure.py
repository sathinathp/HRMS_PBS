# Generated manually - Finalize AttendanceSession structure

from django.db import migrations, models


def set_unique_constraint(apps, schema_editor):
    """Set up unique constraint after data migration"""
    from django.db import connection

    with connection.cursor() as cursor:
        # Drop old unique constraint if exists
        cursor.execute("""
            SELECT constraint_name FROM information_schema.table_constraints 
            WHERE table_name = 'employees_attendancesession' AND constraint_type = 'UNIQUE'
        """)
        constraints = cursor.fetchall()

        for (constraint_name,) in constraints:
            try:
                cursor.execute(f"""
                    ALTER TABLE employees_attendancesession DROP CONSTRAINT IF EXISTS {constraint_name}
                """)
            except:
                pass


class Migration(migrations.Migration):
    dependencies = [
        ("employees", "0032_update_attendance_and_session_models"),
    ]

    operations = [
        # Clean up old constraints
        migrations.RunPython(set_unique_constraint, migrations.RunPython.noop),
        # Set new unique constraint
        migrations.AlterUniqueTogether(
            name="attendancesession",
            unique_together={("employee", "date", "session_number")},
        ),
    ]

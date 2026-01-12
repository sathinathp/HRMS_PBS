# Generated manually - Update Attendance and AttendanceSession models

from django.db import migrations, models
import django.db.models.deletion


def migrate_attendance_session_data(apps, schema_editor):
    """Migrate data from old AttendanceSession structure to new"""
    from django.db import connection

    with connection.cursor() as cursor:
        # Check if attendance_id column exists (old structure)
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'employees_attendancesession' AND column_name = 'attendance_id'
        """)
        has_attendance_id = cursor.fetchone() is not None

        if has_attendance_id:
            # Check if employee_id column exists
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'employees_attendancesession' AND column_name = 'employee_id'
            """)
            has_employee_id = cursor.fetchone() is not None

            if not has_employee_id:
                # Add employee_id column
                cursor.execute("""
                    ALTER TABLE employees_attendancesession 
                    ADD COLUMN IF NOT EXISTS employee_id INTEGER
                """)

            # Check if date column exists
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'employees_attendancesession' AND column_name = 'date'
            """)
            has_date = cursor.fetchone() is not None

            if not has_date:
                cursor.execute("""
                    ALTER TABLE employees_attendancesession 
                    ADD COLUMN IF NOT EXISTS date DATE
                """)

            # Migrate data from attendance to employee/date
            cursor.execute("""
                UPDATE employees_attendancesession AS s
                SET employee_id = a.employee_id, date = a.date
                FROM employees_attendance AS a
                WHERE s.attendance_id = a.id AND s.employee_id IS NULL
            """)


def cleanup_old_columns(apps, schema_editor):
    """Remove old columns from AttendanceSession"""
    from django.db import connection

    with connection.cursor() as cursor:
        old_columns = [
            "attendance_id",
            "location_in",
            "location_out",
            "duration_hours",
            "user_timezone",
        ]

        for col in old_columns:
            cursor.execute(f"""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'employees_attendancesession' AND column_name = '{col}'
            """)
            if cursor.fetchone():
                # Drop any constraints first
                cursor.execute(f"""
                    ALTER TABLE employees_attendancesession DROP COLUMN IF EXISTS {col} CASCADE
                """)

        # Ensure created_at exists
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'employees_attendancesession' AND column_name = 'created_at'
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE employees_attendancesession 
                ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            """)


def cleanup_attendance_columns(apps, schema_editor):
    """Remove old columns from Attendance and add new ones"""
    from django.db import connection

    with connection.cursor() as cursor:
        # Remove old columns
        old_columns = [
            "user_timezone",
            "current_session_type",
            "daily_sessions_count",
            "max_daily_sessions",
            "total_break_hours",
            "total_working_hours",
        ]

        for col in old_columns:
            cursor.execute(f"""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'employees_attendance' AND column_name = '{col}'
            """)
            if cursor.fetchone():
                cursor.execute(f"""
                    ALTER TABLE employees_attendance DROP COLUMN IF EXISTS {col} CASCADE
                """)

        # Add new columns if missing
        new_columns = [
            ("clock_in_attempts", "INTEGER DEFAULT 0"),
            ("daily_clock_count", "INTEGER DEFAULT 0"),
            ("max_daily_clocks", "INTEGER DEFAULT 3"),
        ]

        for col_name, col_type in new_columns:
            cursor.execute(f"""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'employees_attendance' AND column_name = '{col_name}'
            """)
            if not cursor.fetchone():
                cursor.execute(f"""
                    ALTER TABLE employees_attendance ADD COLUMN {col_name} {col_type}
                """)


class Migration(migrations.Migration):
    dependencies = [
        ("employees", "0031_attendance_user_timezone"),
    ]

    operations = [
        # Step 1: Add new columns to AttendanceSession
        migrations.AddField(
            model_name="attendancesession",
            name="employee",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attendance_sessions",
                to="employees.employee",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="attendancesession",
            name="date",
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name="attendancesession",
            name="clock_in_latitude",
            field=models.DecimalField(
                blank=True, decimal_places=7, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="attendancesession",
            name="clock_in_longitude",
            field=models.DecimalField(
                blank=True, decimal_places=7, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="attendancesession",
            name="clock_out_latitude",
            field=models.DecimalField(
                blank=True, decimal_places=7, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="attendancesession",
            name="clock_out_longitude",
            field=models.DecimalField(
                blank=True, decimal_places=7, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="attendancesession",
            name="duration_minutes",
            field=models.IntegerField(
                default=0, help_text="Duration of this session in minutes"
            ),
        ),
        migrations.AddField(
            model_name="attendancesession",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="attendancesession",
            name="location_validated",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="attendancesession",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        # Step 2: Migrate data from old structure
        migrations.RunPython(
            migrate_attendance_session_data, migrations.RunPython.noop
        ),
        # Step 3: Cleanup old AttendanceSession columns
        migrations.RunPython(cleanup_old_columns, migrations.RunPython.noop),
        # Step 4: Cleanup Attendance columns
        migrations.RunPython(cleanup_attendance_columns, migrations.RunPython.noop),
        # Step 5: Alter session_type field
        migrations.AlterField(
            model_name="attendancesession",
            name="session_type",
            field=models.CharField(
                choices=[("WEB", "Web/Office"), ("REMOTE", "Remote/WFH")], max_length=50
            ),
        ),
        # Step 6: Update Meta options
        migrations.AlterModelOptions(
            name="attendancesession",
            options={"ordering": ["date", "session_number"]},
        ),
        # Step 7: Create SessionLocationLog model
        migrations.CreateModel(
            name="SessionLocationLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("latitude", models.DecimalField(decimal_places=7, max_digits=10)),
                ("longitude", models.DecimalField(decimal_places=7, max_digits=10)),
                (
                    "accuracy",
                    models.FloatField(
                        blank=True, help_text="GPS accuracy in meters", null=True
                    ),
                ),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="location_logs",
                        to="employees.attendancesession",
                    ),
                ),
            ],
            options={
                "ordering": ["-timestamp"],
            },
        ),
        # Step 8: Alter Attendance status field
        migrations.AlterField(
            model_name="attendance",
            name="status",
            field=models.CharField(
                choices=[
                    ("PRESENT", "Present"),
                    ("ABSENT", "Absent"),
                    ("HALF_DAY", "Half Day"),
                    ("LEAVE", "On Leave"),
                    ("WFH", "Work From Home"),
                    ("ON_DUTY", "On Duty"),
                    ("WEEKLY_OFF", "Weekly Off"),
                    ("HOLIDAY", "Holiday"),
                    ("MISSING_PUNCH", "Missing Punch"),
                ],
                default="ABSENT",
                max_length=20,
            ),
        ),
    ]

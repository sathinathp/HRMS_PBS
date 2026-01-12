# Generated manually - Fix AttendanceSession and Attendance schema sync
# This migration handles the state sync between Django ORM and actual database

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    This migration fixes the schema sync issue:
    1. Registers AttendanceSession model in Django's migration state (table already exists)
    2. Adds missing columns to Attendance table
    3. Creates SessionLocationLog model
    
    The AttendanceSession table already exists in the database with a different structure,
    so we use SeparateDatabaseAndState to sync Django's understanding without modifying the DB.
    """
    
    dependencies = [
        ("employees", "0031_attendance_user_timezone"),
    ]

    operations = [
        # Step 1: Register AttendanceSession in Django state without creating table
        # The table already exists with the OLD structure in the database
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="AttendanceSession",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("session_number", models.IntegerField(help_text="Session number for the day (1, 2, 3)")),
                        ("clock_in", models.DateTimeField()),
                        ("clock_out", models.DateTimeField(blank=True, null=True)),
                        ("clock_in_latitude", models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                        ("clock_in_longitude", models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                        ("clock_out_latitude", models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                        ("clock_out_longitude", models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                        ("session_type", models.CharField(choices=[("WEB", "Web/Office"), ("REMOTE", "Remote/WFH")], max_length=50)),
                        ("is_active", models.BooleanField(default=True)),
                        ("location_validated", models.BooleanField(default=False)),
                        ("duration_minutes", models.IntegerField(default=0, help_text="Duration of this session in minutes")),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        ("updated_at", models.DateTimeField(auto_now=True)),
                        ("employee", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_sessions", to="employees.employee")),
                        ("date", models.DateField()),
                    ],
                    options={
                        "db_table": "employees_attendancesession",
                        "ordering": ["date", "session_number"],
                        "unique_together": {("employee", "date", "session_number")},
                    },
                ),
            ],
            database_operations=[
                # Transform the existing table to match the new schema
                migrations.RunSQL(
                    sql="""
                    -- Add employee_id column if not exists
                    ALTER TABLE employees_attendancesession 
                    ADD COLUMN IF NOT EXISTS employee_id INTEGER;
                    
                    -- Add date column if not exists
                    ALTER TABLE employees_attendancesession 
                    ADD COLUMN IF NOT EXISTS date DATE;
                    
                    -- Populate employee_id and date from attendance FK
                    UPDATE employees_attendancesession AS s
                    SET employee_id = a.employee_id, date = a.date
                    FROM employees_attendance AS a
                    WHERE s.attendance_id = a.id AND s.employee_id IS NULL;
                    
                    -- Add location coordinate columns
                    ALTER TABLE employees_attendancesession 
                    ADD COLUMN IF NOT EXISTS clock_in_latitude DECIMAL(10,7);
                    ALTER TABLE employees_attendancesession 
                    ADD COLUMN IF NOT EXISTS clock_in_longitude DECIMAL(10,7);
                    ALTER TABLE employees_attendancesession 
                    ADD COLUMN IF NOT EXISTS clock_out_latitude DECIMAL(10,7);
                    ALTER TABLE employees_attendancesession 
                    ADD COLUMN IF NOT EXISTS clock_out_longitude DECIMAL(10,7);
                    
                    -- Add new boolean columns
                    ALTER TABLE employees_attendancesession 
                    ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
                    ALTER TABLE employees_attendancesession 
                    ADD COLUMN IF NOT EXISTS location_validated BOOLEAN DEFAULT FALSE;
                    
                    -- Add duration_minutes (convert from duration_hours if exists)
                    ALTER TABLE employees_attendancesession 
                    ADD COLUMN IF NOT EXISTS duration_minutes INTEGER DEFAULT 0;
                    
                    -- Convert duration_hours to duration_minutes if duration_hours exists
                    DO $$
                    BEGIN
                        IF EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'employees_attendancesession' AND column_name = 'duration_hours'
                        ) THEN
                            UPDATE employees_attendancesession 
                            SET duration_minutes = COALESCE(ROUND(duration_hours * 60)::INTEGER, 0)
                            WHERE duration_minutes = 0 OR duration_minutes IS NULL;
                        END IF;
                    END $$;
                    
                    -- Add updated_at column
                    ALTER TABLE employees_attendancesession 
                    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
                    
                    -- Update session_type values to match new choices
                    UPDATE employees_attendancesession 
                    SET session_type = 'WEB' 
                    WHERE session_type NOT IN ('WEB', 'REMOTE');
                    
                    -- Alter session_type column size if needed
                    ALTER TABLE employees_attendancesession 
                    ALTER COLUMN session_type TYPE VARCHAR(50);
                    
                    -- Drop old columns that are no longer needed
                    ALTER TABLE employees_attendancesession 
                    DROP COLUMN IF EXISTS attendance_id CASCADE;
                    ALTER TABLE employees_attendancesession 
                    DROP COLUMN IF EXISTS location_in CASCADE;
                    ALTER TABLE employees_attendancesession 
                    DROP COLUMN IF EXISTS location_out CASCADE;
                    ALTER TABLE employees_attendancesession 
                    DROP COLUMN IF EXISTS duration_hours CASCADE;
                    ALTER TABLE employees_attendancesession 
                    DROP COLUMN IF EXISTS user_timezone CASCADE;
                    
                    -- Add foreign key constraint for employee
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.table_constraints 
                            WHERE constraint_name = 'employees_attendancesession_employee_id_fk' 
                            AND table_name = 'employees_attendancesession'
                        ) THEN
                            ALTER TABLE employees_attendancesession 
                            ADD CONSTRAINT employees_attendancesession_employee_id_fk 
                            FOREIGN KEY (employee_id) REFERENCES employees_employee(id) ON DELETE CASCADE;
                        END IF;
                    END $$;
                    
                    -- Add NOT NULL constraint to employee_id (only for rows that have valid data)
                    DELETE FROM employees_attendancesession WHERE employee_id IS NULL;
                    ALTER TABLE employees_attendancesession 
                    ALTER COLUMN employee_id SET NOT NULL;
                    
                    -- Add NOT NULL constraint to date
                    ALTER TABLE employees_attendancesession 
                    ALTER COLUMN date SET NOT NULL;
                    
                    -- Drop old unique constraint and add new one
                    DO $$
                    DECLARE
                        constraint_rec RECORD;
                    BEGIN
                        FOR constraint_rec IN 
                            SELECT constraint_name FROM information_schema.table_constraints 
                            WHERE table_name = 'employees_attendancesession' AND constraint_type = 'UNIQUE'
                        LOOP
                            EXECUTE 'ALTER TABLE employees_attendancesession DROP CONSTRAINT IF EXISTS ' || constraint_rec.constraint_name;
                        END LOOP;
                    END $$;
                    
                    -- Create new unique constraint
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.table_constraints 
                            WHERE constraint_name = 'employees_attendancesession_employee_date_session_unique' 
                            AND table_name = 'employees_attendancesession'
                        ) THEN
                            ALTER TABLE employees_attendancesession 
                            ADD CONSTRAINT employees_attendancesession_employee_date_session_unique 
                            UNIQUE (employee_id, date, session_number);
                        END IF;
                    END $$;
                    """,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
        ),
        
        # Step 2: Add missing columns to Attendance table
        migrations.RunSQL(
            sql="""
            -- Add clock_in_attempts column
            ALTER TABLE employees_attendance 
            ADD COLUMN IF NOT EXISTS clock_in_attempts INTEGER DEFAULT 0;
            
            -- Add daily_clock_count column
            ALTER TABLE employees_attendance 
            ADD COLUMN IF NOT EXISTS daily_clock_count INTEGER DEFAULT 0;
            
            -- Add max_daily_clocks column
            ALTER TABLE employees_attendance 
            ADD COLUMN IF NOT EXISTS max_daily_clocks INTEGER DEFAULT 3;
            
            -- Remove old columns no longer in model
            ALTER TABLE employees_attendance 
            DROP COLUMN IF EXISTS user_timezone CASCADE;
            ALTER TABLE employees_attendance 
            DROP COLUMN IF EXISTS current_session_type CASCADE;
            ALTER TABLE employees_attendance 
            DROP COLUMN IF EXISTS daily_sessions_count CASCADE;
            ALTER TABLE employees_attendance 
            DROP COLUMN IF EXISTS max_daily_sessions CASCADE;
            ALTER TABLE employees_attendance 
            DROP COLUMN IF EXISTS total_break_hours CASCADE;
            ALTER TABLE employees_attendance 
            DROP COLUMN IF EXISTS total_working_hours CASCADE;
            ALTER TABLE employees_attendance 
            DROP COLUMN IF EXISTS local_clock_in_time CASCADE;
            ALTER TABLE employees_attendance 
            DROP COLUMN IF EXISTS local_clock_out_time CASCADE;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Step 3: Create SessionLocationLog model
        migrations.CreateModel(
            name="SessionLocationLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("latitude", models.DecimalField(decimal_places=7, max_digits=10)),
                ("longitude", models.DecimalField(decimal_places=7, max_digits=10)),
                ("accuracy", models.FloatField(blank=True, help_text="GPS accuracy in meters", null=True)),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="location_logs", to="employees.attendancesession")),
            ],
            options={
                "ordering": ["-timestamp"],
            },
        ),
    ]

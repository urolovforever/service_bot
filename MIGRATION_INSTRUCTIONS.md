# Database Migration Instructions

## Problem
The new registration form requires two additional fields in the `users` table:
- `phone_number` (VARCHAR(50))
- `location_id` (INTEGER, foreign key to locations.id)

## Solution Options

### Option 1: Run Python Migration Script (Recommended)
From your project directory, run:
```bash
python migration_add_user_fields.py
```

### Option 2: Run SQL Script Directly
If you have psql installed:
```bash
psql -h localhost -U marketplace_user -d marketplace_bot -f migration.sql
```

When prompted, enter the password: `secure_password_here`

### Option 3: Run SQL via Docker (if using Docker)
```bash
docker exec -i marketplace_postgres psql -U marketplace_user -d marketplace_bot < migration.sql
```

### Option 4: Manual SQL Commands
Connect to your database and run:
```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS location_id INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'users_location_id_fkey'
    ) THEN
        ALTER TABLE users ADD CONSTRAINT users_location_id_fkey
        FOREIGN KEY (location_id) REFERENCES locations(id);
    END IF;
END $$;
```

## After Migration
Once the migration is complete, restart your bot:
```bash
python main.py
```

The registration form will now properly collect:
- ✅ First name
- ✅ Last name
- ✅ Phone number
- ✅ Location

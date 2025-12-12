-- Migration script to add phone_number and location_id to users table

-- Add phone_number column
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR(50);

-- Add location_id column
ALTER TABLE users ADD COLUMN IF NOT EXISTS location_id INTEGER;

-- Add foreign key constraint (PostgreSQL will skip if exists)
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

#!/bin/bash
set -e

# Create the postgres superuser if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'postgres') THEN
            CREATE ROLE postgres WITH SUPERUSER CREATEDB CREATEROLE LOGIN PASSWORD 'postgres';
        END IF;
    END
    \$\$;
    
    -- Ensure isaahamed has full privileges
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
    
    -- Create necessary extensions if needed
    -- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOSQL

echo "Database initialization complete!"
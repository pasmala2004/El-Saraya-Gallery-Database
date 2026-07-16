-- ============================================================================
-- Database Migration Verification Script
-- ============================================================================
-- Run this script after applying the migration to verify all tables,
-- constraints, indexes, and types are created correctly.
--
-- Usage:
--   psql -U erp_user -d erp_db -f verify_migration.sql
-- ============================================================================

\echo '==================================================================='
\echo 'DATABASE MIGRATION VERIFICATION'
\echo '==================================================================='
\echo ''

-- ============================================================================
-- 1. Check Alembic Version Table
-- ============================================================================
\echo '1. Alembic Version'
\echo '-------------------------------------------------------------------'
SELECT version_num, CAST(created AS VARCHAR) as applied_at 
FROM alembic_version;
\echo ''

-- ============================================================================
-- 2. Verify All Tables Exist (Expected: 11 tables + alembic_version)
-- ============================================================================
\echo '2. Tables'
\echo '-------------------------------------------------------------------'
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns 
     WHERE table_schema = 'public' AND table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE'
ORDER BY table_name;
\echo ''
\echo 'Expected: 12 tables (11 application + alembic_version)'
\echo ''

-- ============================================================================
-- 3. Verify Enum Types (Expected: 5 enums)
-- ============================================================================
\echo '3. Enum Types'
\echo '-------------------------------------------------------------------'
SELECT 
    t.typname as enum_name,
    string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder) as values
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid  
WHERE t.typtype = 'e'
GROUP BY t.typname
ORDER BY t.typname;
\echo ''
\echo 'Expected: 5 enums'
\echo ''

-- ============================================================================
-- 4. Verify Primary Keys (Expected: 11 PKs)
-- ============================================================================
\echo '4. Primary Keys'
\echo '-------------------------------------------------------------------'
SELECT
    tc.table_name,
    kcu.column_name as pk_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
  ON tc.constraint_name = kcu.constraint_name
WHERE tc.constraint_type = 'PRIMARY KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name;
\echo ''
\echo 'Expected: 11 primary keys (all named "id")'
\echo ''

-- ============================================================================
-- 5. Verify Foreign Keys with CASCADE Rules (Expected: 13 FKs)
-- ============================================================================
\echo '5. Foreign Keys'
\echo '-------------------------------------------------------------------'
SELECT
    tc.table_name as from_table,
    kcu.column_name as from_column,
    ccu.table_name AS to_table,
    ccu.column_name AS to_column,
    rc.delete_rule as on_delete
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
  ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.column_name;
\echo ''
\echo 'Expected: 13 foreign keys'
\echo '  - 8 with CASCADE delete rule'
\echo '  - 5 with RESTRICT delete rule'
\echo ''

-- ============================================================================
-- 6. Verify Indexes (Expected: 14 indexes + 11 PKs)
-- ============================================================================
\echo '6. Indexes'
\echo '-------------------------------------------------------------------'
SELECT
    schemaname,
    tablename,
    indexname,
    CASE 
        WHEN indexname LIKE '%_pkey' THEN 'PRIMARY KEY'
        WHEN indexdef LIKE '%UNIQUE%' THEN 'UNIQUE INDEX'
        ELSE 'INDEX'
    END as index_type
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
\echo ''
\echo 'Expected: 25 indexes total (11 PKs + 14 indexes)'
\echo ''

-- ============================================================================
-- 7. Verify Unique Constraints (Expected: 3)
-- ============================================================================
\echo '7. Unique Constraints'
\echo '-------------------------------------------------------------------'
SELECT
    tc.table_name,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
  ON tc.constraint_name = kcu.constraint_name
WHERE tc.constraint_type = 'UNIQUE'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.column_name;
\echo ''
\echo 'Expected: 3 unique constraints'
\echo '  - product_categories.name'
\echo '  - quotations.quotation_number'
\echo '  - jobs.quotation_id'
\echo ''

-- ============================================================================
-- 8. Verify Column Defaults (UUID generation and timestamps)
-- ============================================================================
\echo '8. Column Defaults'
\echo '-------------------------------------------------------------------'
SELECT 
    table_name,
    column_name,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND column_default IS NOT NULL
  AND table_name != 'alembic_version'
ORDER BY table_name, column_name;
\echo ''
\echo 'Expected: All id columns use gen_random_uuid()'
\echo 'Expected: All created_at/updated_at use now()'
\echo ''

-- ============================================================================
-- 9. Verify Nullable Columns
-- ============================================================================
\echo '9. NOT NULL Constraints Summary'
\echo '-------------------------------------------------------------------'
SELECT 
    table_name,
    COUNT(*) FILTER (WHERE is_nullable = 'NO') as not_null_count,
    COUNT(*) FILTER (WHERE is_nullable = 'YES') as nullable_count,
    COUNT(*) as total_columns
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name != 'alembic_version'
GROUP BY table_name
ORDER BY table_name;
\echo ''

-- ============================================================================
-- 10. Verify Data Types (Check for UUID, timestamps, enums)
-- ============================================================================
\echo '10. Column Data Types Summary'
\echo '-------------------------------------------------------------------'
SELECT 
    data_type,
    COUNT(*) as column_count
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name != 'alembic_version'
GROUP BY data_type
ORDER BY column_count DESC;
\echo ''
\echo 'Expected types: USER-DEFINED (enums), uuid, text, character varying,'
\echo '                timestamp with time zone, date, numeric, smallint, boolean'
\echo ''

-- ============================================================================
-- 11. Table-by-Table Column Verification
-- ============================================================================
\echo '11. Detailed Column Information'
\echo '-------------------------------------------------------------------'
\echo ''

\echo 'customers (10 columns expected):'
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'customers' AND table_schema = 'public'
ORDER BY ordinal_position;
\echo ''

\echo 'product_categories (4 columns expected):'
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'product_categories' AND table_schema = 'public'
ORDER BY ordinal_position;
\echo ''

\echo 'products (6 columns expected):'
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'products' AND table_schema = 'public'
ORDER BY ordinal_position;
\echo ''

\echo 'quotations (11 columns expected):'
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'quotations' AND table_schema = 'public'
ORDER BY ordinal_position;
\echo ''

\echo 'quotation_items (10 columns expected):'
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'quotation_items' AND table_schema = 'public'
ORDER BY ordinal_position;
\echo ''

\echo 'jobs (12 columns expected):'
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'jobs' AND table_schema = 'public'
ORDER BY ordinal_position;
\echo ''

\echo 'measurements (8 columns expected):'
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'measurements' AND table_schema = 'public'
ORDER BY ordinal_position;
\echo ''

\echo 'measurement_items (11 columns expected):'
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'measurement_items' AND table_schema = 'public'
ORDER BY ordinal_position;
\echo ''

\echo 'payments (13 columns expected):'
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'payments' AND table_schema = 'public'
ORDER BY ordinal_position;
\echo ''

\echo 'activity_logs (6 columns expected):'
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'activity_logs' AND table_schema = 'public'
ORDER BY ordinal_position;
\echo ''

\echo 'reports (7 columns expected):'
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'reports' AND table_schema = 'public'
ORDER BY ordinal_position;
\echo ''

-- ============================================================================
-- 12. Final Summary
-- ============================================================================
\echo '==================================================================='
\echo 'VERIFICATION SUMMARY'
\echo '==================================================================='
\echo ''
\echo 'If all sections show expected counts and no errors, the migration'
\echo 'has been applied successfully.'
\echo ''
\echo 'Expected counts:'
\echo '  - Tables: 12 (11 application + alembic_version)'
\echo '  - Enum types: 5'
\echo '  - Primary keys: 11'
\echo '  - Foreign keys: 13'
\echo '  - Indexes: 25 (11 PKs + 14 indexes)'
\echo '  - Unique constraints: 3'
\echo ''
\echo '==================================================================='

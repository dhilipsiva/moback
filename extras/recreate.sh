export PGPASSWORD='admin_pass'
psql -d postgres -f user.sql
psql -d postgres -c "DROP DATABASE moback;"
psql -d postgres -c "CREATE DATABASE moback WITH owner=foo"

export PGPASSWORD='bar'
psql -U foo -d moback -f schema.sql

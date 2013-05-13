psql -U postgres -d postgres -f user.sql
psql -U postgres -d postgres -c "DROP DATABASE moback;"
psql -U postgres -d postgres -c "CREATE DATABASE moback WITH owner=foo ENCODING='utf-8';"
psql -U foo -d moback -f schema.sql

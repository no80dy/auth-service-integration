cat ./ddl/movies_database.sql | psql -U app -d movies_database
psql -U app -d movies_database SET search_path = public, content;
#!/usr/bin/bash

ENV_FILE="./movies_admin/config/.env"

if [ ! -f "$ENV_FILE" ]; then
	echo "File .env not found!"
	exit 1
fi

while IFS= read -r line; do
	export "$line"
done < "$ENV_FILE"

echo "DB_NAME: $DB_NAME"
echo "DB_USER: $DB_USER"
echo "DB_PASSWORD: $DB_PASSWORD"
echo "DB_HOST: $DB_HOST"
echo "DB_PORT: $DB_PORT"

psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f ./schema_design/movies_database.ddl

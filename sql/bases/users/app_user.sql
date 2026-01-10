create user ${POSTGRES_APP_USER} with 
    password '${POSTGRES_APP_PASSWORD}'
    nocreatedb
    nocreaterole;

grant connect on database ${POSTGRES_DB} to ${POSTGRES_APP_USER};

grant usage on schema ${POSTGRES_SCHEMA} to ${POSTGRES_APP_USER};

alter default privileges in schema ${POSTGRES_SCHEMA} grant
    select, insert, update, delete on tables to ${POSTGRES_APP_USER};

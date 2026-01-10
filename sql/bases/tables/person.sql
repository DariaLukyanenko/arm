create table if not exists PERSON (
    ID serial primary key,
    EXTERNAL_ID varchar(255) unique not null,
    STATUS varchar(50) default 'active' not null,
    DATETIME_CREATED timestamp default CURRENT_TIMESTAMP
);

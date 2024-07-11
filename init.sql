CREATE TABLE users (
    telegram_id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    surname VARCHAR(255),
    username VARCHAR(255)
);

CREATE TABLE documents (
    document_id SERIAL PRIMARY KEY,
    file_id VARCHAR(255) NOT NULL,
    caption VARCHAR(255),
    status BOOLEAN DEFAULT TRUE
);
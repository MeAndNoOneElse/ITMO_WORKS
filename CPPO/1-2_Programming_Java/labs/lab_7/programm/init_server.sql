CREATE TABLE IF NOT EXISTS users
(
    id       SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    permissions VARCHAR(50) NOT NULL CHECK (permissions IN ('USER', 'ADMIN', 'MODERATOR', 'ABOBA')) DEFAULT 'USER'
    );

CREATE TABLE IF NOT EXISTS coordinates
(
    id SERIAL PRIMARY KEY,
    x  DOUBLE PRECISION CHECK (x > -980),
    y  FLOAT CHECK (y <= 295) NOT NULL
    );
CREATE TABLE IF NOT EXISTS event
(
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(255) NOT NULL,
    time VARCHAR(255)
    );
CREATE TABLE IF NOT EXISTS type
(
    id         SERIAL PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL UNIQUE
    );
INSERT INTO type (type_name)
VALUES ('VIP'),
       ('USUAL'),
       ('CHEAP'),
       ('BUDGETARY');
CREATE TABLE IF NOT EXISTS tickets
(
    id                     SERIAL PRIMARY KEY,
    name                   VARCHAR(255)                        NOT NULL CHECK (name <> ''),
    coordinates_id         INT                                 NOT NULL,
    FOREIGN KEY (coordinates_id) REFERENCES coordinates (id) ON DELETE CASCADE,
    creation_date          TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    price INT CHECK (price > 0),
    description            TEXT                                NOT NULL,
    type_id               INT                                 NOT NULL,
    FOREIGN KEY (type_id) REFERENCES TicketType (id),
    event_id              INT                                 NOT NULL,
    FOREIGN KEY (event_id) REFERENCES event (id) ON DELETE CASCADE,
    user_id                INT                                 NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
    );

CREATE OR REPLACE FUNCTION delete_related_records()
    RETURNS TRIGGER AS $$
BEGIN
DELETE FROM coordinates WHERE id = OLD.coordinates_id;
DELETE FROM event WHERE id = OLD.event_id;
RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_music_bands_delete
    AFTER DELETE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION delete_related_records();

SELECT tickets.id            AS id,
       tickets.name          AS ticket_name,
       coordinates.x         AS coordinates_x,
       coordinates.y         AS coordinates_y,
       tickets.creation_date AS creation_date,
       tickets.price         AS price,
       tickets.description   AS description,
       TicketType.type_name  AS type_name,
       event.name            AS event_name,
       event.time            AS event_time,
       users.username        AS username
FROM tickets
         JOIN coordinates ON tickets.coordinates_id = coordinates.id
         JOIN event ON tickets.event_id = event.id
         JOIN TicketType ON tickets.type_id = TicketType.id
         JOIN users ON tickets.user_id = users.id
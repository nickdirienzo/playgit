DROP TABLE IF EXISTS songs CASCADE;
CREATE TABLE songs (
  id VARCHAR(100) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  album VARCHAR(100),
  artist VARCHAR(100),
  artwork_url VARCHAR(100),
  year INTEGER,
  genre VARCHAR(100)
);

DROP TABLE IF EXISTS playlists CASCADE;
CREATE SEQUENCE playlist_id_seq;
CREATE TABLE playlists (
  id INTEGER PRIMARY KEY DEFAULT nextval('playlist_id_seq'),
  uid INTEGER NOT NULL REFERENCES users (id),
  name VARCHAR(100),
  parent INTEGER REFERENCES playlists (id),
  create_date TIMESTAMP DEFAULT now(),
  path VARCHAR(100)
);

DROP TABLE IF EXISTS users CASCADE;
CREATE SEQUENCE user_id_seq;
CREATE TABLE users (
  id INTEGER PRIMARY KEY DEFAULT nextval('user_id_seq'),
  username VARCHAR(100) UNIQUE,
  password VARCHAR(100)
);

DROP TABLE IF EXISTS activities CASCADE;
CREATE SEQUENCE activity_id_seq;
CREATE TABLE activities (
    id INTEGER PRIMARY KEY DEFAULT nextval('activity_id_seq'),
    uid INTEGER NOT NULL REFERENCES users (id),
    activity_date TIMESTAMP DEFAULT now(),
    description VARCHAR(255)
);

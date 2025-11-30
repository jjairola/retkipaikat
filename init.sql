
INSERT OR IGNORE INTO users (username, password_hash) VALUES
('admin', 'hash');

INSERT INTO classes (title, value) VALUES ('Tyyppi', 'Lintutorni');
INSERT INTO classes (title, value) VALUES ('Tyyppi', 'Laavu');
INSERT INTO classes (title, value) VALUES ('Tyyppi', 'Kota');
INSERT INTO classes (title, value) VALUES ('Tyyppi', 'Tulentekopaikka');
INSERT INTO classes (title, value) VALUES ('Tyyppi', 'Näköalapaikka');
INSERT INTO classes (title, value) VALUES ('Tyyppi', 'Retkeilyreitti');
INSERT INTO classes (title, value) VALUES ('Tyyppi', 'Luontopolku');

INSERT INTO classes (title, value) VALUES ('Vaikeusaste', 'Helppo');
INSERT INTO classes (title, value) VALUES ('Vaikeusaste', 'Keskitaso');
INSERT INTO classes (title, value) VALUES ('Vaikeusaste', 'Vaativa');

INSERT OR IGNORE INTO destinations (name, description, municipality, user_id) VALUES
('Maarin lintutorni', 'Laajalahden luonnonsuojelualue on pääkaupunkiseudun parhaita lintuvesiä. Se on erinomainen lintujen tarkkailupaikka niin muuttoaikoina kuin muulloinkin. Lintutorneista ja poluilta voi tarkkailla alueen luontoa sitä häiritsemättä.', 'Espoo', 1);


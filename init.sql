
INSERT OR IGNORE INTO users (username, password_hash) VALUES
('admin', 'hash');

INSERT OR IGNORE INTO destinations (name, description, municipality, user_id) VALUES
('Maarin lintutorni', 'Laajalahden luonnonsuojelualue on pääkaupunkiseudun parhaita lintuvesiä. Se on erinomainen lintujen tarkkailupaikka niin muuttoaikoina kuin muulloinkin. Lintutorneista ja poluilta voi tarkkailla alueen luontoa sitä häiritsemättä.', 'Espoo', 1);

INSERT OR IGNORE INTO classifications (name) VALUES
('Lintutorni'),
('Laavu'),
('Kota'),
('Lapsiystävällinen'),
('Tulentekopaikka'),
('Esteetön');

INSERT OR IGNORE INTO destination_classifications (destination_id, classification_id) VALUES
(1, 1);
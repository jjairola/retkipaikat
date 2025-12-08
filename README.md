# Retkipaikat

Sovelluksessa käyttäjät pystyvät jakamaan retkipaikkojaan. Retkipaikassa lukee nimi, kuvaus ja kunta.

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään retkipaikkoja ja muokkaamaan ja poistamaan niitä.
- Käyttäjä näkee sovellukseen lisätyt retkipaikat.
- Käyttäjä pystyy etsimään retkipaikkoja hakusanalla.
- Käyttäjäsivu näyttää, montako retkipaikkaa käyttäjä on lisännyt ja listan käyttäjän lisäämistä retkipaikoista.
- Käyttäjä pystyy valitsemaan retkipaikalla yhden tai useamman luokittelun (esim. laavu, kota, lapsiystävällinen, tulentekopaikka, esteetön).
- Käyttäjä pystyy antamaan retkipaikalle kommentin ja arvosanan. Retkipaikasta näytetään kommentit ja keskimääräinen arvosana.

Tässä pääasiallinen tietokohde on retkipaikka ja toissijainen tietokohde on kommentti retkipaikkaan.

## Sovelluksen asennus

### Python venv

Ohelman vaatimukset on tallennettu requirements.txt tiedostoon, joka toimii seuraavasti venv kanssa.

Asennus:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Tiedokannan alustus:

```
sqlite3 database.db < schema.sql
sqlite3 database.db < init.sql
```

Käynnistä ohjelma:

```
$ cd src
$ flask run
```





## Suuren tietomäärän käsittely

Sovellus on testattu suurella tietomäärällä. Sovellusta voi testata suurella tietomäärällä käyttämällä ```seed.py``` tiedostoa, joka luo suuren määrän testidataa.

### Retkikohteiden sivuutus etusivulla

Retkikohteiden lajittelu etusivulla niiden saaman arvostelun perusteella osoittautui raskaaksi operaatioksi, jos kommenttien muodostama arvosana lasketaan jokaisella etusivun kyselyllä kaikista kommenteista. Tämän takia retkikohteen saama arvosana talletaan destinations -tauluun average_rating kenttään, ja kenttä päivitetään kommentin lisäyksen, muuttamisen ja poistamisen yhteydessä. Ohjelmassa päädyttiin toteuttamaan keskiarvon laskenta retkikohteelle koodissa tietokanta -triggerin sijaan, jotta ratkaisu on yksinkertainen. Keskiarvolle myös lisättiin indeksi.

Etusivulla käytetyt indeksit ja niiden käyttötarkoitukset:

1. ```CREATE INDEX idx_destinations_average_rating ON destinations(average_rating DESC);``` - Käytetään rekikohteiden järjestämiseen retkikohteiden saaman arvosanan mukaan.

2. ```CREATE INDEX idx_destination_classes_destination_id ON destination_classes(destination_id);``` - Retkikohteiden kyselyyn liitetään aina retkikohteen luokittelut. Oletuksena destionation_classes(destination_id) ei ole indeksoitu, mikä ei ole tehokasta useampien rekitkohteiden näyttämisessä listaussivulla.

3. ```CREATE INDEX idx_comments_destination ON comments(destination_id);``` - Retkikohteiden kyselyyn liitetään aina retkikohteen kommentit. Oletuksena comments(destination_id) ei ole indeksoitu, mikä ei ole tehokasta useampien rekitkohteiden näyttämisessä listaussivulla.

### Hakusivu


Hakusivulla lasketaan jokaiselle luokitukselle (classes) niiden nykyinen määrä (destination_classes taulussa). Tätä varten on lisätty indeksi, joka nopeuttaa luokituksien määrän laskentaa.

Hakusivulla käytetyt indeksit ja käyttötarkoitukset:

1.  ```CREATE INDEX idx_classes_title_value ON destination_classes(title, value);``` - Retkikohteiden hakusivulla lasketaan jokaiselle luokittelulle niiden määrä tietokannassa. Indeksi tarvitaan, että voidaan laskea jokaiselle luokittelulle (title, value) tehokkaasti osumien määrä tietokannassa.

### Tietokannan alustus testausta varten

```
# Luo testidata
python3 seed.py

Testidata luo:
* käyttäjiä:  50000
* retkikohteita: 100000
* kommentteja: 1000000

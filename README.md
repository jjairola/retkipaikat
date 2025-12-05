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

### Python env

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

Sovelllus toimii suurella tietomäärällä. Raskain tietokantakysely suurella tietomäärällä on etusivun retkikohteiden lajittelu retkikohteiden saamien arvosanojen perusteella, koska lajittelua varten tarvitaan komenttien retkikohteelle muodostama arvosana.

Etusivun arvosteluperusteinen järjestys on toteutettu erillisellä ```ratings_cache``` taululla, johon talletetaan jokaisen retkikohteen saama arvosana retkikohteen päivityksen yhteydessä. Ratings_cache:n päivityks valittiin toteutettavaksi koodissa tietokanta-triggerin sijaan, koska koska harjoitustyö haluttiin pitää hyvin yksinkertaisena.

Seuraavat indeksit on luotu ja niiden käyttötarkoitus:

1. ```CREATE INDEX idx_ratings_cache_avgerage ON ratings_cache(average_rating DESC);``` - Käytetään rekikohteiden järjestämiseen retkikohteiden saaman arvosanan mukaan. Etusivulla näytettyvät destionations (retkikohteet):lle tehdään right join ratings_cache taulun kanssa. Näin voidaan tehdä limitys suoraan valmiiden keskiarvojen mukaan, eikä keskiarvoja tarvitse laskea erikseen kommenteista. Ilman ratings_cache taulua, joudutaan laskemaan kaikkien kommenttien keskiarvo muodostamat arvosanat jokaiselle retkikohteelle, joka on erityisen raskas kysely.

2.  ```CREATE INDEX idx_classes_title_value ON destination_classes(title, value);``` - Retkikohteiden hakusivulla lasketaan jokaiselle luokittelulle niiden määrä tietokannassa. Indeksi tarvitaan, että voidaan laskea jokaiselle luokittelulle (title, value) tehokkaasti osumien määrä tietokannassa.

3. ```CREATE INDEX idx_destination_classes_destination_id ON destination_classes(destination_id);``` - Retkikohteiden kyselyyn liitetään aina retkikohteen luokittelut. Oletuksena destionation_classes(destination_id) ei ole indeksoitu, mikä ei ole tehokasta useampien rekitkohteiden näyttämisessä listaussivulla.

4. ```CREATE INDEX idx_comments_destination ON comments(destination_id);``` - Retkikohteiden kyselyyn liitetään aina retkikohteen kommentit. Oletuksena comments(destination_id) ei ole indeksoitu, mikä ei ole tehokasta useampien rekitkohteiden näyttämisessä listaussivulla.


### Tietokannan alustus testausta varten

```
# Luo testidata
python3 seed.py

# Päivitä arvostelujen välimuisti joka tarvitaan etusivun lajittelun arvostelujen mukaan
python3 ratings_cache.py
```

Testidata luo:
* käyttäjiä:  50000
* retkikohteita: 100000
* kommentteja: 1000000

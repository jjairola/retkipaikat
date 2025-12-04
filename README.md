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


###

Tietokannan alustus testausta varten:

```
# Luo testidata
python3 seed.py

# Päivitä arvostelujen välimuisti joka tarvitaan etusivun lajittelun arvostelujen mukaan
python3 ratings_cache.py
```
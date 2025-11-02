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

## Ohjelman suoritus

Ohjeet (Mac/Linux):

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd src
flash run
```
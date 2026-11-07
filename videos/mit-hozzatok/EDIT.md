# „Mit hozzatok magatokkal a fotózásra?” – v2 újravágás

**Forrás:** Drive, „Miket hozzatok?” mappa (Kitti fiókja)

- nyers felvétel: `VID_20261107_154444.mp4` (95,1 mp, egy felvétel)
- 8 fotó
- zene: `cheerful-joyful-playful` (Pixabay)
- logó: `logo-sarga.png`
- az előző vágás: `Mosolymuvesz_reels_mit_hozzatok.mp4`

**Kimenet:** `renders/Mosolymuvesz_reels_mit_hozzatok_v2.mp4`, 1080×1920, 30 fps, 75,6 mp

## Mi változott az első vágáshoz képest

| | v1 | v2 |
|---|---|---|
| Hossz | 95 mp | 75,6 mp (72,9 mp beszéd + 2,7 mp záró kártya) |
| Horog | kicsi felirat, a mellkas magasságában | nagy cím Kitti arca alatt, fölötte az „5 tipp a fotózásra” címke, már a 0. képkockán |
| Felirat helye | alul, a mikrofonon és a Reels gombjai alatt (1640 px körül) | a mikrofon fölött, a Reels biztonságos sávjában (alja 1280 px-nél), halvány sötét háttérrel; a kulcsszavak sárgák |
| Záró rész | csak a „mosolymuvesz.hu” felirat | záró kártya a cicás logóval: „Szabad karácsonyi időpontok – Link az első kommentben – mosolymuvesz.hu” |
| Szín | hideg, szürkés | meleg korrekció Kitti felvételén |
| Vágások | – | a vágásoknál váltakozó közelítés vagy fotó, hogy ne ugorjon a kép |

## Kivágott részek (nyers idő)

| Idő | Szöveg | Miért |
|---|---|---|
| 3,54–8,23 | „Sokan szoktátok tőlem kérdezni egy-egy foglalás után.” | a kérdés maga a horog, ez csak felvezetés |
| 25,42–29,27 | „és a kezdeti megszeppenést egy kicsit segítse ez a helyzet.” | nyelvtanilag döcögős, és ugyanazt ismétli |
| 42,33–45,45 | „Ehhez lehetnek ilyen kiegészítő eszközök,” | Kitti utána újrakezdi („kiegészítő kellékek…”) |
| egyéb | 0,45 mp-nél hosszabb szünetek | kb. 0,2 mp-re rövidítve |

A megtartott szakaszok listája a `scripts/prepare.sh` és a `scripts/build.py` fájlban van (`SEGS`). Ha egy kivágott mondatot vissza szeretnétek tenni, ott kell átírni, aztán mindkét szkriptet újra kell futtatni.

## Feliratok

A szöveg az első vágás feliratából származik, amit a hangfelvétel alapján írtak. Az időzítést a hangsáv szüneteihez igazítottam: ebben a munkamenetben nem volt elérhető beszédfelismerő, ezért szó szintű időbélyegek nincsenek. Két hely ellenőrzendő:

- „kis **nyunyókája**”: biztosan így hangzik el?
- a „hogy a gyermek egy kicsit feloldódjon az új helyzetben” végére vessző helyett pont került, mert a mondat folytatását kivágtuk.

## Újraépítés

```bash
scripts/prepare.sh <letöltött forrásmappa>   # assets/: vágott beszéd, fotók, hátterek, logó, zene
python3 scripts/build.py                      # index.html + compositions/*
npx hyperframes check
npx hyperframes render -o renders/Mosolymuvesz_reels_mit_hozzatok_v2.mp4
```

## Közzététel előtt

- Csak a **ruhás videó után** mehet ki, mert Kitti ezt mondja benne: „már megbeszéltük a ruhákat”.
- **Borítókép:** a 0. képkockán Kitti épp pislog, ezért feltöltéskor válasszatok külön borítót, például az 1,2 mp-nél lévő képkockát.
- A link az első kommentbe kerül: `https://mosolymuvesz.hu/karacsony/?utm_source=facebook&utm_medium=social&utm_campaign=karacsony2026&utm_content=mit_hozzatok_v2`

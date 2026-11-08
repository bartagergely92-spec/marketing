# „Mit vegyetek fel a karácsonyi fotózásra?” – organikus Reels

**Alap:** a blogcikk – https://mosolymuvesz.hu/tippek/mit-vegyunk-fel-a-karacsonyi-fotozasra/

**Forrás:** Drive, „Mit vegyetek fel?” mappa (Kitti fiókja, 2026. nov. 8.)

- 9 felvétel: `VID_20261108_102154 … 104611`, összesen kb. 3 perc 10 mp
- 33 fotó
- zene: `maksymmalko-cheerful-joyful-playful-music-399359.mp3` (Pixabay)

**Kimenet:** `renders/Mosolymuvesz_reels_mit_vegyetek_fel_final.mp4`, 1080×1920, 30 fps, kb. 100 mp (97 mp beszéd + 3 mp záró kártya)

## Felépítés

| # | Fejezet | Ami elhangzik (rövidítve) | Kép |
|---|---|---|---|
| – | Horog | „Mindjárt itt a fotózás, és nem tudjátok, hogy miben öltözzetek? Gyertek, és segítek!” | nagy cím: „Mit vegyetek fel a karácsonyi fotózásra?” + „6 ruhatipp óvónénitől” |
| 1 | Kényelem | kényelmes ruha; ha szúr, oda a hangulat | KEP01027 |
| 2 | Színharmónia | 2–3 harmonizáló szín, cserélgetve a családtagok között | KEP07399-Edit, majd **színpaletta-kártya** a blog színeivel |
| 3 | Minták: a kevesebb több | Disney-s, Mancs őrjáratos minták helyett bársony, kötött anyag | KEP07575-Edit, KEP02177_1 |
| 4 | Rétegek | kalap, mellény, kardigán | KEP01860_1 |
| 5 | Átmeneti tárgy | „igazi mentőmellények egy fotózáson” | 7.jpg |
| 6 | Nyugalom | „A legszebb ruha sem pótolja a nyugalmat. Nálam nem kell pózolni…” + „Játékos feladatokkal…” | KEP09578, KEP09606, KEP06552-Recovered |
| – | Zárás | „A videó alatt küldöm a részletes tájékoztatót az öltözködésről, illetve egy összeállítást.” | záró kártya: „Részletes ruhatippek és színpaletta – Link az első kommentben” |

## Kimaradt (a nyers felvételen megvan, vissza lehet tenni)

- **Kényelem:** „Ez főleg a gyerekeknél fontos, de nálunk felnőtteknél is kiemelkedő szempont. Hiszen hogyha jól érezzük magunkat a ruhában… az látszik a fotókon is.”
- **Színek:** a felsorolás kimondva („Mondok pár példát… pasztellkék”). Helyette a színpaletta-kártya mutatja.
- **Minták:** „Kerüljétek a nagy feliratokat, mindenféle ilyen nagy mintázatokat”, „akár egy apró pöttyös ruha vagy egy finom kockás ing”.
- **Rétegek:** „Praktikus és egyben jól mutat a képeken”, „hiszen hogyha a gyermek szaladgál, kimelegszik…”.
- **Átmeneti tárgy:** „hiszen a kezdeti bizalmatlanságot segítheti… ebben az új helyzetben.” Ez a tegnapi videóban már szerepelt.
- **Nyugalom:** „Hogyha esetleg elcsúsztok az idővel, vagy lecsöppen a ruhára valami, ne aggódjatok.”

## Feliratok

A feliratok szó szintű beszédfelismeréssel (whisper medium, magyar) készültek, kézzel javítva. Javított szavak:

| Felismert | Javítva |
|---|---|
| összevállogattok | összeválogattok |
| cserégetitek | cserélgetitek |
| disznis | Disney-s |
| mancsőrjáratos | Mancs őrjáratos |
| ovodás | óvodás |
| kardigan | kardigán |
| mentő mellények | mentőmellények |
| videmsággal | vidámsággal |
| mosajok | mosolyok |
| küld a mai … tájékoztadót | küldöm a … tájékoztatót |

A „4.” és a „6.” sorszámot kiírva szerepeltetjük („Negyedik”, „Hatodik”).

## Újraépítés

```bash
scripts/prepare.sh <letöltött forrásmappa>   # a work/edit.json alapján vág (előtte: python3 scripts/plan.py)
python3 scripts/build.py
npx hyperframes check
npx hyperframes render -o renders/Mosolymuvesz_reels_mit_vegyetek_fel.mp4
```

A `work/` mappába kerülnek a felvételek hangsávjai (`<felvétel>.wav`) és az átiratok (`<felvétel>.json`). A `scripts/plan.py` innen olvassa a szóidőket.

## Közzététel

- A link az első kommentbe kerüljön:
  `https://mosolymuvesz.hu/tippek/mit-vegyunk-fel-a-karacsonyi-fotozasra/?utm_source=facebook&utm_medium=social&utm_campaign=karacsony2026&utm_content=mit_vegyetek_fel`
- Ha Kitti a Pinterest-táblát is linkeli („egy összeállítást”), az mehet ugyanabba a kommentbe.

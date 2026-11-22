# fuzzy-waffle-bohu · HOUSE / Study

Interaktivní 3D model bytového domu s opakovanou dispozicí jednoho vzorového bytu ve všech 11 podlažích. Okna a dveřní otvory jsou skutečně otevřené skrz obvodové stěny a doplněné o ostění v hloubce původních stěnových panelů.

**Demo:** https://akcizur.github.io/fuzzy-waffle-bohu/

## Co je v repozitáři

- `house.obj` – model domu, 11 bytových modulů, skutečné otvory a ostění
- `house.txt` – synchronizovaná textová kopie modelu
- `house.mtl` – materiálová knihovna včetně materiálu ostění
- `index.html` – samostatný interaktivní 3D prohlížeč
- `tools/repeat_apartment_column.py` – reprodukovatelný generátor bytového sloupce
- `tools/add_opening_reveals.py` – reprodukovatelné doplnění ostění otvorů
- `tools/remove_duplicate_shell_faces.py` – kontrola překryvů bytů s pláštěm
- `tools/validate_openings.py` – ray-test průchodnosti všech 22 otvorů
- `.github/workflows/pages.yml` – automatické nasazení na GitHub Pages

## Bytový sloupec

V původním modelu bylo kompletní vnitřní členění nalezeno na šestém podlaží. Z této předlohy bylo vybráno 357 jedinečných polygonů; po odečtení dvou původních výplní otvorů zůstává 355 kandidátních ploch pro každé podlaží.

Při kontrole napojení na plášť se ukázalo, že část těchto polygonů už existuje v původní geometrii domu. Kdyby se kopírovaly také, vznikaly by téměř totožné koplanární plochy, které mohou v prohlížeči způsobovat z-fighting. Proto se z bytových kopií odstranilo 130 ploch, jejichž plochu už z více než 99 % pokrývá stejný materiál a stejně orientovaná plocha původního pláště. Původní plochy zůstávají zachované v plášti, nejde tedy o ztrátu geometrie.

Výsledné moduly apartment_column_floor_01 až apartment_column_floor_11 obsahují pouze geometrii, která není už reprezentována pláštěm. Jejich rozdílný počet ploch je záměrný a odpovídá ověřenému překryvu s původní konstrukcí:

| Podlaží | Plochy v modulu | Plochy ponechané pouze v plášti |
| ---: | ---: | ---: |
| 1 | 350 | 5 |
| 2 | 352 | 3 |
| 3 | 351 | 4 |
| 4 | 341 | 14 |
| 5 | 321 | 34 |
| 6 | 355 | 0 |
| 7 | 343 | 12 |
| 8 | 342 | 13 |
| 9 | 340 | 15 |
| 10 | 332 | 23 |
| 11 | 346 | 9 |

Generátor bytového sloupce zachovává půdorysnou polohu a původní rozvržení. Výška Y je přizpůsobena skutečné konstrukční výšce daného podlaží. Koplanární překryvy lze znovu zkontrolovat příkazem python tools/remove_duplicate_shell_faces.py --check.

## Skutečné otvory oken a dveří

Ze zdrojového modelu bylo odstraněno 22 skleněných / plných výplňových polygonů, tedy dvě výplně na každé podlaží. Odpovídající plochy vnější stěny byly geometricky rozříznuty podle jejich skutečných obrysů. Vzniklo 22 průchozích otvorů: jedno okenní pole a jeden vysoký dveřní otvor na každý byt.

Otvory nejsou jen tmavé textury: původní plocha skla a odpovídající části stěn byly odstraněny z geometrie. Průchodnost byla kontrolována vzorkovací mřížkou přes plochu všech 22 otvorů; po celé ploše nebyla nalezena žádná zbývající stěnová nebo skleněná plocha.

V každém podlaží jsou také zachovány dva původní vnitřní dveřní průchody. Ty byly otevřené už ve zdrojové geometrii a nebyly znovu vyřezávány.

Automatický test průchodnosti vzorkuje vnitřek všech 22 vnějších otvorů paprsky skrz jejich změřenou hloubku. Kontroluje 2 926 bodů a ověřuje, že uvnitř otvorů nezůstala žádná protínající stěnová ani skleněná plocha. Test zahrnuje i dveře v 11. podlaží, přestože u nich chybí odpovídající vnější plocha pláště.

## Ostění a hloubka stěn

U 21 otvorů bylo zkontrolováno všech 84 bočních hran ostění. Šest ploch už bylo součástí původní geometrie (okno v 5. a 6. podlaží a dveře v 6. podlaží), proto byly ponechány a znovu se negenerují. Doplněno bylo pouze zbývajících 78 chybějících ploch. Hloubka každého nového ostění je odvozena ze vzdálenosti mezi původní rovinou vnějšího stěnového panelu a rovinou odstraněné okenní / dveřní výplně, nikoli z jedné odhadnuté konstanty. Naměřené hloubky se v původních modelových jednotkách pohybují přibližně od 0.3306 do 1.0968.

U dveřního otvoru v nejvyšším podlaží nebyla v původním modelu nalezena odpovídající protilehlá stěnová plocha. Otvor proto zůstává průchozí a ostění se tam uměle nedoplňovalo.

Výsledné ostění má 84 bočních ploch celkem: 6 zachovaných původních a 78 nových čtyřúhelníkových ploch v samostatných objektech podle podlaží. Materiál `OpeningReveal` je samostatný a lze ho dále upravovat v 3D editoru. Generátor před vytvořením ploch porovnává jejich obrysy s existující geometrií, aby stejné boky nepřidával podruhé.


## Porovnání bytů s původním modelem

Automatický regresní test načítá původní house.obj přímo z prvního uploadu v commitu 544d67f6cbcaa963f1dde9949694e3aa2878af42. Z původního šestého podlaží vybere 357 jedinečných ploch a odečte dvě původní skleněné / plné výplně. Zbývajících 355 kandidátních ploch pro každé podlaží porovnává v geometrii, skupině, materiálu i smoothing stavu.

Před porovnáním test ověří, které kandidátní plochy jsou už obsažené v původním plášti. Tyto plochy se v bytovém modulu neopakují, ale zůstávají v hlavním modelu. Všech 130 vynechaných ploch je geometricky pokryto stejným materiálem, orientací a rovinou pláště. Všechny zbývající plochy odpovídají zdrojové dispozici bez chybějících nebo přidaných polygonů.

Zbylý rozdíl v měřítku Y je nutný pro vyplnění nestejných výšek původní konstrukce:

| Podlaží | Svislé měřítko | Rozdíl vůči originálu |
| ---: | ---: | ---: |
| 1 | 1.0488 | +4.88 % |
| 2 | 1.0001 | +0.01 % |
| 3 | 0.9512 | −4.88 % |
| 4–6 | 1.0000 | 0.00 % |
| 7 | 1.0002 | +0.02 % |
| 8 | 1.0001 | +0.01 % |
| 9–10 | 1.0000 | 0.00 % |
| 11 | 1.0489 | +4.89 % |

Půdorys a topologie opakovaných bytových ploch zůstávají shodné s originálem. První, třetí a jedenácté podlaží nemají totožnou svislou geometrii kvůli rozdílným výškám původních podlaží. Pouhé vypnutí Y měřítka by v kratším třetím podlaží způsobilo kolizi se sousedním podlažím.

## Ovládání prohlížeče

- Levé tlačítko myši: otáčení
- Kolečko: přiblížení / oddálení
- Pravé tlačítko myši: posun
- Front / Side / Top: pevné pohledy
- Wireframe: kontrola polygonální sítě
- Auto orbit: pomalé automatické otáčení
- Ground grid: pomocná podložka
- Reset view: návrat ke standardní perspektivě
- Apartment stack: zobrazí pouze bytové moduly včetně ostění
- Full building: zobrazí celý dům včetně pláště

## Spuštění lokálně

V kořenové složce projektu spusť jednoduchý HTTP server:

```bash
python -m http.server 8000
```

Potom otevři http://localhost:8000. (Ve Windows lze použít také `py -m http.server 8000`.)

Prohlížeč načítá Three.js a jeho OBJ/MTL loadery z CDN. Model a materiály se načítají relativně z repozitáře.

## Data modelu po úpravě

| Vlastnost | Hodnota |
| --- | ---: |
| Vrcholy | 9,455 |
| UV souřadnice | 2,795 |
| Normály | 1,370 |
| Polygony | 6,889 |
| Bytové moduly | 11 (3,773 ploch po odstranění překryvů) |
| Vnější průchozí otvory | 22 |
| Vnitřní průchozí dveřní otvory | 22 |
| Ostění | 84 ploch celkem / 78 nových |
| Duplicitní shell plochy odstraněné z bytových kopií | 130 |
| Skupiny původního modelu | `house`, `kv` |

Jednotka ani fyzické měřítko nejsou ve zdrojovém OBJ souboru doložené. Rozměry proto zůstávají v původních modelových jednotkách.

### Omezení geometrie

Původní export obsahuje otevřené a vícenásobně sdílené hrany. Vyříznutí otvorů a doplnění ostění zlepšují prostorovou geometrii, ale samo o sobě z modelu nedělá uzavřený stavební solid. Před 3D tiskem, konstrukčními výpočty nebo BIM je potřeba provést další opravu a kontrolu geometrie.

---

Three.js: https://threejs.org/ · original source geometry retained and edited

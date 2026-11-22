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
- `.github/workflows/pages.yml` – automatické nasazení na GitHub Pages

## Bytový sloupec

V původním modelu bylo kompletní vnitřní členění nalezeno na šestém podlaží. Z této předlohy bylo vybráno 357 jedinečných polygonů a přeneseno do všech 11 podlaží. Každý bytový modul je samostatně pojmenovaný jako `apartment_column_floor_01` až `apartment_column_floor_11`.

Půdorysná poloha a rozvržení zůstávají shodné. Výška Y je přizpůsobena skutečné konstrukční výšce daného podlaží. Opakující se fasádní geometrie nebyla zbytečně zdvojována.

## Skutečné otvory oken a dveří

Ze zdrojového modelu bylo odstraněno 22 skleněných / plných výplňových polygonů, tedy dvě výplně na každé podlaží. Odpovídající plochy vnější stěny byly geometricky rozříznuty podle jejich skutečných obrysů. Vzniklo 22 průchozích otvorů: jedno okenní pole a jeden vysoký dveřní otvor na každý byt.

Otvory nejsou jen tmavé textury: původní plocha skla a odpovídající části stěn byly odstraněny z geometrie. Průchodnost byla kontrolována vzorkovací mřížkou přes plochu všech 22 otvorů; po celé ploše nebyla nalezena žádná zbývající stěnová nebo skleněná plocha.

V každém podlaží jsou také zachovány dva původní vnitřní dveřní průchody. Ty byly otevřené už ve zdrojové geometrii a nebyly znovu vyřezávány.

## Ostění a hloubka stěn

U 21 otvorů, za kterými zdrojový model obsahoval odpovídající vnější stěnovou rovinu, byly doplněny čtyři boční plochy ostění. Hloubka každého ostění je odvozena ze vzdálenosti mezi původní rovinou vnějšího stěnového panelu a rovinou odstraněné okenní / dveřní výplně, nikoli z jedné odhadnuté konstanty. Naměřené hloubky se v původních modelových jednotkách pohybují přibližně od 0.3306 do 1.0968.

U dveřního otvoru v nejvyšším podlaží nebyla v původním modelu nalezena odpovídající protilehlá stěnová plocha. Otvor proto zůstává průchozí a ostění se tam uměle nedoplňovalo.

Ostění tvoří 84 nových čtyřúhelníkových ploch v samostatných objektech podle podlaží. Materiál `OpeningReveal` je samostatný a lze ho dále upravovat v 3D editoru.

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
| Vrcholy | 9,479 |
| UV souřadnice | 2,819 |
| Normály | 1,376 |
| Polygony | 7,027 |
| Bytové moduly | 11 |
| Vnější průchozí otvory | 22 |
| Vnitřní průchozí dveřní otvory | 22 |
| Ostění | 21 otvorů / 84 ploch |
| Skupiny původního modelu | `house`, `kv` |

Jednotka ani fyzické měřítko nejsou ve zdrojovém OBJ souboru doložené. Rozměry proto zůstávají v původních modelových jednotkách.

### Omezení geometrie

Původní export obsahuje otevřené a vícenásobně sdílené hrany. Vyříznutí otvorů a doplnění ostění zlepšují prostorovou geometrii, ale samo o sobě z modelu nedělá uzavřený stavební solid. Před 3D tiskem, konstrukčními výpočty nebo BIM je potřeba provést další opravu a kontrolu geometrie.

---

Three.js: https://threejs.org/ · original source geometry retained and edited

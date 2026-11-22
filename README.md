# fuzzy-waffle-bohu · HOUSE / Study

Interaktivní 3D model bytového domu s opakovanou dispozicí jednoho vzorového bytu ve všech 11 podlažích. Okna a vysoké dveřní otvory jsou skutečně otevřené skrz obvodové stěny, nejde o tmavé textury ani o ponechané skleněné výplně.

**Demo:** https://akcizur.github.io/fuzzy-waffle-bohu/

## Co je v repozitáři

- `house.obj` – model domu, 11 bytových modulů a geometricky vyříznuté otvory
- `house.txt` – synchronizovaná textová kopie modelu
- `house.mtl` – neutrální materiálová knihovna pro původní názvy materiálů
- `index.html` – samostatný interaktivní 3D prohlížeč
- `tools/repeat_apartment_column.py` – reprodukovatelný generátor bytového sloupce
- `.github/workflows/pages.yml` – automatické nasazení na GitHub Pages

## Bytový sloupec

V původním modelu bylo kompletní vnitřní členění nalezeno na šestém podlaží. Z této předlohy bylo vybráno 357 jedinečných polygonů a přeneseno do všech 11 podlaží. Každý bytový modul je samostatně pojmenovaný jako `apartment_column_floor_01` až `apartment_column_floor_11`.

Půdorysná poloha a rozvržení zůstávají shodné. Výška Y je přizpůsobena skutečné konstrukční výšce daného podlaží. Opakující se fasádní geometrie nebyla zbytečně zdvojována.

## Skutečné otvory oken a dveří

Ze zdrojového modelu bylo odstraněno 22 skleněných / plných výplňových polygonů, tedy dvě výplně na každé podlaží. Odpovídající plochy vnější stěny byly geometricky rozříznuty podle jejich skutečných obrysů. Vzniklo 22 průchozích otvorů: jedno okenní pole a jeden vysoký dveřní otvor na každý byt.

Otvory nebyly vytvořeny pouze odstraněním skla: ve 31 stěnových panelech byla upravena samotná geometrie stěny. Jeden panel bylo možné odstranit celý, zbývajících 30 bylo rozděleno na nové plochy kolem otvorů. Nové trojúhelníkové plochy zachovávají rovinu a normály původních panelů.

V každém podlaží jsou také zachovány dva původní vnitřní dveřní průchody. Ty byly otevřené už ve zdrojové geometrii, proto se znovu nevyřezávaly.

### Kontrola průchodnosti

Byl proveden geometrický test paprskem skrz stěnu ve středu každého otvoru:

- 22 / 22 vnějších okenních a dveřních otvorů bez kolize
- 22 / 22 vnitřních dveřních průchodů bez kolize

Test kontroluje skutečné trojúhelníky v OBJ, nikoli pouze viditelnost materiálu v prohlížeči.

## Ovládání prohlížeče

- Levé tlačítko myši: otáčení
- Kolečko: přiblížení / oddálení
- Pravé tlačítko myši: posun
- Front / Side / Top: pevné pohledy
- Wireframe: kontrola polygonální sítě
- Auto orbit: pomalé automatické otáčení
- Ground grid: pomocná podložka
- Reset view: návrat ke standardní perspektivě
- Apartment stack: zobrazí pouze bytové moduly
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
| Vrcholy | 9,143 |
| UV souřadnice | 2,483 |
| Normály | 1,292 |
| Polygony | 6,943 |
| Bytové moduly | 11 |
| Jedinečné polygony původního modulu | 357 |
| Vnější průchozí otvory | 22 |
| Vnitřní průchozí dveřní otvory | 22 |
| Skupiny původního modelu | `house`, `kv` |
| Rozměr X | 103.9872 |
| Rozměr Y | 169.5991 |
| Rozměr Z | 97.9452 |

Jednotka ani fyzické měřítko nejsou v OBJ souboru doložené. Rozměry proto zůstávají v původních modelových jednotkách.

### Omezení geometrie

Původní export obsahuje otevřené a vícenásobně sdílené hrany. Vyříznutí otvorů zlepšuje průchodnost modelu, ale samo o sobě z něj nedělá uzavřený stavební solid. Před 3D tiskem, konstrukčními výpočty nebo BIM je potřeba provést další opravu a kontrolu geometrie.

### Materiály

Názvy materiálů `Material__743` a `Material__764` jsou převzaté z OBJ. Barvy v `house.mtl` jsou prezentační náhrada; původní materiálová knihovna v repozitáři chyběla.

## Nasazení na GitHub Pages

Workflow se spouští po každém pushi do větve `main` a také ručně přes GitHub Actions. Při prvním nasazení otevři **Settings → Pages → Build and deployment** a nastav **Source: GitHub Actions**.

---

Three.js: https://threejs.org/ · original source geometry retained and edited

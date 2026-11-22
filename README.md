# fuzzy-waffle-bohu · HOUSE / Study

Interaktivní 3D model bytového domu s opakovanou dispozicí jednoho vzorového bytu v celém svislém sloupci.

**Demo:** https://akcizur.github.io/fuzzy-waffle-bohu/

## Co je v repozitáři

- `house.obj` – upravená geometrie domu a jedenáct samostatně pojmenovaných bytových modulů
- `house.txt` – synchronizovaná textová kopie modelu
- `house.mtl` – neutrální materiálová knihovna pro původní názvy materiálů
- `index.html` – samostatný interaktivní 3D prohlížeč
- `tools/repeat_apartment_column.py` – reprodukovatelný generátor bytového sloupce pro čistý původní model
- `.github/workflows/pages.yml` – automatické nasazení na GitHub Pages

## Bytový sloupec

V původním modelu bylo kompletní vnitřní členění nalezeno na šestém podlaží. Z této předlohy bylo vybráno 357 polygonů, které se neopakovaly v ostatních podlažích. Tyto části byly převedeny do samostatných objektů `apartment_column_floor_01` až `apartment_column_floor_11`.

Stejná půdorysná dispozice je nyní ve všech 11 výškových úrovních. Kopírované části zachovávají souřadnice X/Z; pouze výška Y se přizpůsobí skutečné výšce konkrétního podlaží, aby moduly navazovaly na stávající konstrukční úrovně. Opakující se obvodový plášť a fasádní geometrie se znovu nekopírovaly.

Každé podlaží má 357 polygonů bytového modulu. Původní geometrie domu zůstala zachována, pouze jedinečné části vzorového bytu jsou oddělené do pojmenovaných objektů. Díky tomu lze v Blenderu nebo jiném 3D editoru vybrat jednotlivé podlaží samostatně.

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
| Vrcholy | 8 732 |
| UV souřadnice | 2 072 |
| Normály | 881 |
| Polygony | 6 859 |
| Bytové moduly | 11 |
| Polygony na jeden modul | 357 |
| Skupiny původního modelu | `house`, `kv` |
| Výškový rozsah X | 103.9872 |
| Výškový rozsah Y | 169.5991 |
| Výškový rozsah Z | 97.9452 |

Jednotka ani fyzické měřítko nejsou v OBJ souboru doložené. Rozměry proto zůstávají v původních modelových jednotkách.

### Omezení geometrie

Původní export obsahuje otevřené a vícenásobně sdílené hrany. Opakování bytové dispozice tento problém samo o sobě neopravuje. Model proto zatím nelze považovat za ověřený uzavřený solid pro 3D tisk, konstrukční výpočty nebo BIM bez další kontroly a opravy geometrie.

### Materiály

Názvy materiálů `Material__743` a `Material__764` jsou převzaté z OBJ. Barvy v `house.mtl` jsou prezentační náhrada; původní materiálová knihovna v repozitáři chyběla.

## Nasazení na GitHub Pages

Workflow se spouští po každém pushi do větve `main` a také ručně přes GitHub Actions. Při prvním nasazení otevři **Settings → Pages → Build and deployment** a nastav **Source: GitHub Actions**.

---

Three.js: https://threejs.org/ · original source geometry retained

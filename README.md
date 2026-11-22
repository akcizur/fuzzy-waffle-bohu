# fuzzy-waffle-bohu · HOUSE / Study

Minimalistická webová prezentace původního 3D modelu domu v OBJ formátu.

**Demo:** https://akcizur.github.io/fuzzy-waffle-bohu/

## Co je v repozitáři

- \`house.obj\` – původní geometrie, beze změny
- \`house.mtl\` – nově vytvořená neutrální materiálová knihovna, protože soubor na niž OBJ odkazoval v repozitáři chyběl
- \`index.html\` – samostatný interaktivní 3D prohlížeč, bez bundleru a bez instalace balíčků
- \`.github/workflows/pages.yml\` – automatické nasazení na GitHub Pages

## Ovládání

- Levé tlačítko myši: otáčení
- Kolečko: přiblížení / oddálení
- Pravé tlačítko myši: posun
- Front / Side / Top: pevné pohledy
- Wireframe: kontrola polygonální sítě
- Auto orbit: pomalé automatické otáčení
- Ground grid: pomocná podložka
- Reset view: návrat ke standardní perspektivě

## Spuštění lokálně

V kořenové složce projektu spusť jednoduchý HTTP server:

\`\`\`bash
python -m http.server 8000
\`\`\`

Potom otevři http://localhost:8000. (Ve Windows lze použít také \`py -m http.server 8000\`.)

Prohlížeč načítá Three.js a jeho OBJ/MTL loadery z CDN. Samotný model i materiály se načítají relativně z repozitáře.

## Data zdrojového modelu

| Vlastnost | Hodnota |
| --- | ---: |
| Vrcholy | 3 912 |
| UV souřadnice | 2 072 |
| Normály | 881 |
| Polygony | 3 289 |
| Skupiny | \`house\`, \`kv\` |
| Původní rozsah X | 103.9872 |
| Původní rozsah Y | 169.5991 |
| Původní rozsah Z | 97.9452 |

Jednotka ani fyzické měřítko nejsou v OBJ souboru doložené. Rozměry proto zůstávají v původních modelových jednotkách.

### Omezení geometrie

Základní kontrola indexovaných hran ukazuje otevřené a vícenásobně sdílené hrany. Část výsledku může ovlivňovat způsob exportu a oddělené vrcholy na švech, ale síť není možné bez další opravy považovat za ověřený uzavřený solid. Před 3D tiskem, kolizními výpočty, BIM nebo výrobou je potřeba geometrii zkontrolovat a případně opravit v Blenderu či jiném 3D nástroji.

### Materiály

Názvy materiálů \`Material__743\` a \`Material__764\` jsou převzaté z OBJ. Barvy v novém \`house.mtl\` jsou neutrální prezentační náhrada; původní barevné hodnoty nebyly k dispozici.

## Nasazení na GitHub Pages

Workflow se spouští po každém pushi do větve \`main\` a také ručně přes GitHub Actions. Při prvním nasazení otevři **Settings → Pages → Build and deployment** a nastav **Source: GitHub Actions**. Aktuální GitHub Actions token nemá oprávnění vytvořit Pages web automaticky, takže tuto jednorázovou aktivaci musí provést správce repozitáře. Potom v **Actions** spusť workflow „Deploy model viewer“ ručně, případně odešli další commit do `main`.

---

Three.js: https://threejs.org/ · model source preserved

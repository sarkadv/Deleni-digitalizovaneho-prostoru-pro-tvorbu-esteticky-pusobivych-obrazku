# Využití geometrického dělení digitalizovaného obrazu pro tvorbu esteticky působivých obrázků

Program, který stylizuje vstupní obrázek pomocí geometrického dělení prostoru. Obrázek rozdělí na oblasti
Voroného diagramem, Delaunayho triangulací nebo kvadrantovým stromem, každou oblast vybarví podle původního
obrázku a volitelně přidá speciální efekt. Bakalářská práce na Fakultě aplikovaných věd (2025).

## Jak to funguje

1. **Výběr bodů.** Z obrázku se vybere počáteční množina bodů podle zvoleného rozložení.
2. **Dělení prostoru.** Nad body se vytvoří teselace (dělení prostoru). Voroného diagram a Delaunayho triangulace 
   používají implementaci z knihovny SciPy, kvadrantový strom má vlastní implementaci.
3. **Vykreslení.** Vzniklé oblasti se vykreslí podle zvoleného efektu a výsledek se uloží jako obrázek PNG.

Vstupem je obrázek ve formátu JPEG (barevný model RGB). Výstup je ve formátu PNG, protože je bezeztrátový a
nevytváří artefakty na ostrých hranách mezi oblastmi.

### Teselace, rozložení bodů a efekty

| Teselace                    | Rozložení bodů                                                                                     | Efekty                                                                 |
| --------------------------- | -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Voroného diagram            | rovnoměrné, normální (pravidlo třetin), dělení oblastí podle chyby, Mitchellův algoritmus          | mřížka (jednobarevná / vícebarevná), gradienty, papír                  |
| Delaunayho triangulace      | rovnoměrné, normální (pravidlo třetin), Laplaceův operátor (3 varianty), Mitchellův algoritmus     | mřížka (jednobarevná / vícebarevná), gradienty, papír                  |
| Kvadrantový strom           | dané principem teselace                                                                            | mřížka (jednobarevná / vícebarevná), gradienty, různé tvary oblastí, obdélníkové oblasti s ovály |

Delaunayho triangulace je k dispozici ve dvou variantách: rychlejší a s lepšími barvami. Vždy je také možné
nepoužít žádný efekt.

Rozložení bodů, která respektují obsah obrázku (Laplaceův operátor, dělení oblastí podle chyby, kvadrantový
strom), zachovávají více detailů originálu. Rovnoměrné rozložení a Mitchellův algoritmus dávají silněji
stylizovaný, mozaikovitý výsledek.

## Instalace

### Python

Program vyžaduje Python. Preferovaná a otestovaná verze je
[3.11](https://www.python.org/downloads/release/python-3119/). S novějšími nebo staršími verzemi nemusí být
použité knihovny kompatibilní.

### Pillow, NumPy, SciPy a Shapely

V adresáři programu spusťte:

```
pip install -r requirements.txt
```

### Tkinter

Tkinter se většinou instaluje spolu s Pythonem. Pokud program spadne na chybě `Module Tkinter not found`:

- **macOS:** Tkinter je vždy nainstalován spolu s Pythonem.
- **Linux (Ubuntu / Debian):** `sudo apt-get install python3-tk`. Pokud ani poté není modul nalezen, pomůže
  `sudo apt-get install tk-dev` a reinstalace Pythonu.
- **Windows:** Znovu spusťte instalátor Pythonu, zvolte opravu instalace a v okně „Optional Features“
  zaškrtněte „tcl/tk“.

### Pycairo

Nejdříve nainstalujte systémovou knihovnu cairo:

- **macOS:** `brew install cairo pkg-config` (vyžaduje [Homebrew](https://brew.sh))
- **Linux (Ubuntu / Debian):** `sudo apt-get install libcairo2-dev pkg-config python3-dev`
- **Windows:** není potřeba nic instalovat.

Poté na všech systémech spusťte:

```
pip install pycairo
```

Podle nastavení systému může být místo `pip` potřeba použít `pip3`.

## Spuštění

```
python3 main.py
```

1. Klikněte na **Vybrat obrázek** a zvolte obrázek ve formátu JPEG. Ukázkové obrázky jsou ve složce
   `img_input/`.
2. Volitelně zaškrtněte **Zapsat vygenerované body do souboru**. Body se uloží do složky `points_output/`.
3. Vyberte teselaci, rozložení bodů a efekt.
4. Klikněte na **Generovat**. Po dokončení zobrazte výsledek tlačítkem **Zobrazit** a uložte ho tlačítkem
   **Uložit obrázek**.

## Struktura programu

| Soubor / adresář            | Obsah                                                                    |
| --------------------------- | ------------------------------------------------------------------------ |
| `main.py`                   | Vstupní bod programu                                                     |
| `point_generator.py`        | Výběr počáteční množiny bodů                                             |
| `tessellation_generator.py` | Dělení prostoru na oblasti                                               |
| `visualizer.py`             | Vykreslení oblastí podle zvoleného efektu                                |
| `distributions/`            | Jednotlivá rozložení bodů                                                |
| `tessellations/`            | Voroného diagram, Delaunayho triangulace a kvadrantový strom             |
| `geometry/`                 | Oblasti, body a pixely                                                   |
| `gui/`                      | Grafické uživatelské rozhraní (Tkinter)                                  |
| `enums/`                    | Výčtové typy teselací, rozložení bodů a efektů                           |
| `util/`                     | Pomocné funkce pro barvy, geometrii, konvoluci, vykreslování a zápis bodů |
| `img_input/`                | Ukázkové vstupní obrázky                                                 |
| `img_output/`               | Výchozí složka pro uložení výsledných obrázků                            |
| `points_output/`            | Složka pro soubory s vygenerovanými body                                 |

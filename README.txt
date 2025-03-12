- INSTALACE PYTHON 3 -
Pro spuštění programu je nutné mít nainstalovaný interpreter jazyka Python.
Preferovaná a otestovaná verze je 3.11, kterou je možné stáhnout na adrese:
https://www.python.org/downloads/release/python-3119/

Pro novější nebo starší verze nemusí být k dispozici / kompatibilitní
použité knihovny!

---------------------------------------------------------------------------------

- INSTALACE KNIHOVEN -
1) Pillow, NumPy, SciPy, Shapely
V adresáři programu je nutné spustit příkaz:
"pip install -r requirements.txt" nebo "pip3 install -r requirements.txt"
(záleží na nastavení aliasu na konkrétním systému).

2) Tkinter
Knihovna Tkinter je už většinou nainstalovaná spolu s celým Pythonem.
Pokud se tak nestalo, je potřeba ji doinstalovat.

    a) MacOS
    Je nutné použít balíčkovací systém Homebrew (instalace podle https://brew.sh).
    Poté pro instalaci stačí příkaz:
    "brew install python-tk".

    b) Linux (Ubuntu / Debian)
    Pro instalaci stačí příkaz:
    "apt-get install python3-tk".

    c) Windows
    Je potřeba znovu spustit Python installer a opravit instalaci Pythonu.
    V okně "Optional Features" je nutné mít zaškrtlou možnost "tcl/tk".

3) Pycairo
    a) MacOS
    Je nutné použít balíčkovací systém Homebrew (instalace podle https://brew.sh).
    Poté spustit příkaz:
    "brew install cairo pkg-config"

    b) Linux (Ubuntu / Debian)
    Nutné použít příkaz:
    "sudo apt install libcairo2-dev pkg-config python3-dev"

    c) Windows
    Stačí pouze společný příkaz o řádku níže.

Nakonec společné pro všechny platformy - příkaz:
"pip install pycairo" nebo "pip3 install pycairo"
(záleží na nastavení aliasu na konkrétním systému).

---------------------------------------------------------------------------------

- SPUŠTĚNÍ PROGRAMU -
V adresáři programu stačí spustit příkaz:
"python main.py" nebo "python3 main.py"
(záleží na nastavení aliasu na konkrétním systému).


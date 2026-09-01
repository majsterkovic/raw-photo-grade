# Mobile / Linear DNG — co wiedzieć zanim wywołasz

Źródła: analiza Gemini ("Tworzenie Skilla Claude Code DNG.md", 2026-08-28, zweryfikowana),
dokumentacja rawpy/LibRaw, Halide "Understanding ProRAW", doświadczenia z repo phone-dng-grade.

## Dlaczego telefonowy DNG ≠ klasyczny Bayer RAW

| Cecha | DSLR/mirrorless Bayer RAW | Mobilny Linear DNG (ProRAW, Pixel RAW+, Samsung) |
|---|---|---|
| Stan danych | surowa mosaika Bayera | fuzja wieloklatkowa, częściowo przetworzona, liniowa |
| Odszumianie | dopiero w postprocessingu | częściowo wykonane przez ISP przed zapisem |
| Metadane tonalne | statyczne profile aparatu | gain mapy (ISO-21496-1 / Apple gain map), tablice gainu |
| Biały punkt | stały próg ADC (np. 16383) | zmienny po fuzji klatek |
| Przestrzeń wyjściowa | macierz aparatu → sRGB | pre-zprofilowana Linear sRGB / Display P3 |

## Żelazne zasady wywoływania (potwierdzone, wdrożone w develop.py)

1. `use_camera_wb=True` — smartfon zapisuje trafne mnożniki WB w momencie ekspozycji;
   omijanie ich daje zafarb (zwłaszcza Pixel bywa zimny w cieniu / zielony przy LED).
2. `no_auto_bright=True` — LibRaw domyślnie liniowo podnosi jasność do średniej;
   w mobilnym DNG z już nałożonym tone-mappingiem to niszczy czerń i światła.
   Ekspozycję koryguj świadomie (`--exposure`), nie przez auto-bright.
3. Nie podnoś shadow tak mocno jak przy pełnej klatce — szum żyje w cieniach małej matrycy.
4. ProRAW ma już lokalny tone-mapping: `--shadows` + `--clarity` na maks = od razu fałsz.
5. 48/50 MP: zawsze preview na długim boku ~1600 px przed pełnym eksportem.
6. Orientacja bywa tylko w EXIF — `--orient auto` (domyślne w skryptach) stosuje ją;
   przy ręcznych operacjach poza skryptami sprawdzić obrót przed kadrowaniem.
7. Gain map (HDR DNG, iPhone 15+/Android Ultra HDR): podstawowy JPEG to SDR-baza;
   pełny HDR wymaga parsera gain map — na razie poza zakresem skilla; jeśli EXIF
   sugeruje HDR (Ultra HDR / gain map), uprzedź użytkownika zamiast udawać, że widziałeś pełny zakres.

## Proste geometrie kadrów (wdrożone w crop.py)

- `--straighten` — histogram orientacji mocnych krawędzi (odpowiednik Hougha w numpy)
  wyznacza dominującą nearly-poziomą linię; rotacja ±10° max, potem inscribed-rect
  (żadne czarne rogi nie trafiają do wyniku). Kąt zwracany w JSON — jeśli po rotacji
  kadr pochylony MOCNIEJ, załóż kąt 0 i użyj `--box` albo popraw ręcznie.
- `--horizon` — umieszcza wyznaczony horyzont na 1/3 lub 2/3 kadru (reguła trójpodziału).

## Kiedy NIE używać tej ścieżki

- Pliki z zaawansowanym retuszem/warstwami → najpierw JPEG/TIFF z aplikacji.
- HDR gain-map jako wynik końcowy → potrzebne dedykowane narzędzie (np. ImageMagick ≥7.1 obsługuje HDR JPEG partial).
- Potrzebna maska lokalna/retusz obiektowy →.darktable/RawTherapee GUI, nie ten skill.

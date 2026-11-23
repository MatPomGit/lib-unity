# Model zagrożeń biblioteki lib-unity

**Stan: analiza źródła adaptera read-only (2026-11-22).** Kontrole
przeanalizowano dla PR #1, nie dla rzeczywistego Unity Editor.
Testy Unity CLI, Windows, Pipeline i urządzeń: **NOT_RUN**.

| Aktywo i granica | Ryzyko / scenariusz | Kontrola w kodzie | Dowód / pozostały warunek |
| --- | --- | --- | --- |
| Lokalny program `unity`, PATH i `--executable` | Podstawiony wykonywalny plik uruchomi dowolny kod z prawami użytkownika | `shell=False`, stały wektor argv i allowlista nazw poleceń; **nie** uwierzytelniają pliku | Wyłącznie zaufana, zweryfikowana binarka i PATH; test rzeczywistego CLI NOT_RUN |
| `status/list/commands` | Nieznana komenda mogłaby zmienić projekt | Odrzucenie wszystkich innych nazw; brak `eval` / `command` | `tests/test_adapter.py`, CI exact-SHA |
| stdout JSON z lokalnego CLI | Duży lub złośliwy wynik powoduje wyczerpanie pamięci | Odczyt co najwyżej 1 MiB + 1 bajt, przerwanie procesu po przekroczeniu limitu, timeout maks. 60 s | Testy syntetyczne, brak Unity E2E |
| JSON i błędy CLI | Uszkodzone dane, błędne `success` i exit status | Parsowanie JSON, walidacja typu, błędy i kod wyjścia | Testy offline, brak kontraktu wersji Unity potwierdzonego E2E |
| Zwrócona telemetria i metadane edytora | Nazwy projektów/ścieżki lub diagnostyka mogą być prywatne | Biblioteka nie zapisuje wyników ani nie transmituje ich sama | Odbiorca odpowiada za ograniczenie logów, retencję, kontrolę dostępu i eksport |
| Wheel / zależności | Podmiana i niezweryfikowane wydanie | CI smoke-test instalacji, brak publikacji | Release i łańcuch dostaw wymagają odrębnej oceny |

**Granice ochrony:** przekazany przez konsumenta parametr `executable`
i zmienna `PATH` to wejścia zaufane, nie sandbox. Adapter uruchamia
lokalny proces z uprawnieniami bieżącego użytkownika; nie izoluje
złośliwego ani podmienionego CLI. Przed użyciem w systemie
operacyjnym wymagane są weryfikacja dostawcy, lokalizacji/wersji
binarki, minimalne uprawnienia i osobny test zachowania.

Subprocess `stderr` jest odrzucany, a `stdout` nie jest logowany
automatycznie. Wyniki API mogą nadal zawierać informacje prywatne;
zabroniona jest ich niejawna publikacja w CI, Issues i Pages.
Ograniczenie rozmiaru i czasu chroni proces wywołujący przed
typowym nadmiernym wynikiem, ale nie jest granicą bezpieczeństwa
wobec złośliwego procesu potomnego, który mógłby tworzyć procesy
lub pliki poza adapterem. Zabezpieczenie wymaga izolacji na poziomie OS.

**Ryzyko rezydualne:** brak E2E z faktycznym `unity`, brak
autoryzowanego audytu binarki i brak aktywnego kanału zgłaszania
podatności (`SECURITY.md`). Nie deklarować produkcyjnego
bezpieczeństwa ani certyfikacji zgodności silnika.

Powiązania: [przepływ danych](../architecture/data-flow.md),
[bezpieczeństwo](../../SECURITY.md), [testy](../testing.md).

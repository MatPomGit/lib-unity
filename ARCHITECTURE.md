# Architektura lib-unity

`src/lib_unity/client.py` uruchamia odczytowe polecenia
oficjalnego Unity CLI bez powłoki. Nie implementuje własnego
serwera MCP, schedulerów ani operacji zmieniających projekt.

**Wejście:** zaufana lokalna binarka `unity` i polecenie
z allowlisty `status/list/commands`. **Wyjście:** sparsowany
JSON (obiekt lub lista), maksymalnie 1 MiB surowego stdout.
Adapter wywołuje lokalny proces z uprawnieniami konsumenta,
z timeoutem 15 sekund domyślnie (maksymalnie 60 sekund).
Nie jest sandboxem dla podmienionej binarki lub niepewnego PATH.

**Kontrole offline:** odmowa komend mutujących i niepoprawnych
typów, limit wielkości odpowiedzi, timeout, brak binarki,
niezerowy exit code, niepoprawny JSON i envelope `success/errors`.
Wynik jest zwracany w pamięci bez zapisu i bez automatycznej
transmisji. Konsument odpowiada za prywatność i retencję
metadanych edytora.

**Stan:** adapter read-only zaimplementowany; rzeczywiste
Unity CLI, Unity Editor i Unity Pipeline E2E **NOT_RUN**.
Dokumenty: [granice zaufania](docs/security/threat-model.md),
[przepływ danych](docs/architecture/data-flow.md).
Operacje write, `eval` i mutacje należą do odrębnego etapu,
wymagają zatwierdzenia i nie są elementem tego PR.

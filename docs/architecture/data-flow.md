# Przepływy danych i granice zaufania

**Stan: IMPLEMENTED (adapter lokalnego CLI), ENGINE_E2E_NOT_RUN.**

Przepływ: **konsument Python → `UnityCLI.query` → walidacja nazwy
polecenia → zaufany lokalny program `unity` → stdout JSON do 1 MiB
→ walidacja kodu wyjścia i schematu → wynik w pamięci konsumenta**.

Wejście zawiera ścieżkę do binarki `unity` lub nazwę wyszukiwaną
przez PATH. To granica zaufania i decyzja konsumenta; sam adapter
nie potwierdza integralności binarki. Wywołanie używa wyłącznie
`status`, `list` lub `commands` oraz `--format json`.
Nie uruchamia powłoki, komend mutujących, `eval` ani działań
wymagających instalacji. Timeout domyślnie 15 sekund, dozwolony
maksymalnie 60 sekund. Wielkość stdout jest ograniczona przed
pełnym odczytem do pamięci; stderr nie jest zachowywany.

Wyjście: obiekt lub lista JSON. Przy braku binarki, timeout,
niepoprawnym JSON, niedozwolonej nazwie, zbyt dużej odpowiedzi
lub błędzie CLI biblioteka zgłasza wyjątek. Adapter nie zapisuje
wyników, nie przesyła ich sieciowo, nie redaguje informacji
o projektach ani nie kontroluje dalszej retencji i publikacji
danych przez aplikację konsumenta. Odbiorca musi sam wymusić
minimalizację, kontrolę dostępu, retencję i zasady logowania.

Wynik JSON może zawierać nazwy projektów, lokalizacje i metadane
uruchomionego Unity Editor; nie należy umieszczać prawdziwych
odpowiedzi w publicznych logach testów. Przebiegi CI używają
syntetycznych fixture, nie prawdziwego edytora.
Nie ustalono jeszcze zgodności z Unity Pipeline, OpenXR ani
urządzeniami. Testy tych środowisk: **NOT_RUN**.

Powiązania: [model zagrożeń](../security/threat-model.md),
[prywatność](../privacy.md), [kontrakt](../contracts.md).

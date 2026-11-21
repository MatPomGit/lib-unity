# lib-unity

Biblioteka Python do odczytywania stanu podłączonego edytora i listy narzędzi poprzez **oficjalne Unity CLI**. Wersja rozwojowa, bez wydania i bez zależności od dostawcy LLM.

## Zakres wersji rozwojowej

Adapter udostępnia wyłącznie trzy polecenia: `unity status --format json`, `unity list --format json`, `unity commands --format json`. Nie wywołuje `unity command`, `unity eval` ani mutacji zasobów. Wywołania używają tablicy argumentów bez shell, timeoutu i walidacji JSON.

## Instalacja i użycie

Zainstaluj [Unity CLI](https://docs.unity.com/en-us/unity-cli), a dla sterowania pracującym edytorem zainstaluj Unity Pipeline (Unity 6.0 LTS+). Python 3.11+:

```bash
python -m pip install -e .
python -m lib_unity status
python -m lib_unity list
python -m unittest discover -s tests -v
```

Lista poleceń dostępnych w danej wersji CLI jest dynamiczna. Unity CLI obsługuje także `unity mcp` dla klientów MCP. Nie jest to część niniejszej biblioteki rozwojowej.

## Bezpieczeństwo i status

Biblioteka nie instaluje oprogramowania i nie wykonuje arbitralnych poleceń. Integracja z aktywnym Unity, OpenXR, Quest 3 i Android: **NOT_RUN**. [Kontrakt](contracts/api.json) · [Architektura](ARCHITECTURE.md) · [Licencja](LICENSE).

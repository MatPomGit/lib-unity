# Architektura lib-unity

`src/lib_unity/client.py` uruchamia wybrane polecenia odczytowe oficjalnego Unity CLI przez `subprocess.run` bez powłoki. CLI jest źródłem prawdy o podłączonych edytorach i narzędziach. Adapter nie implementuje drugiego serwera MCP ani własnej infrastruktury kolejkowej.

Wejście: lokalna ścieżka do wykonywalnego `unity`, nazwa dozwolonego polecenia. Wyjście: sparsowany JSON z CLI. Ochrona: allowlist `status/list/commands`, limit czasu 15 s, brak mutacji. Zweryfikowane offline błędy: brak binarki, timeout, niezerowy exit code, nieprawidłowy JSON.

Kolejny etap: adapter write z listą dozwolonych komend, potwierdzaniem projektu, suchym przebiegiem i audytem Research Autopilot. Nie wykonywać automatycznie `eval` ani arbitralnych skryptów otrzymanych od modelu.

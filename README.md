# Dagon

Bot discordowy z klimatem Przedwiecznego: rzuty kośćmi do RPG i obrazki na zawołanie.

## Komendy

Prefiks: `!!` (albo wzmianka `@Dagon`). Pełna lista: `!!help`.

| Komenda | Opis |
|---|---|
| `!!roll 3d6` / `!!roll 2k10` | Rzut kośćmi (max 100 kości, max 100 ścianek) |
| `!!motivate` (`!!mot`, `!!m`) | Motywujący obrazek z inspirobot.me |
| `!!cat`, `!!dog`, `!!duck`, `!!fox` | Losowe zwierzaki |

## Uruchomienie

```sh
cp .env.example .env   # uzupełnij DISCORD_TOKEN
poetry install
make start
```

Docker:

```sh
make docker-build
make docker-run
```

W Discord Developer Portal bot musi mieć włączony intent **Message Content**.

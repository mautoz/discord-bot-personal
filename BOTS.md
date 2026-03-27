# Discord Bots — Documentação

Todos os bots rodam na VPS `89.117.33.57` com `nohup python3.8`.
Logs em `logs/`, PIDs em `pids/`.

---

## 👋 welcome_member.py

Monitora entrada e saída de membros no servidor.

| Evento | Comportamento |
|---|---|
| Membro entra | Embed verde com menção, nome do servidor e número do membro |
| Membro sai | Embed vermelho com frase da série *Eu, a Patro e as Crianças* |

**Env:** `DISCORD_TOKEN`, `GERAL_CHANNEL`

---

## 🎬 imdb_bot.py

Busca informações de filmes e séries via **OMDB API**.

| Comando | Descrição |
|---|---|
| `$title <termo>` | Busca títulos por nome |
| `$id <imdbID>` | Ficha completa pelo ID do IMDB |

**Env:** `DISCORD_TOKEN`, `IMDB_CHANNEL`

---

## 🤖 movies_cast_bot.py (Wall-E)

Busca informações detalhadas de filmes e séries via **The Movie DB (TMDB)**.

| Comando | Descrição |
|---|---|
| `$help` | Lista todos os comandos |
| `$movie <título>` | Busca filmes e retorna IDs |
| `$serie <título>` | Busca séries e retorna IDs |
| `$info <id>` | Ficha completa do filme: diretor, roteiristas, fotografia, trilha, elenco, bilheteria, nota |
| `$serieinfo <id>` | Ficha completa da série: criadores, temporadas, episódios, elenco, nota |
| `$cast <id>` | Elenco completo do filme |
| `$seriecast <id>` | Elenco completo da série |
| `$posters <id>` | Galeria de imagens do filme (até 5) |
| `$serieposters <id>` | Galeria de imagens da série (até 5) |

**Env:** `DISCORD_TOKEN_WALLE`, `IMDB_CHANNEL`, `IMDB_CHANNEL_SKYNET`, `TMDB_KEY`

---

## 📺 youtube_bot.py

Busca canais e vídeos recentes via **YouTube Data API**.

| Comando | Descrição |
|---|---|
| `$channels` | Lista canais monitorados |
| `$getid <nome>` | Retorna ID de um canal |
| `$searchchannel <nome>` | Busca ID de um canal no YouTube |
| `$last <nome>` | Vídeos publicados nas últimas 24h |

**Env:** `DISCORD_TOKEN_GERO`, `YOUTUBE_CHANNEL`, `YOUTUBE_CHANNEL_HAL`, `DEVELOPER_KEY`

---

## 🎮 games_deals_bot.py

Publica descontos de jogos diariamente via **IsThereAnyDeal API** (região BR).
Roda automaticamente a cada 24h.

**Env:** `DISCORD_TOKEN_HAL`, `SKYNET_GAMES_CHANNEL`, `TROPA_GAMES_CHANNEL`, `ITAD_API_KEY`

---

## 🎬 movies_upcoming_bot.py

Publica lançamentos de filmes nos cinemas semanalmente via **TMDB**.
Filtra filmes em inglês ou português com estreia em até 7 dias.

**Env:** `DISCORD_TOKEN_HAL`, `TROPA_UPCOMING_CHANNEL`, `SKYNET_UPCOMING_CHANNEL`, `TMDB_KEY`

---

## 📰 entertainment_news_bot.py

Busca notícias de entretenimento via **NewsAPI**.

| Comando | Descrição |
|---|---|
| `$queronoticias` | Notícias em PT-BR (Brasil) |
| `$queronews` | Notícias em EN-US (EUA) |

**Env:** `DISCORD_TOKEN_HAL`, `SKYNET_NEWS_CHANNEL`, `TROPA_NEWS_CHANNEL`, `NEWS_API_KEY`

---

## 🖥️ check_bot_status.py

Monitor de status de todos os bots. Atualiza embeds fixos no Discord a cada hora.

- **Embed principal** — status de todos os bots (🟢/🔴)
- **Embed C-3PO** — status do bot de transcrição de voz

**Env:** `DISCORD_TOKEN_HAL`, `SERVER_CHANNEL`, `SERVER_CHANNEL_HAL`, `SERVER_DEFAULT_MSG`, `SERVER_DEFAULT_MSG_HAL`, `MSG_STATUS_C3PO`, `MSG_STATUS_C3PO_TD`

---

## 🎙️ voice_transcription_bot.py (C-3PO)

Bot Telegram que transcreve mensagens de voz.
Repo separado: `github.com/mautoz/voice-transcription`
Pasta na VPS: `~/voice-transcription/`

**Env:** `TELEGRAM_TOKEN`

---

## Operações na VPS

```bash
# Ver bots rodando
ps aux | grep python3.8

# Ver log de um bot
tail -f ~/discord-bot-personal/logs/<bot>.log

# Reiniciar um bot
kill $(cat ~/discord-bot-personal/pids/<bot>.pid)
cd ~/discord-bot-personal
nohup python3.8 <bot>.py > logs/<bot>.log 2>&1 &

# Atualizar código
cd ~/discord-bot-personal && git pull
```

# 🦋 Fern (The Core Pipeline)

> *"A strict, reliable orchestrator. It doesn't tolerate delays."*

**Fern** is the central nervous system and real-time orchestrator of the Frieren AI Ecosystem. Built on top of `pipecat-ai` and driven by `asyncio`, it manages the entire multimodal pipeline with extreme focus on ultra-low latency.

> [!IMPORTANT]
> **Development Reboot:** This repository marks a complete overhaul of the core pipeline. The previous implementation was highly synchronous and relied on subpar workarounds. This new iteration transitions fully to `pipecat-ai`, enforcing strict asynchronous handling, shifting CPU-bound workloads entirely onto **Heiter**, and establishing proper concurrency. The legacy codebase remains accessible in the `old` branch.

## 🔮 Responsibilities

* **The Gatekeeper:** Establishes and manages bidirectional WebRTC connections with `frieren-desktop`.
* **The Transcriber:** Captures raw PCM audio from the client and routes it through fast VAD and STT.
* **The Catalyst:** Streams context to `heiter` (Inference Server) and processes incoming text tokens on the fly.
* **The Alchemist:** Generates real-time audio streams via TTS and simultaneously extracts speech visemes (mouth animation data) to push back to the 3D client.
* **Interruption Handling:** Instantly purges active buffers the moment the user starts speaking, ensuring natural conversation flow.

## 📐 Architecture Flow

| From | Direction / Protocol | To | Data Transferred |
| :--- | :--- | :--- | :--- |
| `frieren-desktop` | `---> (Raw Audio PCM) ---ч>` | `VAD / STT` | Captures raw microphone input from the client. |
| `VAD / STT` | `---> (Audio/Text Chunks) --->` | `heiter` (LLM) Service | Decoded voice tokens routed to the inference backend. |
| `heiter` (LLM) Service | `<--- (Text Tokens) <---` | TTS Engine | Text tokens generated on the fly stream directly into the synthesis layer. |
| TTS Engine | `<--- (Audio & Visemes) <---` | `frieren-desktop` | Final synthesized audio frames and real-time lip-sync JSON pushed back to the 3D client. |

## 🛠 Tech Stack & Spells

* **Core Engine:** Python 3.14 (Optimized for `asyncio`)
* **Pipeline Framework:** `pipecat-ai`
* **Network Protocol:** LiveKIT for audio
* **Dependencies:** `pydantic`, `httpx`, `aiohttp`

---
*Part of the [Frieren AI Ecosystem](https://github.com/Frierenclaw)*
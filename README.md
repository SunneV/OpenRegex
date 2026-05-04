<div align="center">
  <img src="docs/static/logo.svg" alt="OpenRegex Logo" width="280" style="max-width: 100%; height: auto;">
  <br>
  <img src="docs/static/name.svg" alt="OpenRegex Name" width="450" style="max-width: 100%; height: auto; margin-top: 15px;">
</div>

Official website: **[OpenRegex.com](https://www.openregex.com)**

[![GitHub stars](https://img.shields.io/github/stars/sunnev/openregex)]()

OpenRegex is a unified, open-source platform for testing, debugging, and analyzing regular expressions within isolated
runtimes (Runtime-as-a-Service). It provides developers with a tool that guarantees 100% result consistency with the
target production environment, eliminating the discrepancies between native regex dialects.

<div align="center">
  <img src="docs/static/screenshots/app-screenshot.png" alt="OpenRegex Architecture" style="max-width: 100%; height: auto; margin-top: 15px;">
</div>

---

## 🌟 Key Features

* **Polyglot Micro-Workers:** Native engine execution via completely isolated Docker containers.
* **Pattern Inspector:** Advanced React + Vite frontend for dynamic visual match inspection and group highlighting.
* **AI-Powered Assistant (`worker-ai`):** An optional, independent worker using separate queues designed specifically
  for regex. It automatically generates complex patterns from natural language prompts, explains obscure syntax, and
  optimizes inefficient queries. **🛡️ Security Note:** For production deployments, it is highly recommended to route
  requests through an LLM proxy server (like **LiteLLM**) to safely manage and isolate your API keys rather than
  exposing them directly to the worker environment.
* **Zero-Trust Guardrails:** 1000ms SLA (engine-dependent overrides possible), strict memory limits (e.g., 8MB heap
  limits for binary engines), and multiprocessing isolation to prevent ReDoS attacks.
* **Living Docs System:** Dynamic knowledge base featuring context-aware cheat sheets and engine-specific trivia (
  Factograph).
* **Smart Discovery:** Automatic heartbeat registration of worker node capabilities via Redis.

---

## 🖼️ Feature Showcase

### Multi Regex Engine Selection

Run patterns across multiple engines and compare results instantly.

<img src="docs/static/screenshots/engine-selection.png" alt="Multi Regex Engine Selection" width="800">

---

### Cross-Engine Compatibility Report

Detect inconsistencies and portability issues between engines.

<img src="docs/static/screenshots/compatibility-report-1.png" alt="Compatibility Report 1" width="800">
<br>
<img src="docs/static/screenshots/compatibility-report-2.png" alt="Compatibility Report 2" width="800">

---

### Personal Storage

Store and manage regex patterns locally in your browser.

<img src="docs/static/screenshots/personal-storage.png" alt="Personal Storage" width="800">

---

### Advanced Hint System

Hover tokens to get instant explanations.

<img src="docs/static/screenshots/hint-system.png" alt="Hint System" width="800">

---

### AI Optimization

Generate, explain, and optimize regex patterns.

<img src="docs/static/screenshots/ai-optimization.png" alt="AI Optimization" width="800">

---

## ⚙️ Core Infrastructure

| Component                | Role                 | Tech Stack                                                                             | Version                                                                                                                                         | Downloads                                                                       |
|:-------------------------|:---------------------|:---------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------|
| **Frontend**             | `openregex-frontend` | React + Vite UI. Handles visualization, and worker health monitoring.                  | [![Version](https://img.shields.io/docker/v/sunnev/openregex-frontend?label=latest)](https://hub.docker.com/r/sunnev/openregex-frontend/tags)   | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-frontend?label=)  |
| **Backend**              | `openregex-backend`  | API Orchestrator. Manages Redis job queues, worker discovery, and security guardrails. | [![Version](https://img.shields.io/docker/v/sunnev/openregex-backend?label=latest)](https://hub.docker.com/r/sunnev/openregex-backend/tags)     | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-backend?label=)   |
| **AI Worker** (Optional) | `worker-ai`          | LLM-powered Regex assistant. Generates, explains, and optimizes complex patterns.      | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-ai?label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-ai/tags) | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-ai?label=) |

---

## 🚀 Engine Matrix

| Worker Image    | Engine ID         | Algorithm      | Features & Use Case                                        | Version                                                                                                                                                           | Downloads                                                                           |
|:----------------|:------------------|:---------------|:-----------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------|
| `worker-python` | `python*_re`      | NFA            | Standard `re` module. Susceptible to ReDoS.                | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-python?sort=date&label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-python/tags) | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-python?label=) |
| `worker-python` | `python*_regex`   | NFA (Advanced) | PyPI `regex` module. Variable lookbehinds, fuzzy matching. | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-python?sort=date&label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-python/tags) | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-python?label=) |
| `worker-c-cpp`  | `cpp_re2`         | DFA            | Google RE2. Guaranteed $O(n)$ time, ReDoS-safe.            | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-c-cpp?sort=date&label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-c-cpp/tags)   | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-c-cpp?label=)  |
| `worker-c-cpp`  | `cpp_std`         | NFA            | Standard C++11 `std::regex`. ECMAScript default.           | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-c-cpp?sort=date&label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-c-cpp/tags)   | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-c-cpp?label=)  |
| `worker-c-cpp`  | `cpp_boost`       | NFA (Advanced) | Boost.Regex. PCRE syntax, recursive patterns.              | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-c-cpp?sort=date&label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-c-cpp/tags)   | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-c-cpp?label=)  |
| `worker-c-cpp`  | `cpp_hyperscan`   | DFA/Automata   | Intel Hyperscan. High-performance stream scanning.         | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-c-cpp?sort=date&label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-c-cpp/tags)   | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-c-cpp?label=)  |
| `worker-c-cpp`  | `c_pcre2`         | NFA/JIT        | PCRE2 library. Industry standard for Perl-compatibility.   | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-c-cpp?sort=date&label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-c-cpp/tags)   | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-c-cpp?label=)  |
| `worker-c-cpp`  | `c_onig`          | NFA            | Oniguruma. Used in VS Code, supports multi-encoding.       | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-c-cpp?sort=date&label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-c-cpp/tags)   | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-c-cpp?label=)  |
| `worker-c-cpp`  | `c_posix`         | NFA            | POSIX `regex.h`. Standard libc implementation (ERE).       | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-c-cpp?sort=date&label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-c-cpp/tags)   | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-c-cpp?label=)  |
| `worker-dotnet` | `dotnet_standard` | NFA (Advanced) | `System.Text.RegularExpressions`. Balancing groups.        | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-dotnet?sort=date&label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-dotnet/tags) | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-dotnet?label=) |
| `worker-go`     | `go_standard`     | DFA            | Standard `regexp` package. ReDoS-safe, linear time.        | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-go?sort=date&label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-go/tags)         | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-go?label=)     |
| `worker-jvm`    | `jvm_standard`    | NFA            | Standard `java.util.regex`. Backtracking engine.           | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-jvm?sort=date&label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-jvm/tags)       | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-jvm?label=)    |
| `worker-jvm`    | `jvm_re2j`        | DFA            | Google's RE2J. Guaranteed $O(n)$ execution, ReDoS-safe.    | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-jvm?sort=date&label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-jvm/tags)       | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-jvm?label=)    |
| `worker-rust`   | `rust_standard`   | DFA            | Rust `regex` crate. Linear time $O(n)$, ReDoS-safe.        | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-rust?sort=date&label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-rust/tags)     | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-rust?label=)   |
| `worker-v8`     | `v8_standard`     | NFA            | Native Node.js RegExp. Supports modern `v` flag.           | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-v8?sort=date&label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-v8/tags)         | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-v8?label=)     |
| `worker-php`    | `php_pcre`        | NFA            | PHP `preg_*` functions. PCRE2 based.                       | [![Version](https://img.shields.io/docker/v/sunnev/openregex-worker-php?sort=date&label=latest)](https://hub.docker.com/r/sunnev/openregex-worker-php/tags)       | ![Pulls](https://img.shields.io/docker/pulls/sunnev/openregex-worker-php?label=)    |

---

## 📡 System Topology

<div align="center">
  <img src="docs/static/infographic.png" alt="OpenRegex Architecture" style="max-width: 100%; height: auto; margin-top: 15px;">
</div>

OpenRegex utilizes a microservices architecture managed via UV Workspaces:

1. **OpenRegex Backend (FastAPI):** Central API hub routing traffic using "Smart Discovery".
2. **OpenRegex Frontend (React + Vite):** The visual inspector UI.
3. **Redis Backbone:** Message broker handling task queues (`queue:{family}`) and result pub/sub channels (
   `result:{task_id}`).
4. **Worker Isolators:** Isolated worker nodes (Python, C++, Java, etc.) executing sub-processes for exact native regex
   behaviors.

---

## 🛠️ Installation & Deployment

OpenRegex 2.0 is fully containerized. You no longer need to manually install compilers or runtimes on your host machine.

### Prerequisites

* Docker & Docker Compose
* Git

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/sunnev/openregex.git](https://github.com/sunnev/openregex.git)
   cd openregex
   ```

2. **Set up the Environment File:**
   ```bash
   cp .env.example .env
   ```

3. **Start the Development Environment:**

   **On Windows:**
   ```cmd
   .\deploy\run_deploy.bat
   ```
   **On Linux/macOS:**
   ```bash
   docker-compose -f deploy/docker-compose.yml --env-file .env down -v
   docker-compose -f deploy/docker-compose.yml --env-file .env up --build -d
   ```

4. **Access the Application:**
   Open your browser and navigate to `http://localhost:5000`. The FastAPI backend will be available at
   `http://localhost:8000`.

---

### 📝 Environment Configuration (`.env`)

To customize your OpenRegex deployment, you can configure various parameters in your `.env` file. Below is a breakdown
of the available settings to manage SEO, rate limits, AI worker parameters, and strict execution boundaries:

| Component    | Environment Variable              | Default Value         | Explanation                                                                                                    |
|--------------|:----------------------------------|:----------------------|:---------------------------------------------------------------------------------------------------------------|
| Frontend     | **`ROBOTS_META`**                 | `"noindex, nofollow"` | Controls search engine indexing for production environments. Set to `"index, follow"` to make the site public. |
| Frontend     | **`VITE_APP_TERMS`**              | `""`                  | Toggles the Terms of Service and Cookie Policy popup. Use accept to disable it.                                |
| Backend      | **`RATE_LIMIT_REQUESTS`**         | `60`                  | The maximum number of requests allowed per engine per minute to prevent abuse.                                 |
| Backend      | **`RATE_LIMIT_WINDOW`**           | `60`                  | The time window (in seconds) for the rate-limiting threshold.                                                  |
| Backend      | **`API_AI_ENDPOINT_ENABLE`**      | `"false"`             | Toggles the availability of the AI assistant endpoint (`worker-ai`).                                           |
| Backend      | **`API_REGEX_ENDPOINT_ENABLE`**   | `"true"`              | Toggles the core regex evaluation endpoint.                                                                    |
| Backend      | **`MAX_AI_QUEUE`**                | `10`                  | Max users allowed in the human-agent waitlist before new requests are rejected.                                |
| AI Worker    | **`AI_MAX_WORKERS`**              | `2`                   | The maximum number of concurrent AI worker processes.                                                          |
| AI Worker    | **`LLM_ENDPOINT`**                | `""`                  | The base URL for the LLM service. Can be pointed to a proxy like LiteLLM.                                      |
| AI Worker    | **`LLM_MODEL`**                   | `""`                  | The specific LLM model used for generating, explaining, and optimizing patterns.                               |
| AI Worker    | **`LLM_API_KEY`**                 | `""`                  | Your secret API key for the chosen LLM provider.                                                               |
| AI Worker    | **`LLM_SSL_VERIFY`**              | `"true"`              | Determines whether SSL certificates should be verified when communicating with the LLM endpoint.               |
| Regex Worker | **`WORKER_EXECUTION_TIMEOUT_MS`** | `1000`                | The strict execution SLA (in milliseconds) applied across all regex workers to prevent ReDoS attacks.          |
| Regex Worker | **`WORKER_MAX_INPUT_SIZE`**       | `10485760`            | The maximum allowed length (10MB) for the subject text being tested.                                           |
| Regex Worker | **`WORKER_MAX_MATCHES`**          | `10000`               | The upper limit on the number of individual matches returned by the engine.                                    |
| Regex Worker | **`WORKER_MAX_GROUPS`**           | `1000`                | The maximum number of capture groups processed per request.                                                    |
| Regex Worker | **`WORKER_MAX_JSON_SIZE`**        | `10485760`            | The maximum allowed size (10MB) for JSON payloads communicated over the Redis backbone.                        |

## 🐳 Self-Hosting with Docker Compose

OpenRegex is designed to be easily self-hosted. Using Docker Compose, you can spin up the entire ecosystem—including the
orchestration backend, the visual frontend, and the polyglot worker nodes—with a single command.

**👉 [Example Docker Compose File](docker-compose.yml)**

Run `docker-compose up -d` to deploy.

---

## 🏗️ Documentation

OpenRegex is built on strict architectural guidelines to ensure high performance and maintainability.

**👉 [Read the full Documentation Library & Technical Specifications](docs/README.md)**

---

## OpenRegex Platform Changelog

This is the central orchestration log for the OpenRegex ecosystem. Detailed technical logs for individual components are
maintained within their respective directories:

**👉 [Changelog table](./CHANGELOG.md)**

---

## 📜 Licensing

OpenRegex is licensed under the Apache License 2.0.

Worker components are executed as isolated services and may include third-party libraries under their own licenses (
e.g., BSD, MIT, LGPL). These licenses apply only to the respective worker environments and do not affect the licensing
of the core platform.

For a full list of third-party dependencies and their licenses, see:
[Third-Party Licenses & Notices](THIRD-PARTY-LICENSES.md)

---

## Compliance Guide

### If you use OpenRegex:

* No obligations (Apache 2.0 allows commercial use)

### If you redistribute:

You MUST:

* include LICENSE
* include NOTICE
* preserve attribution

### If you modify:

* mark changes
* keep license notices

### Third-party software:

Each worker includes separate licenses.
See THIRD-PARTY-LICENSES.md


---

## ❤️ Support

You like my work? Just sponsor me!

☕ [![GitHub sponsors](https://img.shields.io/github/sponsors/sunnev)]() ☕


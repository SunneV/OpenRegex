# Third-Party Licenses & Notices

The OpenRegex project utilizes various open-source libraries, runtime environments, and engine binaries across its polyglot worker nodes and orchestration services.

The primary OpenRegex platform is licensed under the **Apache License 2.0**.

---

## 1. Architecture & Compliance Model

OpenRegex operates on an **isolated micro-worker architecture** (Runtime-as-a-Service):
* **Decoupled Runtimes:** Worker components and native regex binaries run inside separate Docker containers and communicate exclusively via standard IPC (subprocesses, standard I/O) and network message queues (Redis).
* **No Proprietary Linking:** No third-party engine code is statically linked into the core OpenRegex API or frontend inspector.
* **Scope of Licenses:** Third-party licenses apply **strictly to the respective worker environments and compiled binaries**, and do not contaminate or alter the Apache 2.0 licensing of the core platform.

---

## 2. Regex Engine License Matrix

The table below provides a comprehensive overview of all regular expression engines evaluated by OpenRegex:

| Engine ID | Worker Container | Library / Runtime | Upstream Maintainer | License (SPDX) | Integration / Linking | Copyleft / Risk Assessment |
|:---|:---|:---|:---|:---|:---|:---|
| `python*_re` | `worker-python` | Python Standard `re` | Python Software Foundation | [PSF-2.0](https://spdx.org/licenses/PSF-2.0.html) | Native interpreter standard library | Permissive; non-viral |
| `python*_regex` | `worker-python` | `regex` package | Matthew Barnett | [Python-2.0](https://spdx.org/licenses/Python-2.0.html) / [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) | PyPI C-extension module | Permissive; non-viral |
| `cpp_re2` | `worker-c-cpp` | Google RE2 (`libre2`) | Google LLC | [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) | Dynamic library linkage (`-lre2`) | Permissive; non-viral |
| `cpp_std` | `worker-c-cpp` | ISO C++ `std::regex` (`libstdc++`) | Free Software Foundation (GCC) | [GPL-3.0-or-later WITH GCC-exception-3.1](https://spdx.org/licenses/GPL-3.0-or-later.html) | Standard C++ Runtime library | Copyleft with Runtime Exception (non-viral for binaries) |
| `cpp_boost` | `worker-c-cpp` | Boost.Regex (`libboost_regex`) | Boost Community | [BSL-1.0](https://spdx.org/licenses/BSL-1.0.html) | Dynamic library linkage (`-lboost_regex`) | Permissive; no binary attribution required |
| `cpp_hyperscan` | `worker-c-cpp` | Intel Hyperscan / Vectorscan | Intel Corporation / VectorCamp | [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) | Dynamic library linkage (`-lhs`) | Permissive; non-viral |
| `c_pcre2` | `worker-c-cpp` | PCRE2 Library (`libpcre2-8`) | Philip Hazel & Zoltan Herczeg | [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) | Dynamic library linkage (`-lpcre2-8`) | Permissive; non-viral |
| `c_onig` | `worker-c-cpp` | Oniguruma (`libonig`) | K.Kosako & K.Takata | [BSD-2-Clause](https://spdx.org/licenses/BSD-2-Clause.html) | Dynamic library linkage (`-lonig`) | Permissive; non-viral |
| `c_posix` | `worker-c-cpp` | GNU C Library `regex.h` (`glibc`) | Free Software Foundation (GNU) | [LGPL-2.1-or-later](https://spdx.org/licenses/LGPL-2.1-or-later.html) | Standard C dynamic runtime linkage | Weak Copyleft; satisfied via standard dynamic linking without glibc modifications |
| `v8_standard` | `worker-v8` | Native V8 RegExp (`RegExp`) | Node.js contributors & Google V8 | [MIT](https://spdx.org/licenses/MIT.html) / [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) | Node.js built-in runtime object | Permissive; non-viral |
| `v8_re2` | `worker-v8` | `node-re2` (Google RE2 wrapper) | Eugene Lazutkin & Google LLC | [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) | Node.js native C++ addon module | Permissive; non-viral |
| `jvm_standard` | `worker-jvm` | `java.util.regex` (OpenJDK) | Eclipse Temurin / Oracle / OpenJDK | [GPL-2.0-only WITH Classpath-exception-2.0](https://openjdk.org/legal/gplv2+ce.html) | Java Virtual Machine core runtime | Copyleft with Classpath Exception (non-viral for independent applications) |
| `jvm_re2j` | `worker-jvm` | RE2J (`com.google.re2j:re2j`) | Google LLC | [Go / BSD-3-Clause style](https://github.com/google/re2j/blob/master/LICENSE) | JVM Maven dependency | Permissive; non-viral |
| `dotnet_standard` | `worker-dotnet` | `System.Text.RegularExpressions` | Microsoft Corporation (.NET Foundation) | [MIT](https://spdx.org/licenses/MIT.html) | .NET 10 BCL runtime class | Permissive; non-viral |
| `go_standard` | `worker-go` | `regexp` package | The Go Authors | [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) | Go standard library module | Permissive; non-viral |
| `rust_standard` | `worker-rust` | `regex` crate | The Rust Project Developers | [MIT](https://spdx.org/licenses/MIT.html) OR [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) | Rust Cargo crate compilation | Permissive; dual-licensed |
| `php_pcre` | `worker-php` | PHP PCRE Extension (`preg_*`) | The PHP Group & PCRE project | [PHP-3.01](https://spdx.org/licenses/PHP-3.01.html) / [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) | PHP CLI built-in runtime extension | Permissive open-source license |

---

## 3. Copyleft & Runtime Exception Analysis

### 3.1. LGPL-2.1 Components (`glibc` / `c_posix`)
* The POSIX regex implementation utilizes the standard system C library (`glibc`), licensed under the **GNU Lesser General Public License v2.1 or later (LGPL-2.1-or-later)**.
* **Compliance Verification:** OpenRegex links dynamically to the unmodified system `libc.so.6` supplied by the base OS image (Debian / Alpine). Under Section 6 of LGPL-2.1, dynamically linking unmodified shared libraries does not subject the host application or calling orchestrator to copyleft terms.

### 3.2. GPLv3 with GCC Runtime Library Exception (`libstdc++` / `cpp_std`)
* The C++ standard regex engine utilizes `libstdc++`, licensed under **GPL-3.0 with GCC Runtime Library Exception v3.1**.
* **Compliance Verification:** The GCC Runtime Library Exception explicitly permits compiling code that includes GCC headers and linking against the standard C++ library to create independent binaries under any license of choice (including Apache 2.0 and proprietary distributions), provided the compilation process was conducted with an Eligible Compilation Process.

### 3.3. GPLv2 with Classpath Exception (`Eclipse Temurin` / `OpenJDK` / `jvm_standard`)
* The Java Virtual Machine execution environment is based on Eclipse Temurin (OpenJDK), licensed under **GPL-2.0 with the Classpath Exception**.
* **Compliance Verification:** The Classpath Exception explicitly allows linking independent Java applications against the standard class library without subjecting the application code itself to GPL requirements.

---

## 4. Redistribution and Compliance Checklist

When deploying, redistributing, or packaging OpenRegex in containerized or binary form:

1. **Preserve Attribution:** Keep the `LICENSE` and `NOTICE` files in all root distributions and source repositories.
2. **Third-Party Notices:** Do not remove copyright headers from vendor libraries or container base images.
3. **Container Image Integrity:** When creating derivative worker images, maintain the relevant third-party license texts in their respective image layers (`/usr/share/doc/*` or vendor directories).
4. **Commercial Use:** The Apache 2.0 license of OpenRegex and the permissive/exception-backed licenses of all third-party components permit free commercial, educational, and internal enterprise usage.

---

## 5. Standard License Text References

For detailed full legal texts of the standard open-source licenses referenced above, consult the official SPDX registry:

* **Apache License 2.0:** [`https://spdx.org/licenses/Apache-2.0.html`](https://spdx.org/licenses/Apache-2.0.html)
* **MIT License:** [`https://spdx.org/licenses/MIT.html`](https://spdx.org/licenses/MIT.html)
* **BSD 3-Clause "New" or "Revised" License:** [`https://spdx.org/licenses/BSD-3-Clause.html`](https://spdx.org/licenses/BSD-3-Clause.html)
* **BSD 2-Clause "Simplified" License:** [`https://spdx.org/licenses/BSD-2-Clause.html`](https://spdx.org/licenses/BSD-2-Clause.html)
* **Boost Software License 1.0:** [`https://spdx.org/licenses/BSL-1.0.html`](https://spdx.org/licenses/BSL-1.0.html)
* **Python Software Foundation License 2.0:** [`https://spdx.org/licenses/PSF-2.0.html`](https://spdx.org/licenses/PSF-2.0.html)
* **GNU Lesser General Public License v2.1:** [`https://spdx.org/licenses/LGPL-2.1-or-later.html`](https://spdx.org/licenses/LGPL-2.1-or-later.html)
* **GNU General Public License v2.0 w/ Classpath Exception:** [`https://openjdk.org/legal/gplv2+ce.html`](https://openjdk.org/legal/gplv2+ce.html)
* **GNU General Public License v3.0 w/ GCC Runtime Exception:** [`https://spdx.org/licenses/GCC-exception-3.1.html`](https://spdx.org/licenses/GCC-exception-3.1.html)
* **The PHP License v3.01:** [`https://spdx.org/licenses/PHP-3.01.html`](https://spdx.org/licenses/PHP-3.01.html)
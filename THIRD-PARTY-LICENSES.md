# Third-Party Licenses & Notices

The OpenRegex project utilizes various open-source libraries and components across its worker nodes.

The primary project is licensed under the Apache License 2.0.

Worker components are executed as isolated services (Docker containers / subprocesses) and may include third-party software under their respective licenses listed below.

---

## Licensing Model & Compliance

- The core OpenRegex platform is licensed under Apache 2.0.
- Worker components are **not linked** to the core application and run as independent runtimes.
- Therefore, third-party licenses apply **only to the respective worker environments**, not to the entire platform.

### LGPL Components (glibc)

The POSIX implementation (`glibc`) is licensed under LGPL.

OpenRegex uses system-provided libc in a compliant way:
- via dynamic linking
- without modification

This satisfies LGPL requirements.

### GPL Components with Exceptions

Some components are distributed under GPL licenses with exceptions:

- OpenJDK → GPLv2 + Classpath Exception  
- libstdc++ → GPLv3 + GCC Runtime Exception  

These exceptions explicitly allow use in non-GPL and Apache-licensed projects without imposing copyleft obligations.

---

## 1. worker-v8 (JavaScript / Node.js)
* v8_standard → MIT (Node.js) / BSD 3-Clause (V8)
* v8_re2 → BSD 3-Clause

## 2. worker-c-cpp (C / C++)
* c_onig → BSD 2-Clause
* c_pcre2 → BSD 3-Clause
* c_posix → LGPL (glibc)
* cpp_boost → BSL-1.0
* cpp_hyperscan → BSD 3-Clause
* cpp_re2 → BSD 3-Clause
* cpp_std → GPLv3 + GCC Runtime Exception

## 3. worker-dotnet
* dotnet_standard → MIT

## 4. worker-go
* go_standard → BSD 3-Clause

## 5. worker-jvm
* jvm_standard → GPLv2 + Classpath Exception
* jvm_re2j → BSD 3-Clause

## 6. worker-php
* php_pcre → PHP License / BSD 3-Clause (PCRE2)

## 7. worker-python
* python_re → PSFL
* python_regex → PSFL / ZPL

## 8. worker-rust
* rust_standard → MIT OR Apache-2.0

---

## Distribution Notes

When OpenRegex is distributed via Docker images or compiled binaries:

- Third-party licenses apply only to the components included in that image
- License notices must be preserved
- Users are responsible for compliance when redistributing modified images

End users and redistributors are responsible for ensuring compliance with applicable licenses when modifying or redistributing OpenRegex components.
---

## Appendix: Example License Text (BSD 3-Clause)

### BSD 3-Clause License (Example for RE2 / node-re2)
```text
Copyright (c) 2005-2026, [Original Author(s) / e.g., Eugene Lazutkin for node-re2]
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

  * Redistributions of source code must retain the above copyright notice, this
    list of conditions and the following disclaimer.
  * Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.
  * Neither the name of the copyright holder nor the names of its contributors
    may be used to endorse or promote products derived from this software
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
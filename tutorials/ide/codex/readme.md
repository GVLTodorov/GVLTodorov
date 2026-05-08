# Codex CLI Installation (Ubuntu)

Short guide for installing OpenAI Codex CLI on Ubuntu 22.04, 24.04, and 26.04.

## 1. Install prerequisites

```bash
sudo apt update
sudo apt install curl ca-certificates
```

---

## 2. Install Codex CLI (Recommended: Binary Method)

### For x86_64 systems

```bash
curl -fL -o codex.tar.gz \
https://github.com/openai/codex/releases/latest/download/codex-x86_64-unknown-linux-musl.tar.gz

tar -xzf codex.tar.gz

sudo install -m 0755 codex-x86_64-unknown-linux-musl /usr/local/bin/codex

rm codex.tar.gz codex-x86_64-unknown-linux-musl
```

### For ARM64 systems

```bash
curl -fL -o codex.tar.gz \
https://github.com/openai/codex/releases/latest/download/codex-aarch64-unknown-linux-musl.tar.gz

tar -xzf codex.tar.gz

sudo install -m 0755 codex-aarch64-unknown-linux-musl /usr/local/bin/codex

rm codex.tar.gz codex-aarch64-unknown-linux-musl
```

---

## 3. Verify installation

```bash
codex --version
```

---

## 4. Authenticate

### Login with ChatGPT account

```bash
codex login
```

### Login with API key

```bash
printenv OPENAI_API_KEY | codex login --with-api-key
```

---

## 5. Basic usage

Start interactive session:

```bash
codex
```

Run with prompt:

```bash
codex "explain this project"
```

Non-interactive mode:

```bash
codex exec "summarize this repository"
```

Review local changes:

```bash
codex review --uncommitted
```

---

## 6. Update Codex

```bash
update-codex-cli
```

---

## 7. Uninstall

```bash
sudo rm -f /usr/local/bin/codex
rm -rf ~/.codex
```

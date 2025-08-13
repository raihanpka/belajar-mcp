# MCP Chat CLI (Extended version dari Anthropic MCP Course)

MCP Chat CLI adalah aplikasi antarmuka baris perintah yang memungkinkan kemampuan obrolan interaktif dengan model AI melalui API Anthropic. Aplikasi ini mendukung pengambilan dokumen, prompt berbasis perintah, dan integrasi alat yang dapat diperluas melalui arsitektur MCP (Model Control Protocol).

## Prasyarat

- Python 3.9+
- OpenAI API Key atau Anthropic API Key (Aku pakai OpenAI)

## Setup

### Langkah 1: Konfigurasi variabel lingkungan

1. Buat atau edit file `.env` di root proyek dan verifikasi bahwa variabel-variabel berikut diatur dengan benar:

```
OPENAI_API_KEY=""  # Enter your OpenAI API secret key
```

### Langkah 2: Install dependencies

#### Opsi 1: Setup dengan `uv` (Disarankan)

[uv](https://github.com/astral-sh/uv) adalah fast Python package installer and resolver.

1. Install uv, jika belum terinstall:

```bash
pip install uv
```

2. Buat dan aktifkan virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install package/dependencies:

```bash
uv pip install -e .
```

4. Jalankan project nya

```bash
uv run main.py
```

#### Opsi 2: Setup tanpa `uv`

1. Buat dan aktifkan virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install package/dependencies:

```bash
pip install anthropic python-dotenv prompt-toolkit "mcp[cli]==1.8.0"
```

3. Jalankan project nya

```bash
python main.py
```

### Penggunaan

#### Cara Interaksi

Cukup ketik pesan Anda dan tekan Enter untuk berbicara dengan model.

#### Pengambilan Dokumen

Gunakan simbol @ diikuti oleh ID dokumen untuk memasukkan konten dokumen dalam query Anda:

```
> Tell me about @deposition.md
```

### Commands

Gunakan prefix / untuk mengeksekusi command yang didefinisikan di MCP server:

```
> /summarize deposition.md
```

Command akan otomatis auto-complete ketika Anda menekan Tab.

## Pengembangan

### Menambahkan Dokumen Baru

Edit file `mcp_server.py` untuk menambahkan dokumen baru ke dalam dictionary `docs`.

### Implementasi MCP Features

Untuk mengimplementasikan MCP features:

1. Lagi menyelesaikan TODOs yang ada di `mcp_server.py`
2. Implementasikan fungsi yang kurang di `mcp_client.py`

### Credit
Introduction to Model Context Protocol (MCP) Course by Anthropic
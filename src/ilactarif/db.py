"""SQLite şeması ve bağlantı yönetimi.

Tablolar:
  drugs         — İlaç ana kaydı (Excel'den import edilen + sonradan eklenen)
  drug_labels   — Bir ilaca ait 1/2/3 numaralı etiket içerikleri (JSON)
  settings      — Eczane bilgileri, uygulama ayarları

Şema sade tutuldu; FTS5 vb. iyileştirmeler veri modeli onaylandıktan sonra eklenecek.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "ilactarif.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS drugs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode         TEXT    UNIQUE,
    name            TEXT    NOT NULL,
    manufacturer    TEXT,
    drug_type       TEXT,            -- 'İLAÇ' veya 'PASİF İLAÇ'
    sales_count     INTEGER DEFAULT 0,   -- Excel 'Çıkış' sütunu
    stock           INTEGER DEFAULT 0,
    equivalent_code TEXT,
    rank            INTEGER,         -- Çıkış'a göre sıralama (1 = en çok satan)
    created_at      TEXT    DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT    DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_drugs_rank ON drugs(rank);
CREATE INDEX IF NOT EXISTS idx_drugs_name ON drugs(name);

CREATE TABLE IF NOT EXISTS drug_labels (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    drug_id      INTEGER NOT NULL REFERENCES drugs(id) ON DELETE CASCADE,
    label_type   INTEGER NOT NULL CHECK (label_type IN (1, 2, 3)),
    -- 1 = Kullanım/dozaj etiketi
    -- 2 = Hazırlama etiketi (şurup/süspansiyon)
    -- 3 = Uyarı etiketi
    content_json TEXT    NOT NULL,    -- Yapısal içerik (bkz. models.py)
    source_url   TEXT,                -- Bilginin alındığı kaynak (Titck, prospektüs vb.)
    reviewed     INTEGER DEFAULT 0,   -- Eczacı onayı (0=AI, 1=onaylanmış, 2=düzeltilmiş)
    filled_at    TEXT    DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(drug_id, label_type)
);

CREATE INDEX IF NOT EXISTS idx_labels_drug ON drug_labels(drug_id);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""


DEFAULT_SETTINGS = {
    "eczane_adi":     "İKİZLER ECZANESİ",
    "eczane_telefon": "",
    "eczane_adres":   "",
}


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """SQLite bağlantısı döndürür. Foreign keys aktif, satırlar dict gibi erişilebilir."""
    path = Path(db_path) if db_path else DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Tabloları oluştur ve varsayılan ayarları ekle."""
    conn.executescript(SCHEMA)
    for k, v in DEFAULT_SETTINGS.items():
        conn.execute(
            "INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)", (k, v)
        )
    conn.commit()


if __name__ == "__main__":
    with get_connection() as c:
        init_schema(c)
        print(f"OK: schema initialized at {DB_PATH}")

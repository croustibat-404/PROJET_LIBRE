CREATE TABLE IF NOT EXISTS users (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,   -- identifiant interne pas exposé
    client_number  TEXT    NOT NULL UNIQUE,             -- identifiant PUBLIC de connexion
    first_name     TEXT    NOT NULL,
    last_name      TEXT    NOT NULL,
    email          TEXT    NOT NULL UNIQUE,
    phone          TEXT,                                -- facultatif : seule colonne sans NOT NULL
    password_hash  TEXT    NOT NULL,                    -- le hash
    created_at     TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Comptes bancaires : un client peut en avoir plusieurs
CREATE TABLE IF NOT EXISTS accounts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL
                    REFERENCES users(id) ON DELETE RESTRICT,   -- impossible de supprimer un client qui a des comptes, plus sécurisé que ON DELETE CASCADE
    type            TEXT    NOT NULL CHECK (type IN ('checking', 'savings')),
    account_number  TEXT    NOT NULL UNIQUE,
    balance_cents   INTEGER NOT NULL DEFAULT 0 CHECK (balance_cents >= 0),
    created_at      TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Virements entre comptes
CREATE TABLE IF NOT EXISTS transfers (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    from_account_id       INTEGER NOT NULL
                        REFERENCES accounts(id) ON DELETE RESTRICT,
    to_account_id         INTEGER NOT NULL
                        REFERENCES accounts(id) ON DELETE RESTRICT,
    amount_cents          INTEGER NOT NULL CHECK (amount_cents > 0),
    label                 TEXT,                                  -- motif, facultatif
    status                TEXT    NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'completed', 'rejected')),
    created_at            TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (from_account_id <> to_account_id)                     -- pas de virement vers soi-même
);

CREATE INDEX IF NOT EXISTS idx_transfers_from ON transfers(from_account_id, created_at);
CREATE INDEX IF NOT EXISTS idx_transfers_to   ON transfers(to_account_id, created_at);
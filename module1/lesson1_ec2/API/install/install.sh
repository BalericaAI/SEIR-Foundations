#!/bin/bash

set -e

# ======================================
#  BALERICA LEGACY BANK INSTALLER
# ======================================
#
# Builds the full lab on Amazon Linux 2023:
#
#   FastAPI  (modern edge)
#   GnuCOBOL (legacy core)
#   SQLite   (system of record)
#
# Run it from the repo:
#
#   bash module1/lesson1_ec2/API/install/install.sh
#
# ======================================

# The repo directory this script lives in (install/..)
SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BANK_HOME="/opt/balerica-bank"

echo "======================================"
echo " BALERICA LEGACY BANK INSTALLER"
echo "======================================"
echo
echo "Source : $SRC_DIR"
echo "Target : $BANK_HOME"
echo

echo "[1/9] Updating packages..."
sudo dnf update -y

echo "[2/9] Installing dependencies..."
sudo dnf install -y \
    python3 \
    python3-pip \
    sqlite \
    gcc \
    make \
    autoconf \
    automake \
    libtool \
    flex \
    bison \
    gmp-devel \
    ncurses-devel \
    tar \
    gzip

# Amazon Linux 2023's dnf repos do not package gnucobol, and
# AL2023 does not support EPEL the way older Amazon Linux/RHEL
# did, so GnuCOBOL is built from source here instead.
# --without-db skips Berkeley DB / ISAM support, which this lab
# does not need (account_lookup/payment_post only use
# LINE SEQUENTIAL files).
if ! command -v cobc >/dev/null 2>&1; then
    echo "  gnucobol is not packaged for AL2023 - building GnuCOBOL 3.2 from source..."
    GNUCOBOL_TMP="$(mktemp -d)"
    curl -fsSL -o "$GNUCOBOL_TMP/gnucobol.tar.gz" \
        "https://sourceforge.net/projects/gnucobol/files/gnucobol/3.2/gnucobol-3.2.tar.gz/download"
    tar xzf "$GNUCOBOL_TMP/gnucobol.tar.gz" -C "$GNUCOBOL_TMP"
    (
        cd "$GNUCOBOL_TMP/gnucobol-3.2"
        ./configure --prefix=/usr/local --without-db
        make -j"$(nproc)"
        sudo make install
    )
    echo /usr/local/lib | sudo tee /etc/ld.so.conf.d/gnucobol.conf > /dev/null
    sudo ldconfig
    rm -rf "$GNUCOBOL_TMP"
else
    echo "  GnuCOBOL already installed, skipping build."
fi

echo "[3/9] Creating directories..."
sudo mkdir -p $BANK_HOME/{app,cobol/bin,data,logs,agents,swift}

sudo chown -R $USER:$USER $BANK_HOME

echo "[4/9] Copying Balerica Bank sources..."
cp "$SRC_DIR"/app/*.py        $BANK_HOME/app/
cp "$SRC_DIR"/cobol/*.cob     $BANK_HOME/cobol/
cp "$SRC_DIR"/agents/*.py     $BANK_HOME/agents/
cp "$SRC_DIR"/swift/*.py      $BANK_HOME/swift/

cd $BANK_HOME

echo "[5/9] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "[6/9] Installing Python packages..."
pip install \
    fastapi \
    uvicorn \
    boto3 \
    python-dotenv

echo "[7/9] Creating database..."

sqlite3 data/bank.db <<'SQL'

CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    status TEXT NOT NULL,
    balance REAL NOT NULL,
    currency TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    status TEXT NOT NULL,
    reference TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO accounts
VALUES
(
    '100001',
    'Alice Johnson',
    'ACTIVE',
    5000.00,
    'USD'
);

INSERT OR IGNORE INTO accounts
VALUES
(
    '100002',
    'Robert Smith',
    'ACTIVE',
    2750.00,
    'USD'
);

INSERT OR IGNORE INTO accounts
VALUES
(
    '100003',
    'Maria Garcia',
    'ACTIVE',
    8100.00,
    'USD'
);

SQL

echo "[8/9] Compiling COBOL programs..."

cobc -x \
    -o cobol/bin/account_lookup \
    cobol/account_lookup.cob

cobc -x \
    -o cobol/bin/payment_post \
    cobol/payment_post.cob

# OPEN EXTEND cannot create the journal; an empty file can.
touch data/payments.dat

echo "[9/9] Exporting the ledger for the COBOL core..."

# COBOL reads fixed-width records, not SQLite.
# The bridge module writes data/accounts.dat.
python3 -c "
import sys
sys.path.insert(0, 'app')
import cobol_bridge
count = cobol_bridge.export_accounts()
print(f'  exported {count} account(s) to data/accounts.dat')
"

echo
echo "Installation complete."
echo
echo "Smoke-test the COBOL core:"
echo
echo "  cd $BANK_HOME"
echo "  ./cobol/bin/account_lookup 100001"
echo "  ./cobol/bin/payment_post TXN0001 100001 125.50 USD INV-1001"
echo
echo "Start the bank API:"
echo
echo "  cd $BANK_HOME"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo
echo "Then prove connectivity with SWIFT traffic:"
echo
echo "  python3 swift/traffic_generator.py --count 10"
echo

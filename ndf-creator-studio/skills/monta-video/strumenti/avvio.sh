#!/bin/sh
# NDF Creator Studio: il programma di avvio per il Mac. Lo stesso comando installa la prima volta e controlla in
# silenzio a ogni chat:   sh "<studio>/strumenti/avvio.sh" [opzioni di controllo.py]
#
# Usa solo quello che c'è su ogni Mac (sh, curl, tar, shasum). Lo studio ha il SUO Python 3.12, nella sua casa
# (~/Library/Application Support/NDFCreatorStudio/python): se non c'è lo scarica (circa 20 MB, una volta sola) e lo
# controlla con l'impronta SHA-256 scritta qui sotto. Non usa MAI il python3 del Mac: senza gli strumenti per
# sviluppatori apre la finestra "installa gli strumenti", e quello di Homebrew su alcuni Mac è rotto.
# Niente password, niente installato nel sistema. Poi passa la mano a controllo.py, che stampa le righe STATO e
# alla fine PRONTO o NON PRONTO.

PY_VERSIONE='3.12.15'
PY_USCITA='20261021'
PY_FONTE='https://github.com/astral-sh/python-build-standalone/releases/download'
SHA_ARM='a18cc33862b53bd54a148c710def5375c1b47470cccedf817a19c2d211764584'      # Mac Apple Silicon
SHA_INTEL='869e0b30959beccc616ce14907439f4d0b3170c5830a2362dade07f07b0ed3b8'    # Mac Intel

QUI=$(cd "$(dirname "$0")" && pwd)
if [ -n "${NDF_STUDIO_CASA:-}" ]; then
  CASA="$NDF_STUDIO_CASA"
else
  CASA="$HOME/Library/Application Support/NDFCreatorStudio"
fi

va() {   # è un Python dello studio che funziona?
  [ -x "$1" ] && "$1" -c 'import sys; sys.exit(0 if sys.version_info[:2] == (3, 12) else 1)' >/dev/null 2>&1
}

non_pronto() {
  echo "STATO Python dello studio: MANCA · $1"
  echo "NON PRONTO"
  exit 1
}

PY=''
for c in "$CASA/venv/bin/python" "$CASA/python/bin/python3"; do
  if va "$c"; then PY="$c"; break; fi
done

if [ -z "$PY" ]; then
  if [ "$(uname -s)" != Darwin ]; then
    non_pronto "questo programma di avvio è per il Mac; su Windows si usa avvio.ps1"
  fi
  if [ "$(uname -m)" = arm64 ] || [ "$(sysctl -n hw.optional.arm64 2>/dev/null)" = 1 ]; then
    build='aarch64-apple-darwin'; impronta="$SHA_ARM"
  else
    build='x86_64-apple-darwin'; impronta="$SHA_INTEL"
  fi
  echo "STATO Python dello studio: lo scarico (circa 20 MB, una volta sola)"
  mkdir -p "$CASA" || non_pronto "non riesco a creare la cartella $CASA"
  parte="$CASA/python.tar.gz.parziale"
  nuovo="$CASA/python.nuovo"
  rm -rf "$parte" "$nuovo"
  url="$PY_FONTE/$PY_USCITA/cpython-$PY_VERSIONE%2B$PY_USCITA-$build-install_only.tar.gz"
  prova=1
  # un download che resta fermo 45 secondi si rifà da capo, 3 volte in tutto, con una riga ogni volta
  until curl -fsSL --connect-timeout 20 --speed-limit 1024 --speed-time 45 -o "$parte" "$url"; do
    rm -f "$parte"
    [ "$prova" -lt 3 ] || non_pronto "il download non arriva: controlla internet e riprova"
    prova=$((prova + 1))
    echo "STATO Python dello studio: il download si è fermato, riprovo ($prova di 3)"
    sleep 3
  done
  if [ "$(shasum -a 256 "$parte" | cut -d ' ' -f 1)" != "$impronta" ]; then
    rm -f "$parte"
    non_pronto "il file scaricato non è quello giusto (impronta diversa), quindi non l'ho usato: riprova più tardi"
  fi
  mkdir -p "$nuovo" && tar -xzf "$parte" -C "$nuovo"
  rm -f "$parte"
  va "$nuovo/python/bin/python3" || { rm -rf "$nuovo"; non_pronto "il Python scaricato non parte su questo Mac"; }
  rm -rf "$CASA/python"
  mv "$nuovo/python" "$CASA/python" && rm -rf "$nuovo"
  PY="$CASA/python/bin/python3"
  echo "STATO Python dello studio: OK · $PY_VERSIONE"
fi

exec "$PY" "$QUI/controllo.py" "$@"

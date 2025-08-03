#!/usr/bin/env bash
set -euxo pipefail

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="_diag_${STAMP}"
mkdir -p "${OUT_DIR}"/{tree,configs,deps,git,logs,ops,evidence}

# 0) Detectar stack e arquivos-chave
echo "=== DETECT ===" | tee "${OUT_DIR}/summary.txt"
ls -la | tee -a "${OUT_DIR}/summary.txt" || true
for f in .replit replit.nix nixpacks.toml package.json yarn.lock pnpm-lock.yaml \
         requirements.txt pyproject.toml poetry.lock Pipfile Pipfile.lock \
         go.mod go.sum Cargo.toml Cargo.lock Gemfile Gemfile.lock \
         composer.json composer.lock pom.xml build.gradle gradle.properties \
         Dockerfile docker-compose.yml Procfile fly.toml railway.json vercel.json \
         .env .env.* .gitignore Makefile Taskfile.yml README.md
do
  [[ -f "$f" ]] && echo "$f" >> "${OUT_DIR}/configs/_present_files.txt" || true
done

# 1) Árvore de arquivos (sanitizada)
if command -v tree >/dev/null 2>&1; then
  tree -a -I 'node_modules|.git|__pycache__|.venv|dist|build|.cache|.mypy_cache|.pytest_cache' > "${OUT_DIR}/tree/full_tree.txt" || true
else
  find . -path './.git' -prune -o -path './node_modules' -prune -o -print | sort > "${OUT_DIR}/tree/full_tree.txt" || true
fi
# Top 100 maiores arquivos
du -ah . 2>/dev/null | sort -hr | head -n 100 > "${OUT_DIR}/tree/top_100_files.txt" || true
# Alterados nos últimos 7 dias
find . -type f -mtime -7 -not -path './.git/*' -not -path './node_modules/*' | sort > "${OUT_DIR}/tree/changed_last_7d.txt" || true

# 2) Dependências
[[ -f package.json ]] && jq -r '.dependencies,.devDependencies' package.json > "${OUT_DIR}/deps/node_deps.json" || true
[[ -f requirements.txt ]] && cp requirements.txt "${OUT_DIR}/deps/requirements.txt" || true
[[ -f pyproject.toml ]] && cp pyproject.toml "${OUT_DIR}/deps/pyproject.toml" || true
[[ -f poetry.lock ]] && cp poetry.lock "${OUT_DIR}/deps/poetry.lock" || true
[[ -f go.mod ]] && cp go.mod "${OUT_DIR}/deps/go.mod" || true
[[ -f Cargo.toml ]] && cp Cargo.toml "${OUT_DIR}/deps/Cargo.toml" || true
[[ -f Gemfile ]] && cp Gemfile "${OUT_DIR}/deps/Gemfile" || true

# 3) Configs e infraestrutura
for f in .replit replit.nix nixpacks.toml Dockerfile docker-compose.yml Procfile vercel.json fly.toml railway.json \
         README.md Makefile Taskfile.yml .gitignore
do [[ -f "$f" ]] && cp "$f" "${OUT_DIR}/configs/" || true; done

# 4) Variáveis de ambiente (somente nomes, valores REDACTED)
env | sort | sed -E 's/=.*/=<REDACTED>/' > "${OUT_DIR}/ops/env_vars_redacted.txt"

# 5) Git (se houver)
if command -v git >/dev/null 2>&1 && [[ -d .git ]]; then
  git status -sb > "${OUT_DIR}/git/status.txt" || true
  git rev-parse --abbrev-ref HEAD > "${OUT_DIR}/git/branch.txt" || true
  git rev-parse --short HEAD > "${OUT_DIR}/git/commit.txt" || true
  git log --graph --decorate --abbrev-commit --date=iso \
    --pretty=format:'%h %ad %an %d %s' -n 30 > "${OUT_DIR}/git/log_last_30.txt" || true
  git remote -v | sed -E 's@(https?://|git@).*@<REDACTED_REMOTE>@' > "${OUT_DIR}/git/remotes_redacted.txt" || true
fi

# 6) Processos/portas (melhor esforço)
(ps aux || true) | head -n 200 > "${OUT_DIR}/ops/ps_aux.txt"
(command -v ss >/dev/null && ss -tulpen || true) > "${OUT_DIR}/ops/ports.txt"
(command -v lsof >/dev/null && lsof -i -P -n || true) > "${OUT_DIR}/ops/lsof.txt"

# 7) Coleta de logs (últimos 7 dias + tail)
# Heurística: *.log, *.out, *.err, pastas logs/
LOG_LIST="${OUT_DIR}/logs/_found_logs.txt"
find . \( -name "*.log" -o -name "*.out" -o -name "*.err" -o -path "*/logs/*" \) \
   -type f -not -path './.git/*' -not -path './node_modules/*' | sort | uniq > "${LOG_LIST}" || true

# Tail de cada log (até 1000 linhas) + agregados por mtime
: > "${OUT_DIR}/logs/tails_1000.txt"
while IFS= read -r f; do
  echo -e "\n===== FILE: $f =====" >> "${OUT_DIR}/logs/tails_1000.txt"
  (tail -n 1000 "$f" 2>/dev/null || head -n 1000 "$f" 2>/dev/null || true) >> "${OUT_DIR}/logs/tails_1000.txt"
done < "${LOG_LIST}"

# Logs recentes (modificados nos últimos 7 dias)
: > "${OUT_DIR}/logs/changed_logs_last_7d.txt"
find . \( -name "*.log" -o -name "*.out" -o -name "*.err" -o -path "*/logs/*" \) \
   -type f -mtime -7 -not -path './.git/*' -not -path './node_modules/*' -printf "%TY-%Tm-%Td %TH:%TM:%TS %p\n" \
   | sort -r > "${OUT_DIR}/logs/changed_logs_last_7d.txt" || true

# 8) Sumário curto
{
  echo "# Diagnostics Summary (${STAMP})"
  echo "## Key Files Present"
  cat "${OUT_DIR}/configs/_present_files.txt" 2>/dev/null || true
  echo -e "\n## Top 10 Largest Files"
  head -n 10 "${OUT_DIR}/tree/top_100_files.txt" 2>/dev/null || true
  echo -e "\n## Recent Changes (7d) – Files"
  head -n 50 "${OUT_DIR}/tree/changed_last_7d.txt" 2>/dev/null || true
  echo -e "\n## Recent Logs (7d) – Count"
  wc -l "${OUT_DIR}/logs/changed_logs_last_7d.txt" 2>/dev/null || true
} > "${OUT_DIR}/SUMMARY.md"

# 9) Empacotar
ARCHIVE="diagnostics_${STAMP}.tar.gz"
tar -czf "${ARCHIVE}" "${OUT_DIR}"

echo "✅ Bundle gerado: ${ARCHIVE}"
echo "👉 Conteúdo resumido em: ${OUT_DIR}/SUMMARY.md"

# Git Best Practices for SPEED Knowledge Graph Project

## ✅ What's Being Ignored

The `.gitignore` file prevents committing:

### 🔒 Secrets & Environment Variables
- ✅ `.env` files (backend and frontend)
- ✅ API keys and credentials
- ✅ Any file containing "secret" in the name

### 🐍 Python Files
- ✅ Virtual environments (`venv/`, `env/`)
- ✅ Python cache (`__pycache__/`, `*.pyc`)
- ✅ Distribution files (`dist/`, `build/`)
- ✅ Test coverage reports

### 📦 Node.js Files
- ✅ `node_modules/` directory
- ✅ Build output (`frontend/build/`)
- ✅ NPM logs

### 🗄️ Database & Data Files
- ✅ Neo4j data directories
- ✅ Database dumps (`.db`, `.sqlite`)
- ✅ Large CSV outputs (except examples)

### 📝 Logs & Temporary Files
- ✅ All `.log` files
- ✅ Temporary files (`.tmp`, `.bak`)
- ✅ Editor swap files

### 💻 IDE & OS Files
- ✅ `.vscode/`, `.idea/`
- ✅ `.DS_Store` (macOS)
- ✅ `Thumbs.db` (Windows)

## 🚀 Initial Setup

### First Time Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd Speed-Start

# Create your environment files from examples
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit .env files and add your secrets
# backend/.env: Add ANTHROPIC_API_KEY
# frontend/.env: Update API_URL if needed

# These .env files will NOT be committed
```

### Verify .env is Ignored

```bash
# Check git status
git status

# You should NOT see:
# - backend/.env
# - frontend/.env

# If you do see them, run:
git rm --cached backend/.env frontend/.env
git rm --cached .env
```

## 📋 Commit Guidelines

### What TO Commit

✅ **Source Code**
- Python files (`.py`)
- JavaScript/React files (`.js`, `.jsx`)
- Configuration templates (`.env.example`)
- Documentation (`.md`)

✅ **Configuration**
- Docker files (`Dockerfile`, `docker-compose.yml`)
- Package files (`requirements.txt`, `package.json`)
- `.gitignore` itself

✅ **Small Data Files**
- Example queries
- Schema files
- Sample data (if < 10MB)

### What NOT TO Commit

❌ **Never Commit:**
- `.env` files with real secrets
- API keys (Anthropic, OpenAI, etc.)
- Database passwords
- `node_modules/` directory
- Virtual environments (`venv/`)
- Build outputs
- Large data files (> 10MB)
- Personal IDE settings
- Operating system files

## 🔧 Common Git Commands

### Check What Will Be Committed

```bash
# See status
git status

# See changes
git diff

# See what's ignored
git status --ignored
```

### Adding Files

```bash
# Add specific files
git add backend/main.py

# Add all Python files in backend
git add backend/*.py

# Add all changes (be careful!)
git add .

# Interactive add (recommended)
git add -p
```

### Committing

```bash
# Commit with message
git commit -m "Add planning agent implementation"

# Better: Multi-line commit message
git commit -m "Add planning agent with Claude integration

- Implements query intent analysis
- Extracts parameters from natural language
- Returns structured execution plan
- Includes fallback for JSON parse errors"
```

### Branches

```bash
# Create and switch to new branch
git checkout -b feature/add-choropleth-map

# List branches
git branch

# Switch branches
git checkout main

# Delete branch
git branch -d feature/old-feature
```

## 🛡️ Security Checklist

Before every commit:

- [ ] Check `git status` for `.env` files
- [ ] Search for hardcoded API keys: `git grep -i "sk-ant"`
- [ ] Verify no passwords in code: `git grep -i "password.*="`
- [ ] Check for TODO comments with secrets
- [ ] Review `git diff` before committing

### If You Accidentally Commit Secrets

```bash
# Remove from most recent commit (not pushed yet)
git reset HEAD~1
git add <correct files>
git commit -m "Your message"

# Remove file from git but keep locally
git rm --cached backend/.env
git commit -m "Remove .env from tracking"

# If already pushed - YOU MUST:
# 1. Rotate all secrets/API keys immediately
# 2. Use git filter-branch or BFG Repo-Cleaner
# 3. Force push (dangerous)
```

## 📁 Recommended Commit Structure

### Good Commit Messages

```bash
# Format: <type>: <subject>

# Examples:
git commit -m "feat: Add network graph visualization"
git commit -m "fix: Handle empty query results in execution agent"
git commit -m "docs: Update README with Docker instructions"
git commit -m "refactor: Extract data transformation to separate module"
git commit -m "test: Add unit tests for planning agent"
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting)
- `refactor`: Code restructure
- `test`: Tests
- `chore`: Maintenance

## 🌿 Branch Strategy

### Main Branches

- `main` - Production-ready code
- `develop` - Development branch

### Feature Branches

```bash
# Create feature branch
git checkout -b feature/actor-network-viz

# Work on feature
git add ...
git commit -m "feat: Implement actor network visualization"

# Push to remote
git push -u origin feature/actor-network-viz

# Create Pull Request on GitHub
# After merge, delete branch
git checkout main
git pull
git branch -d feature/actor-network-viz
```

## 🔄 Syncing with Remote

```bash
# Pull latest changes
git pull origin main

# Push your changes
git push origin main

# Push new branch
git push -u origin feature/my-feature

# Force push (DANGEROUS - only if necessary)
git push --force origin main
```

## 📊 Large Files Management

For files > 10MB:

### Option 1: Don't Commit Them
```bash
# Add to .gitignore
echo "data/large_dataset.csv" >> .gitignore
git add .gitignore
git commit -m "chore: Ignore large dataset"
```

### Option 2: Use Git LFS (Large File Storage)
```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.csv"
git lfs track "data/*.parquet"

# Commit .gitattributes
git add .gitattributes
git commit -m "chore: Add Git LFS for large files"
```

## 🧹 Cleaning Up

### Remove Untracked Files

```bash
# See what would be removed
git clean -n

# Remove untracked files
git clean -f

# Remove untracked files and directories
git clean -fd
```

### Remove Ignored Files

```bash
# Remove all ignored files (like node_modules)
git clean -fX
```

## 🔍 Useful Commands

### Search History

```bash
# Search commits for a term
git log --grep="planning agent"

# Search code history
git log -S "ANTHROPIC_API_KEY"

# See file history
git log --follow backend/agents/planning_agent.py
```

### View Changes

```bash
# Compare branches
git diff main..develop

# Compare with remote
git diff origin/main

# Show specific commit
git show <commit-hash>
```

## 🚨 Emergency Commands

### Undo Last Commit (Not Pushed)

```bash
# Keep changes
git reset --soft HEAD~1

# Discard changes
git reset --hard HEAD~1
```

### Undo Pushed Commit

```bash
# Create reverse commit
git revert HEAD
git push
```

### Recover Deleted File

```bash
# Find commit where file was deleted
git rev-list -n 1 HEAD -- <file>

# Restore it
git checkout <commit>^ -- <file>
```

## 📝 .gitignore Testing

```bash
# Check if file is ignored
git check-ignore -v backend/.env

# List all ignored files
git status --ignored
```

## 🎯 Quick Reference

```bash
# Daily workflow
git status                      # Check status
git add <files>                 # Stage changes
git commit -m "message"         # Commit
git push                        # Push to remote

# Feature workflow
git checkout -b feature/name    # Create branch
# ... make changes ...
git add .                       # Stage all
git commit -m "feat: ..."       # Commit
git push -u origin feature/name # Push branch

# Before committing
git status                      # Check status
git diff                        # Review changes
grep -r "TODO.*secret" .        # Check for secrets
git commit                      # Commit
```

## ✅ Checklist Before First Commit

- [ ] `.gitignore` file exists
- [ ] `.env` files are in `.gitignore`
- [ ] Created `.env` from `.env.example`
- [ ] No secrets in code
- [ ] No `node_modules/` committed
- [ ] No `venv/` committed
- [ ] Documentation is up to date
- [ ] Commit message is clear

## 📚 Resources

- [Git Documentation](https://git-scm.com/doc)
- [Gitignore Templates](https://github.com/github/gitignore)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Best Practices](https://git-scm.com/book/en/v2)

---

**Remember:** Never commit secrets. When in doubt, don't commit it. You can always add files later, but removing sensitive data from history is difficult and dangerous.

# 🧪 Blockly YAML Editor - Przewodnik Testowania i Rozwoju

## 📋 Checklist: Pierwsze Kroki

### 1. Weryfikacja Instalacji
```bash
# ✅ Sprawdź czy wszystkie moduły są zainstalowane
python3 -c "import flask, yaml, flask_cors; print('✓ All modules OK')"

# ✅ Sprawdź wersje
python3 -c "import flask; print(f'Flask: {flask.__version__}')"
python3 -c "import yaml; print(f'PyYAML: {yaml.__version__}')"

# ✅ Sprawdź czy skrypt jest wykonywalny
ls -la blocked.py | grep x

# ✅ Sprawdź czy katalog backupów istnieje
ls -la .blocked/
```

### 2. Test Podstawowy
```bash
# ✅ Utwórz testowy plik YAML
cat > test.yaml << 'EOF'
version: "3.8"
services:
  test:
    image: nginx
EOF

# ✅ Uruchom edytor
./blocked.py test.yaml --no-browser

# ✅ Sprawdź czy serwer działa
curl http://localhost:5000
```

## 🔬 Testy Funkcjonalne

### Test 1: Tworzenie Nowego Pliku
```bash
# Prompt 1: Test tworzenia nowego pliku
echo "TEST 1: Creating new file"
./blocked.py new-compose.yaml
# Oczekiwany rezultat: 
# - Edytor otwiera się z pustym workspace
# - Można dodawać bloki
# - Plik zostaje utworzony po zapisie
```

### Test 2: Edycja Istniejącego Docker Compose
```bash
# Prompt 2: Test edycji docker-compose
echo "TEST 2: Editing existing docker-compose.yml"
./blocked.py docker-compose.yml
# W przeglądarce:
# 1. Przeciągnij blok "Service" 
# 2. Nazwij go "web"
# 3. Dodaj blok "Image" -> nginx:latest
# 4. Dodaj blok "Ports" -> 80:80
# 5. Kliknij "Generate YAML"
# 6. Sprawdź preview
# 7. Kliknij "Save"
```

### Test 3: Auto-Save
```bash
# Prompt 3: Test auto-save
echo "TEST 3: Testing auto-save feature"
./blocked.py test-autosave.yaml
# W przeglądarce:
# 1. Dodaj dowolny blok
# 2. Czekaj 10 sekund
# 3. Sprawdź w terminalu czy pojawi się "Auto-saved"
# 4. Sprawdź timestamp pliku:
ls -la test-autosave.yaml
```

### Test 4: System Backupów
```bash
# Prompt 4: Test backup system
echo "TEST 4: Testing backup system"
# Utwórz plik testowy
echo "original: content" > backup-test.yaml

# Otwórz w edytorze
./blocked.py backup-test.yaml --no-browser &
PID=$!
sleep 2
kill $PID

# Sprawdź czy backup został utworzony
ls -la .blocked/backup-test.yaml.*

# Porównaj pliki
diff backup-test.yaml .blocked/backup-test.yaml.*
```

### Test 5: Walidacja YAML
```bash
# Prompt 5: Test YAML validation
echo "TEST 5: Testing YAML validation"
# Utwórz niepoprawny YAML
cat > invalid.yaml << 'EOF'
services:
  web:
    image: nginx
    ports:
      - 80:80
    invalid_indent:
   wrong
EOF

./blocked.py invalid.yaml
# Oczekiwany rezultat: Error w preview panel
```

### Test 6: Docker Integration
```bash
# Prompt 6: Test Docker integration
echo "TEST 6: Testing Docker features"
./blocked.py docker-compose.yml
# W przeglądarce:
# 1. Kliknij "Test Docker"
# 2. Powinien wykonać: docker-compose config
# 3. Sprawdź rezultat w preview
```

## 🚀 Testy Zaawansowane

### Test 7: Różne Typy Plików
```bash
# Prompt 7: Test różnych typów plików
echo "TEST 7: Testing different file types"

# Test Dockerfile
echo "FROM nginx" > Dockerfile
./blocked.py Dockerfile
# Sprawdź czy pojawiły się bloki Dockerfile

# Test zwykły YAML
cat > config.yaml << 'EOF'
database:
  host: localhost
  port: 5432
EOF
./blocked.py config.yaml
# Sprawdź czy pojawiły się bloki YAML
```

### Test 8: Port Conflicts
```bash
# Prompt 8: Test konfliktów portów
echo "TEST 8: Testing port conflicts"

# Uruchom pierwszą instancję
./blocked.py file1.yaml --port 5000 &
PID1=$!

# Spróbuj uruchomić drugą na tym samym porcie
./blocked.py file2.yaml --port 5000
# Oczekiwany błąd: Port already in use

# Uruchom na innym porcie
./blocked.py file2.yaml --port 5001 &
PID2=$!

# Cleanup
kill $PID1 $PID2 2>/dev/null
```

### Test 9: Stress Test
```bash
# Prompt 9: Stress test - duży plik
echo "TEST 9: Stress testing with large file"

# Generuj duży docker-compose
cat > large-compose.yaml << 'EOF'
version: "3.8"
services:
EOF

for i in {1..20}; do
  cat >> large-compose.yaml << EOF
  service_$i:
    image: nginx:latest
    ports:
      - "80$i:80"
    environment:
      - ENV_VAR_$i=value_$i
    volumes:
      - ./data_$i:/data
    networks:
      - network_$i
EOF
done

# Otwórz w edytorze
./blocked.py large-compose.yaml
# Sprawdź wydajność i responsywność
```

## 🐛 Testy Debugowania

### Test 10: Error Handling
```bash
# Prompt 10: Test obsługi błędów
echo "TEST 10: Error handling"

# Test nieistniejącego pliku (read-only)
touch readonly.yaml
chmod 444 readonly.yaml
./blocked.py readonly.yaml
# Spróbuj zapisać - powinien pokazać błąd

# Test z brakiem uprawnień do katalogu
mkdir -p restricted/.blocked
chmod 000 restricted/.blocked
cd restricted
../blocked.py test.yaml
# Powinien obsłużyć brak dostępu do .blocked
```

## 🔄 Testy Integracyjne

### Test 11: Full Workflow
```bash
# Prompt 11: Pełny workflow
echo "TEST 11: Complete workflow test"

# 1. Utwórz projekt
mkdir test-project
cd test-project

# 2. Utwórz docker-compose z edytorem
../blocked.py docker-compose.yaml
# Dodaj: service (db), image (postgres), ports (5432:5432)

# 3. Utwórz Dockerfile
../blocked.py Dockerfile  
# Dodaj: FROM, RUN, COPY, CMD blocks

# 4. Sprawdź backupy
ls -la .blocked/

# 5. Testuj z Dockerem
docker-compose config
docker build -f Dockerfile .
```

## 📊 Testy Wydajności

### Test 12: Performance Monitoring
```bash
# Prompt 12: Monitoring wydajności
echo "TEST 12: Performance monitoring"

# Monitoruj zużycie zasobów
./blocked.py docker-compose.yml &
PID=$!

# W osobnym terminalu
while kill -0 $PID 2>/dev/null; do
  ps aux | grep $PID | grep -v grep
  sleep 2
done
```

## 🔍 Testy Bezpieczeństwa

### Test 13: Security Checks
```bash
# Prompt 13: Testy bezpieczeństwa
echo "TEST 13: Security testing"

# Test XSS w nazwach bloków
./blocked.py xss-test.yaml
# W edytorze spróbuj nazwać blok: <script>alert('XSS')</script>

# Test path traversal
./blocked.py ../../etc/passwd
# Powinien obsłużyć bezpiecznie

# Test symbolic links
ln -s /etc/passwd symlink.yaml
./blocked.py symlink.yaml
# Powinien obsłużyć poprawnie
```

## 🎨 Testy UI/UX

### Test 14: Browser Compatibility
```bash
# Prompt 14: Test kompatybilności przeglądarek
echo "TEST 14: Browser compatibility"

# Testuj w różnych przeglądarkach
./blocked.py test.yaml

# Otwórz ręcznie w:
# - Chrome: http://localhost:5000
# - Firefox: http://localhost:5000
# - Safari: http://localhost:5000
# - Edge: http://localhost:5000

# Sprawdź:
# ✓ Blockly się ładuje
# ✓ Drag & drop działa
# ✓ Preview się aktualizuje
# ✓ Przyciski działają
```

## 📈 Metryki do Sprawdzenia

### Checklist Końcowy
```markdown
## ✅ Functionality Tests
- [ ] Edytor się otwiera
- [ ] Bloki można przeciągać
- [ ] YAML się generuje
- [ ] Zapis działa
- [ ] Auto-save działa
- [ ] Backupy są tworzone
- [ ] Walidacja YAML działa
- [ ] Docker test działa (jeśli Docker zainstalowany)

## ✅ Performance Tests  
- [ ] Czas ładowania < 3s
- [ ] Responsywność UI płynna
- [ ] Auto-save nie blokuje UI
- [ ] Duże pliki (>100 linii) działają

## ✅ Error Handling
- [ ] Brak uprawnień - graceful error
- [ ] Niepoprawny YAML - pokazuje błąd
- [ ] Port zajęty - informuje użytkownika
- [ ] Brak modułów - czytelny komunikat

## ✅ User Experience
- [ ] Intuicyjny interface
- [ ] Preview na żywo
- [ ] Status zapisu widoczny
- [ ] Błędy są zrozumiałe
```

## 🚧 Rozwój - Co Dalej?

### Prompt 15: Dodawanie nowych features
```bash
# Sugestie rozwoju:

# 1. Dodaj wsparcie dla Kubernetes
echo "TODO: Add k8s.yaml support with specific blocks"

# 2. Dodaj eksport/import workspace
echo "TODO: Save/load Blockly workspace as JSON"

# 3. Dodaj syntax highlighting w preview
echo "TODO: Use highlight.js for YAML preview"

# 4. Dodaj collaborative editing
echo "TODO: WebSocket support for real-time collaboration"

# 5. Dodaj templates
echo "TODO: Pre-built templates for common configs"
```

## 🔧 Troubleshooting

### Częste Problemy i Rozwiązania
```bash
# Problem: ModuleNotFoundError
# Rozwiązanie:
pip3 install flask flask-cors pyyaml

# Problem: Port already in use
# Rozwiązanie:
lsof -i :5000
kill -9 <PID>
# lub użyj innego portu:
./blocked.py file.yaml --port 8080

# Problem: Browser nie otwiera się
# Rozwiązanie:
./blocked.py file.yaml --no-browser
# Otwórz ręcznie: http://localhost:5000

# Problem: Permission denied
# Rozwiązanie:
chmod +x blocked.py
chmod +x blocked

# Problem: Docker test nie działa
# Rozwiązanie:
# Sprawdź czy Docker jest uruchomiony:
docker info
systemctl start docker  # Linux
open -a Docker  # macOS
```

## 📝 Raport z Testów

### Template raportu
```markdown
## Test Report - Blockly YAML Editor
Date: [DATE]
Version: 1.0.0
Tester: [NAME]

### Environment
- OS: [Linux/macOS/Windows]
- Python: [version]
- Browser: [Chrome/Firefox/Safari]
- Docker: [yes/no, version]

### Test Results
| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | New File Creation | ✅/❌ | |
| 2 | Docker Compose Edit | ✅/❌ | |
| 3 | Auto-Save | ✅/❌ | |
| 4 | Backup System | ✅/❌ | |
| 5 | YAML Validation | ✅/❌ | |
| 6 | Docker Integration | ✅/❌ | |
| 7 | File Types | ✅/❌ | |
| 8 | Port Conflicts | ✅/❌ | |
| 9 | Stress Test | ✅/❌ | |
| 10 | Error Handling | ✅/❌ | |

### Issues Found
1. [Issue description]
2. [Issue description]

### Recommendations
1. [Recommendation]
2. [Recommendation]
```

## 🎯 Podsumowanie

Wykonaj testy w kolejności:
1. **Podstawowe** (1-6) - sprawdzają core functionality
2. **Zaawansowane** (7-11) - sprawdzają edge cases
3. **Wydajnościowe** (12) - sprawdzają performance
4. **Bezpieczeństwa** (13) - sprawdzają security
5. **UI/UX** (14) - sprawdzają user experience

Po zakończeniu testów, wypełnij raport i zdecyduj o dalszym rozwoju! 🚀
#!/bin/bash

# Interactive Testing Guide for Blockly YAML Editor
# This script guides you through manual testing with prompts

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Test tracking
declare -A TEST_STATUS
CURRENT_TEST=0
TOTAL_TESTS=15

# Functions
header() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║     Blockly YAML Editor - Interactive Test Guide      ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

prompt() {
    echo -e "${YELLOW}➤${NC} $1"
}

info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

wait_for_key() {
    echo ""
    echo -e "${MAGENTA}Press ENTER to continue...${NC}"
    read -r
}

ask_result() {
    echo ""
    echo -e "${YELLOW}Did the test pass? (y/n/s for skip):${NC}"
    read -n 1 -r response
    echo ""
    case $response in
        [Yy])
            TEST_STATUS[$1]="PASS"
            success "Test $1 marked as PASSED"
            ;;
        [Nn])
            TEST_STATUS[$1]="FAIL"
            error "Test $1 marked as FAILED"
            echo -e "${YELLOW}Please describe the issue:${NC}"
            read -r issue_description
            TEST_STATUS["$1_notes"]="$issue_description"
            ;;
        [Ss])
            TEST_STATUS[$1]="SKIP"
            info "Test $1 SKIPPED"
            ;;
        *)
            TEST_STATUS[$1]="UNKNOWN"
            ;;
    esac
}

# Test functions
test_installation() {
    header
    echo -e "${CYAN}TEST 1: Installation Verification${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    prompt "Let's verify the installation is complete."
    echo ""

    info "Checking Python version..."
    python3 --version

    info "Checking required modules..."
    python3 -c "
import sys
try:
    import flask
    print('✓ Flask installed:', flask.__version__)
except ImportError:
    print('✗ Flask NOT installed')
    sys.exit(1)

try:
    import yaml
    print('✓ PyYAML installed:', yaml.__version__)
except ImportError:
    print('✗ PyYAML NOT installed')
    sys.exit(1)

try:
    import flask_cors
    print('✓ Flask-CORS installed')
except ImportError:
    print('✗ Flask-CORS NOT installed')
    sys.exit(1)
"

    info "Checking file permissions..."
    ls -la blocked.py 2>/dev/null || ls -la blockly-yaml-editor.py

    ask_result "installation"
    wait_for_key
}

test_basic_startup() {
    header
    echo -e "${CYAN}TEST 2: Basic Startup${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    prompt "We'll test if the editor starts correctly."
    echo ""

    info "Creating a test file..."
    cat > test-startup.yaml << 'EOF'
version: "3.8"
services:
  test:
    image: nginx
EOF

    echo ""
    prompt "Starting the editor..."
    prompt "Run this command in a NEW terminal:"
    echo ""
    echo -e "${GREEN}./blocked.py test-startup.yaml${NC}"
    echo ""
    info "The browser should open automatically"
    info "You should see:"
    echo "  1. Blockly workspace on the left"
    echo "  2. YAML preview on the right"
    echo "  3. The test file content in preview"

    ask_result "basic_startup"
    wait_for_key
}

test_drag_drop() {
    header
    echo -e "${CYAN}TEST 3: Drag and Drop Blocks${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    prompt "Test the drag and drop functionality:"
    echo ""
    info "In the browser with editor open:"
    echo "  1. Click on 'Docker Compose' category (left side)"
    echo "  2. Drag 'Service' block to workspace"
    echo "  3. Change service name to 'webapp'"
    echo "  4. Drag 'Image' block inside the Service block"
    echo "  5. Set image to 'node:16-alpine'"
    echo ""
    info "The preview should update automatically"

    ask_result "drag_drop"
    wait_for_key
}

test_yaml_generation() {
    header
    echo -e "${CYAN}TEST 4: YAML Generation${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    prompt "Test YAML generation from blocks:"
    echo ""
    info "With blocks in workspace:"
    echo "  1. Click 'Generate YAML' button"
    echo "  2. Check the preview panel"
    echo ""
    prompt "Expected result in preview:"
    echo -e "${GREEN}version: \"3.8\"
services:
  webapp:
    image: node:16-alpine${NC}"

    ask_result "yaml_generation"
    wait_for_key
}

test_save_functionality() {
    header
    echo -e "${CYAN}TEST 5: Save Functionality${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    prompt "Test file saving:"
    echo ""
    info "In the editor:"
    echo "  1. Click 'Save File' button"
    echo "  2. You should see '✓ Saved' status"
    echo ""
    info "In terminal, check if file was updated:"
    echo ""

    cat test-startup.yaml

    echo ""
    prompt "Does the file contain your changes?"

    ask_result "save_functionality"
    wait_for_key
}

test_auto_save() {
    header
    echo -e "${CYAN}TEST 6: Auto-Save Feature${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    prompt "Test automatic saving:"
    echo ""
    info "In the editor:"
    echo "  1. Make any change (add/move a block)"
    echo "  2. Wait 10-15 seconds"
    echo "  3. Look for '✓ Auto-saved' message"
    echo ""
    info "Check terminal for auto-save messages"

    ask_result "auto_save"
    wait_for_key
}

test_backup_system() {
    header
    echo -e "${CYAN}TEST 7: Backup System${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    prompt "Test backup creation:"
    echo ""

    info "Creating new file for backup test..."
    echo "original: content" > backup-test.yaml

    info "Open in editor (new terminal):"
    echo -e "${GREEN}./blocked.py backup-test.yaml${NC}"
    echo ""

    info "After editor opens, close it (Ctrl+C in terminal)"
    wait_for_key

    info "Checking for backups..."
    ls -la .blocked/backup-test.yaml.* 2>/dev/null

    if ls .blocked/backup-test.yaml.* &>/dev/null; then
        success "Backup found!"
    else
        error "No backup found"
    fi

    ask_result "backup_system"
    wait_for_key
}

test_dockerfile_support() {
    header
    echo -e "${CYAN}TEST 8: Dockerfile Support${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    prompt "Test Dockerfile editing:"
    echo ""

    info "Creating a Dockerfile..."
    cat > Dockerfile << 'EOF'
FROM node:16-alpine
WORKDIR /app
COPY . .
RUN npm install
CMD ["npm", "start"]
EOF

    info "Open Dockerfile in editor:"
    echo -e "${GREEN}./blocked.py Dockerfile${NC}"
    echo ""

    prompt "You should see:"
    echo "  - Different blocks (Dockerfile category)"
    echo "  - FROM, RUN, COPY, CMD blocks available"
    echo "  - Dockerfile content in preview"

    ask_result "dockerfile_support"
    wait_for_key
}

test_validation() {
    header
    echo -e "${CYAN}TEST 9: YAML Validation${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    prompt "Test YAML validation:"
    echo ""

    info "Create invalid YAML for testing..."
    cat > invalid.yaml << 'EOF'
services:
  web:
    image: nginx
  invalid_indent:
 wrong_indent
EOF

    info "Open in editor:"
    echo -e "${GREEN}./blocked.py invalid.yaml${NC}"
    echo ""

    prompt "You should see:"
    echo "  - Error message in preview panel"
    echo "  - YAML validation error details"

    ask_result "validation"
    wait_for_key
}

test_docker_integration() {
    header
    echo -e "${CYAN}TEST 10: Docker Integration${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    if ! command -v docker &>/dev/null; then
        info "Docker not installed - skipping test"
        TEST_STATUS["docker_integration"]="SKIP"
        wait_for_key
        return
    fi

    prompt "Test Docker integration:"
    echo ""

    info "Create valid docker-compose.yaml:"
    cat > docker-compose.yaml << 'EOF'
version: "3.8"
services:
  web:
    image: nginx:latest
    ports:
      - "8080:80"
EOF

    info "Open in editor:"
    echo -e "${GREEN}./blocked.py docker-compose.yaml${NC}"
    echo ""

    prompt "Click 'Test Docker' button"
    echo "  - Should validate the configuration"
    echo "  - Show result in preview/alert"

    ask_result "docker_integration"
    wait_for_key
}

test_multiple_ports() {
    header
    echo -e "${CYAN}TEST 11: Multiple Instances (Different Ports)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    prompt "Test running multiple instances:"
    echo ""

    info "Open 3 terminals and run:"
    echo ""
    echo "Terminal 1:"
    echo -e "${GREEN}./blocked.py file1.yaml --port 5001${NC}"
    echo ""
    echo "Terminal 2:"
    echo -e "${GREEN}./blocked.py file2.yaml --port 5002${NC}"
    echo ""
    echo "Terminal 3:"
    echo -e "${GREEN}./blocked.py file3.yaml --port 5003${NC}"
    echo ""

    prompt "All three should work simultaneously"

    ask_result "multiple_ports"
    wait_for_key
}

test_large_file() {
    header
    echo -e "${CYAN}TEST 12: Large File Handling${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    prompt "Test with large file:"
    echo ""

    info "Creating large docker-compose.yaml..."
    cat > large-compose.yaml << 'EOF'
version: "3.8"
services:
EOF

    for i in {1..30}; do
        cat >> large-compose.yaml << EOF
  service_$i:
    image: nginx:latest
    container_name: service_$i
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

    info "File created with 30 services"
    echo ""

    info "Open large file:"
    echo -e "${GREEN}./blocked.py large-compose.yaml${NC}"
    echo ""

    prompt "Check:"
    echo "  - Editor loads without issues"
    echo "  - Preview shows all content"
    echo "  - Performance is acceptable"

    ask_result "large_file"
    wait_for_key
}

test_browser_compatibility() {
    header
    echo -e "${CYAN}TEST 13: Browser Compatibility${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    prompt "Test in different browsers:"
    echo ""

    info "Start the editor:"
    echo -e "${GREEN}./blocked.py test.yaml --no-browser${NC}"
    echo ""

    info "Manually open in different browsers:"
    echo "  - Chrome:  http://localhost:5000"
    echo "  - Firefox: http://localhost:5000"
    echo "  - Safari:  http://localhost:5000"
    echo "  - Edge:    http://localhost:5000"
    echo ""

    prompt "Test in each browser:"
    echo "  ✓ Blockly loads correctly"
    echo "  ✓ Drag and drop works"
    echo "  ✓ Preview updates"
    echo "  ✓ Buttons work"

    ask_result "browser_compatibility"
    wait_for_key
}

test_error_recovery() {
    header
    echo -e "${CYAN}TEST 14: Error Recovery${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    prompt "Test error handling:"
    echo ""

    info "Test 1: Read-only file"
    touch readonly.yaml
    chmod 444 readonly.yaml
    echo ""
    echo -e "${GREEN}./blocked.py readonly.yaml${NC}"
    echo "Try to save - should show error"
    echo ""

    info "Test 2: Port already in use"
    echo "Start two instances on same port:"
    echo -e "${GREEN}./blocked.py test1.yaml --port 5000${NC}"
    echo -e "${GREEN}./blocked.py test2.yaml --port 5000${NC}"
    echo "Second should fail gracefully"

    ask_result "error_recovery"

    # Cleanup
    chmod 644 readonly.yaml
    rm readonly.yaml
    wait_for_key
}

test_restore_backup() {
    header
    echo -e "${CYAN}TEST 15: Restore from Backup${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    prompt "Test backup restoration:"
    echo ""

    info "You should have backups from previous tests"
    ls -la .blocked/*.yaml.* 2>/dev/null | head -5
    echo ""

    info "In editor with any file open:"
    echo "  1. Click 'Load Backup' button"
    echo "  2. Select a backup from list"
    echo "  3. File should be restored"
    echo "  4. Page should reload with backup content"

    ask_result "restore_backup"
    wait_for_key
}

# Generate final report
generate_final_report() {
    header
    echo -e "${CYAN}TEST RESULTS SUMMARY${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    local passed=0
    local failed=0
    local skipped=0

    # Count results
    for test in "${!TEST_STATUS[@]}"; do
        if [[ ! "$test" == *"_notes" ]]; then
            case "${TEST_STATUS[$test]}" in
                PASS) ((passed++)) ;;
                FAIL) ((failed++)) ;;
                SKIP) ((skipped++)) ;;
            esac
        fi
    done

    # Display summary
    echo -e "${GREEN}Passed:${NC} $passed"
    echo -e "${RED}Failed:${NC} $failed"
    echo -e "${YELLOW}Skipped:${NC} $skipped"
    echo ""

    # Detailed results
    echo "Detailed Results:"
    echo "─────────────────"

    local test_names=(
        "installation:Installation Verification"
        "basic_startup:Basic Startup"
        "drag_drop:Drag and Drop"
        "yaml_generation:YAML Generation"
        "save_functionality:Save Functionality"
        "auto_save:Auto-Save"
        "backup_system:Backup System"
        "dockerfile_support:Dockerfile Support"
        "validation:YAML Validation"
        "docker_integration:Docker Integration"
        "multiple_ports:Multiple Instances"
        "large_file:Large File Handling"
        "browser_compatibility:Browser Compatibility"
        "error_recovery:Error Recovery"
        "restore_backup:Restore Backup"
    )

    for test_pair in "${test_names[@]}"; do
        IFS=':' read -r key name <<< "$test_pair"
        local status="${TEST_STATUS[$key]:-NOT_RUN}"

        case "$status" in
            PASS) echo -e "${GREEN}✓${NC} $name" ;;
            FAIL)
                echo -e "${RED}✗${NC} $name"
                if [[ -n "${TEST_STATUS[${key}_notes]}" ]]; then
                    echo "  └─ Issue: ${TEST_STATUS[${key}_notes]}"
                fi
                ;;
            SKIP) echo -e "${YELLOW}⊘${NC} $name (skipped)" ;;
            *) echo -e "  $name (not tested)" ;;
        esac
    done

    # Save report to file
    local report_file="interactive_test_report_$(date +%Y%m%d_%H%M%S).txt"
    {
        echo "Blockly YAML Editor - Interactive Test Report"
        echo "Date: $(date)"
        echo ""
        echo "Results: Passed=$passed Failed=$failed Skipped=$skipped"
        echo ""
        for test_pair in "${test_names[@]}"; do
            IFS=':' read -r key name <<< "$test_pair"
            echo "$name: ${TEST_STATUS[$key]:-NOT_RUN}"
            if [[ -n "${TEST_STATUS[${key}_notes]}" ]]; then
                echo "  Notes: ${TEST_STATUS[${key}_notes]}"
            fi
        done
    } > "$report_file"

    echo ""
    success "Report saved to: $report_file"

    # Final message
    echo ""
    if [[ $failed -eq 0 ]]; then
        echo -e "${GREEN}┌────────────────────────────────────┐${NC}"
        echo -e "${GREEN}│   All tests passed successfully!  │${NC}"
        echo -e "${GREEN}│   System is ready for production  │${NC}"
        echo -e "${GREEN}└────────────────────────────────────┘${NC}"
    else
        echo -e "${YELLOW}┌────────────────────────────────────┐${NC}"
        echo -e "${YELLOW}│  Some tests failed - review needed │${NC}"
        echo -e "${YELLOW}└────────────────────────────────────┘${NC}"
    fi
}

# Main menu
show_menu() {
    header
    echo -e "${CYAN}Select Testing Mode:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1) Run all tests sequentially"
    echo "2) Run specific test"
    echo "3) Quick test (essential tests only)"
    echo "4) Generate report from previous tests"
    echo "5) Exit"
    echo ""
    echo -n "Enter choice [1-5]: "
}

# Main execution
main() {
    while true; do
        show_menu
        read -r choice

        case $choice in
            1)
                # Run all tests
                test_installation
                test_basic_startup
                test_drag_drop
                test_yaml_generation
                test_save_functionality
                test_auto_save
                test_backup_system
                test_dockerfile_support
                test_validation
                test_docker_integration
                test_multiple_ports
                test_large_file
                test_browser_compatibility
                test_error_recovery
                test_restore_backup
                generate_final_report
                wait_for_key
                ;;
            2)
                # Run specific test
                header
                echo "Available tests:"
                echo "1) Installation    2) Startup       3) Drag&Drop"
                echo "4) YAML Gen       5) Save          6) Auto-Save"
                echo "7) Backup         8) Dockerfile    9) Validation"
                echo "10) Docker        11) Multi-Port   12) Large File"
                echo "13) Browser       14) Errors       15) Restore"
                echo ""
                echo -n "Enter test number: "
                read -r test_num

                case $test_num in
                    1) test_installation ;;
                    2) test_basic_startup ;;
                    3) test_drag_drop ;;
                    4) test_yaml_generation ;;
                    5) test_save_functionality ;;
                    6) test_auto_save ;;
                    7) test_backup_system ;;
                    8) test_dockerfile_support ;;
                    9) test_validation ;;
                    10) test_docker_integration ;;
                    11) test_multiple_ports ;;
                    12) test_large_file ;;
                    13) test_browser_compatibility ;;
                    14) test_error_recovery ;;
                    15) test_restore_backup ;;
                    *) error "Invalid test number" ;;
                esac
                wait_for_key
                ;;
            3)
                # Quick test
                test_installation
                test_basic_startup
                test_drag_drop
                test_save_functionality
                test_backup_system
                generate_final_report
                wait_for_key
                ;;
            4)
                # Generate report
                generate_final_report
                wait_for_key
                ;;
            5)
                # Exit
                echo "Exiting..."
                exit 0
                ;;
            *)
                error "Invalid choice"
                wait_for_key
                ;;
        esac
    done
}

# Start the interactive test guide
main
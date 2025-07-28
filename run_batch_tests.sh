#!/bin/bash

# Batch testing script for vLLM configurations
# This script loops through all config files and runs tests with organized output directories

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to extract components from config path and generate output directory
generate_output_dir() {
    local config_path="$1"
    
    # Extract components from path: model_configs/vllm-version/instance-type/model-config.yaml
    local vllm_version=$(echo "$config_path" | cut -d'/' -f2)
    local instance_type=$(echo "$config_path" | cut -d'/' -f3)
    local config_file=$(basename "$config_path" .yaml)
    
    # Generate output directory in the format: archive_results/vllm-version--instance-type--model-config
    echo "archive_results/${vllm_version}--${instance_type}--${config_file}"
}

# Function to run test for a single config
run_single_test() {
    local config_path="$1"
    local output_dir="$2"
    
    print_status "Running test for: $config_path"
    print_status "Output directory: $output_dir"
    
    # Run the test
    if uv run run_auto_test.py --config "$config_path" --output-dir "$output_dir"; then
        print_success "Test completed successfully for $config_path"
        return 0
    else
        print_error "Test failed for $config_path"
        return 1
    fi
}

# Main function
main() {
    local config_dir="model_configs"
    local failed_tests=()
    local successful_tests=()
    local total_tests=0
    
    print_status "Starting batch testing for vLLM configurations"
    print_status "Searching for config files in: $config_dir"
    
    # Create archive_results directory if it doesn't exist
    mkdir -p archive_results
    
    # Find all YAML config files (excluding the generic config.yaml)
    while IFS= read -r -d '' config_file; do
        # Skip generic config.yaml files, only process model-specific configs
        if [[ $(basename "$config_file") != "config.yaml" ]]; then
            total_tests=$((total_tests + 1))
            
            print_status "Found config: $config_file"
            
            # Generate output directory
            output_dir=$(generate_output_dir "$config_file")
            
            echo ""
            echo "=========================================="
            echo "Test $total_tests: $(basename "$config_file")"
            echo "=========================================="
            
            # Run the test
            if run_single_test "$config_file" "$output_dir"; then
                successful_tests+=("$config_file")
            else
                failed_tests+=("$config_file")
            fi
            
            echo ""
        fi
    done < <(find "$config_dir" -name "*.yaml" -type f -print0)
    
    # Print summary
    echo ""
    echo "=========================================="
    echo "BATCH TEST SUMMARY"
    echo "=========================================="
    echo "Total tests: $total_tests"
    echo "Successful: ${#successful_tests[@]}"
    echo "Failed: ${#failed_tests[@]}"
    
    if [ ${#successful_tests[@]} -gt 0 ]; then
        echo ""
        print_success "Successful tests:"
        for test in "${successful_tests[@]}"; do
            echo "  ✓ $test"
        done
    fi
    
    if [ ${#failed_tests[@]} -gt 0 ]; then
        echo ""
        print_error "Failed tests:"
        for test in "${failed_tests[@]}"; do
            echo "  ✗ $test"
        done
        exit 1
    fi
    
    print_success "All tests completed successfully!"
}

# Help function
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Batch testing script for vLLM configurations"
    echo ""
    echo "OPTIONS:"
    echo "  -h, --help     Show this help message"
    echo "  -d, --dry-run  Show what tests would be run without executing them"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests"
    echo "  $0 --dry-run         # Preview what tests would be run"
    echo ""
    echo "Output directories will be created in the format:"
    echo "  archive_results/vllm-version--instance-type--model-config"
    echo ""
    echo "Example:"
    echo "  model_configs/vllm-v0.9.2/g6e.4xlarge/Qwen3-30B-A3B-FP8.yaml"
    echo "  → archive_results/vllm-v0.9.2--g6e.4xlarge--Qwen3-30B-A3B-FP8"
}

# Dry run function
dry_run() {
    local config_dir="model_configs"
    local total_tests=0
    
    print_status "DRY RUN - Showing tests that would be executed"
    print_status "Searching for config files in: $config_dir"
    
    echo ""
    echo "Tests that would be run:"
    echo "========================"
    
    while IFS= read -r -d '' config_file; do
        if [[ $(basename "$config_file") != "config.yaml" ]]; then
            total_tests=$((total_tests + 1))
            output_dir=$(generate_output_dir "$config_file")
            
            echo "$total_tests. Config: $config_file"
            echo "   Output: $output_dir"
            echo "   Command: uv run run_auto_test.py --config \"$config_file\" --output-dir \"$output_dir\""
            echo ""
        fi
    done < <(find "$config_dir" -name "*.yaml" -type f -print0)
    
    echo "Total tests that would be run: $total_tests"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -d|--dry-run)
        dry_run
        exit 0
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
#!/bin/bash

# Simple batch testing script for vLLM model configurations
# Runs tests for each model config with organized output directories

set -e

ec2_instance_type=`ec2metadata --instance-type`
echo Current instance type: $ec2_instance_type

# Function to run test for a specific config
run_test() {
    local config_path="$1"
    
    # Extract vllm version and instance type from path
    local vllm_version=$(echo "$config_path" | cut -d'/' -f2)
    local instance_type=$(echo "$config_path" | cut -d'/' -f3)
    local model_name=$(echo "$config_path" | cut -d'/' -f4)
    
    # Check if instance type matches current EC2 instance
    if [ "$instance_type" != "$ec2_instance_type" ]; then
        echo "⏭️  Skipping: $model_name (requires $instance_type, current: $ec2_instance_type)"
        return 0
    fi
    

    # Strip .yaml suffix from model name
    model_name="${model_name%.yaml}"
    
    # Generate output directory in your format
    local output_dir="archive_results/${vllm_version}--${instance_type}--${model_name}"
    
    echo "=========================================="
    echo "Testing: $model_name"
    echo "Config: $config_path"
    echo "Output: $output_dir"
    echo "=========================================="
    # exit
    # Run the test
    uv run run_auto_test.py --config "$config_path" --output-dir "$output_dir" $2
    
    echo "✓ Completed: $model_name"
    echo ""
}

# Create output directory
mkdir -p archive_results

# Run tests for each model configuration
echo "Starting batch tests for vLLM model configurations..."
echo ""

run_test ""


# g6e.4xlarge
run_test "model_configs/sglang-v0.4.9.post4/g6e.4xlarge/Qwen3-30B-A3B-FP8.yaml"
run_test "model_configs/vllm-v0.9.2/g6e.4xlarge/Qwen3-30B-A3B-FP8.yaml"
run_test "model_configs/sglang-v0.4.9.post4/g6e.4xlarge/Qwen3-8B-FP8.yaml"
run_test "model_configs/sglang-v0.4.9.post4/g6e.4xlarge/Qwen3-14B-FP8.yaml"
run_test "model_configs/sglang-v0.4.9.post4/g6e.4xlarge/Qwen3-32B-FP8.yaml"


# p4d.24xlarge


# p5.48xlarge
run_test "model_configs/sglang-v0.4.9.post4/p5.48xlarge/Qwen3-235B-A22B.yaml"
run_test "model_configs/sglang-v0.4.9.post4/p5.48xlarge/Qwen3-30B-A3B-FP8-tp1dp8.yaml"
run_test "model_configs/sglang-v0.4.9.post4/p5.48xlarge/Qwen3-30B-A3B-FP8-tp1dp1.yaml"
run_test "model_configs/sglang-v0.4.9.post6/p5.48xlarge/GLM-4.5-Air-FP8-tp2dp4-mtp.yaml"
run_test "model_configs/sglang-v0.4.9.post6/p5.48xlarge/GLM-4.5-Air-FP8-tp4dp2-mtp.yaml"
run_test "model_configs/sglang-v0.4.9.post6/p5.48xlarge/GLM-4.5-FP8-tp8-mtp.yaml"

# p5en.48xlarge
run_test "model_configs/sglang-v0.4.9.post6/p5en.48xlarge/GLM-4.5-Air-FP8-dp8-mtp.yaml"
run_test "model_configs/sglang-v0.4.9.post6/p5en.48xlarge/GLM-4.5-Air-FP8-tp2dp4-mtp.yaml"
run_test "model_configs/sglang-v0.4.9.post6/p5en.48xlarge/GLM-4.5-FP8-tp8-mtp.yaml"
run_test "model_configs/sglang-v0.4.9.post6/p5en.48xlarge/GLM-4.5-FP8-tp4dp2-mtp.yaml"
run_test "model_configs/sglang-v0.4.9.post4/p5en.48xlarge/DeepSeek-R1-0528.yaml"
run_test "model_configs/sglang-v0.4.9.post4/p5en.48xlarge/Qwen3-235B-A22B-FP8-tp4dp2.yaml"
run_test "model_configs/sglang-v0.4.9.post4/p5en.48xlarge/Qwen3-235B-A22B.yaml"


echo "=========================================="
echo "All tests completed!"
echo "Results saved in archive_results/"
echo "=========================================="
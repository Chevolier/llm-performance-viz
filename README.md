# LLM Test Tool

A comprehensive tool for testing LLM API performance with automated deployment and extensive test matrices.

## Features

- Test LLM API performance with multiple parallel processes
- Automated vLLM Docker deployment and management
- Comprehensive test matrix with configurable input/output tokens and concurrency levels
- Measure first token latency, end-to-end latency, and output tokens per second
- Generate detailed statistical reports with percentiles (p25, p50, p75, p90)
- Support for prompt caching optimization with fixed and random prompt parts
- Token usage tracking and analysis
- Automated warmup and cooldown between test cases

## Installation

Using uv:

```bash
uv pip install -e .
```

## Quick Start Guide

### 1. Download Model Weights

Ensure your model weights are available via Hugging Face Hub or pre-downloaded locally. The tool supports models like `Qwen/Qwen3-235B-A22B-FP8`, `Qwen/Qwen3-30B-A3B-FP8`, etc.

### 2. Create Configuration Files

Configuration files are stored in `model_configs/` organized by framework version and instance type:

```
model_configs/
├── vllm-v0.9.2/
│   ├── g6e.4xlarge/
│   ├── g6e.48xlarge/
│   └── p5en.48xlarge/
├── sglang-v0.4.9.post4/
└── sglang-v0.4.9.post6/
```

Example configuration:

```yaml
deployment:
  docker_image: "vllm/vllm-openai:v0.9.2"
  container_name: "vllm"
  port: 8080
  docker_params:
    gpus: "all"
    shm-size: "1000g"
    ipc: "host"
    network: "host"
    volume:
      - "/opt/dlami/nvme/:/vllm-workspace/"
  app_args:
    model: "Qwen/Qwen3-235B-A22B-FP8"
    trust-remote-code: true
    max-model-len: 32768
    gpu-memory-utilization: 0.90
    tensor-parallel-size: 4
    data-parallel-size: 2

test_matrix:
  input_tokens: [100, 1600, 6400, 12800]
  output_tokens: [100, 400, 1000]
  processing_num: [1, 4, 16, 32, 64, 128]
  random_tokens: [100, 1600, 6400, 12800]

test_config:
  requests_per_process: 5
  warmup_requests: 1
  cooldown_seconds: 5
```

### 3. Run Tests

#### Automated Testing with Deployment
```bash
uv run run_auto_test.py --config model_configs/vllm-v0.9.2/g6e.48xlarge/Qwen3-235B-A22B-FP8-tp8ep.yaml
```

#### Deploy Only (Skip Testing)
```bash
uv run deploy_server.py --config your_config.yaml
```

#### Test with Existing Server
```bash
uv run run_auto_test.py --config your_config.yaml --skip-deployment
```

#### Batch Testing
```bash
# Run all configured tests
./run_model_tests.sh

# Run single test
./run_single_test.sh "model_configs/vllm-v0.9.2/g6e.48xlarge/Qwen3-235B-A22B-FP8-tp8ep.yaml"
```

#### Manual Testing
```bash
llm-test --processes 4 --requests 10 --model_id "Qwen/Qwen3-235B-A22B-FP8" \
    --input_tokens 1000 --output_tokens 100 --random_tokens 100 \
    --url "http://localhost:8080/v1/chat/completions"
```

### 4. Visualize Results

```bash
# Start visualization server
uv run start_viz_server.py
# or
uv run -m llm_test_tool viz

# Access web interface at: http://localhost:8000
```

### Key Parameters

- **tensor-parallel-size**: Number of GPUs for tensor parallelism
- **data-parallel-size**: Number of data parallel replicas  
- **enable-expert-parallel**: Enable expert parallelism for MoE models
- **processing_num**: Concurrent request levels to test
- **input_tokens/output_tokens**: Token lengths for comprehensive testing
- **random_tokens**: Variable prompt parts for caching optimization

Results are saved in timestamped directories under `test_results/` with detailed statistical reports including latency percentiles and throughput metrics.

## Usage

### Manual Testing

```bash
llm-test --processes 4 --requests 10 --model_id "Qwen/Qwen3-30B-A3B-FP8" --input_tokens 20 --random_tokens 5 --output_tokens 100 --url "http://localhost:8080/v1/chat/completions"
```

### Automated Testing with Docker Deployment

The tool now supports automated testing with Docker deployment management:

```bash
# Basic usage
uv run run_auto_test.py --config model_configs/vllm-v0.9.2/g6e.4xlarge/config.yaml

# With custom output directory
uv run run_auto_test.py --config config.yaml --output-dir my_results

# Dry run to see what tests would be executed
uv run run_auto_test.py --config config.yaml --dry-run

# Verbose output for debugging
uv run run_auto_test.py --config config.yaml --verbose

# Force rerun all tests (ignore existing results)
uv run run_auto_test.py --config config.yaml --force-rerun
```

Or using the module directly:

```bash
uv run -m llm_test_tool auto-test --config model_configs/vllm-v0.9.2/g6e.4xlarge/config.yaml --output-dir test_results
```

### Deployment Only (No Benchmarking)

For cases where you only want to deploy a server without running benchmarks:

```bash
# Deploy a server
uv run deploy_server.py --config model_configs/vllm-v0.9.2/g6e.4xlarge/Qwen3-30B-A3B-FP8.yaml

# Show the Docker command without executing
uv run deploy_server.py --config config.yaml --show-command

# Deploy without health check
uv run deploy_server.py --config config.yaml --no-health-check

# Check deployment status
uv run deploy_server.py --config config.yaml --status

# Stop a deployment
uv run deploy_server.py --config config.yaml --stop
```

Or using the module directly:

```bash
uv run -m llm_test_tool deploy --config config.yaml
```

### Performance Visualization

For interactive performance analysis and comparison:

```bash
# Start the visualization server
uv run start_viz_server.py
# or
uv run -m llm_test_tool viz

# Access the web interface at: http://localhost:8000
```

### Parameters

- `--processes`: Number of parallel processes (default: 2)
- `--requests`: Number of requests per process (default: 5)
- `--model_id`: Model ID to test (default: "gpt-3.5-turbo")
- `--input_tokens`: Total approximate input token length (default: 10)
- `--random_tokens`: Number of random tokens to add to the prompt (default: 2)
- `--output_tokens`: Maximum output tokens to generate (default: 50)
- `--url`: API endpoint URL (default: "http://localhost:8080/v1/chat/completions")
- `--output`: Results output file (default: "test_results.json")

## Example Output

```
Starting LLM API test:
- Processes: 4
- Requests per process: 10
- Total requests: 40
- Model ID: Qwen/Qwen3-30B-A3B-FP8
- Total input tokens: 20
- Random tokens: 5
- Output tokens: 100
- API endpoint: http://localhost:8080/v1/chat/completions
--------------------------------------------------

Test completed!
Total duration: 12.45 seconds
Success rate: 100.00%
Throughput: 3.21 requests/second

First Token Latency (seconds):
- Min: 0.4521
- Max: 0.8976
- Mean: 0.6234

Percentiles:
- p25: 0.5123
- p50: 0.5987
- p75: 0.7234
- p90: 0.8456

End-to-End Latency (seconds):
- Min: 1.2345
- Max: 2.3456
- Mean: 1.7890

Percentiles:
- p25: 1.4567
- p50: 1.6789
- p75: 2.0123
- p90: 2.2345

Token Usage Statistics:

Prompt Tokens:
- Min: 18
- Max: 22
- Mean: 20.15

Percentiles:
- p25: 19
- p50: 20
- p75: 21
- p90: 22

Completion Tokens:
- Min: 95
- Max: 105
- Mean: 99.8

Percentiles:
- p25: 97
- p50: 100
- p75: 102
- p90: 104

Output Tokens Per Second:
- Min: 45.23
- Max: 78.91
- Mean: 62.45

Percentiles:
- p25: 55.67
- p50: 61.23
- p75: 68.89
- p90: 74.56

Detailed results saved to: test_results.json
```
## Configuration

### Configuration File Structure

The configuration file is a YAML file with four main sections that control deployment, testing parameters, and test execution:

#### 1. Deployment Section

Controls Docker container deployment and server startup parameters:

```yaml
deployment:
  docker_image: "vllm/vllm-openai:v0.9.2"  # Docker image to use
  container_name: "vllm"                   # Container name for management
  port: 8080                               # Port to expose the API
  
  # Docker runtime parameters
  docker_params:
    gpus: "all"                           # GPU access ("all", "device=0,1", etc.)
    shm-size: "1000g"                     # Shared memory size for multi-GPU
    ipc: "host"                           # IPC mode for performance
    network: "host"                       # Network mode
    volume:                               # Volume mounts
      - "/opt/dlami/nvme/:/vllm-workspace/"
    environment:                          # Environment variables
      CUDA_VISIBLE_DEVICES: "0,1,2,3"
  
  # Application startup arguments
  app_args:
    model: "Qwen/Qwen3-235B-A22B-FP8"    # Model path or HuggingFace ID
    trust-remote-code: true               # Allow custom model code
    max-model-len: 32768                  # Maximum sequence length
    gpu-memory-utilization: 0.90          # GPU memory usage fraction
    tensor-parallel-size: 4               # Number of GPUs for tensor parallelism
    data-parallel-size: 2                 # Number of data parallel replicas
    enable-reasoning: true                # Enable reasoning capabilities
    reasoning-parser: "deepseek_r1"       # Reasoning output parser
    tool-call-parser: "deepseek_v3"       # Tool calling parser
```

#### 2. Test Matrix Section

Defines the comprehensive test scenarios to execute:

```yaml
test_matrix:
  input_tokens: [100, 1600, 6400, 12800]    # Input prompt lengths to test
  output_tokens: [100, 400, 1000]           # Output generation lengths
  processing_num: [1, 4, 16, 32, 64, 128]   # Concurrent request levels
  random_tokens: [100, 1600, 6400, 12800]   # Variable prompt parts for caching
```

**Test Matrix Explanation:**
- **input_tokens**: Controls the base prompt length for testing different context sizes
- **output_tokens**: Sets maximum tokens to generate, testing different generation lengths
- **processing_num**: Number of concurrent requests to simulate different load levels
- **random_tokens**: Variable portion of prompts to test prompt caching effectiveness

The tool automatically generates all combinations of these parameters, skipping invalid cases where `random_tokens > input_tokens`.

#### 3. Test Configuration Section

Controls test execution behavior:

```yaml
test_config:
  requests_per_process: 5    # Number of requests each concurrent process sends
  warmup_requests: 1         # Warmup requests before timing measurements
  cooldown_seconds: 5        # Wait time between different test scenarios
```

**Test Config Explanation:**
- **requests_per_process**: Total requests = `processing_num × requests_per_process`
- **warmup_requests**: Ensures consistent performance by warming up the model
- **cooldown_seconds**: Prevents interference between test cases

### Advanced Configuration Options

#### Parallelism Configuration

Different parallelism strategies for large models:

```yaml
app_args:
  # Tensor Parallelism: Split model layers across GPUs
  tensor-parallel-size: 8
  
  # Data Parallelism: Run multiple model replicas
  data-parallel-size: 2
  
  # Expert Parallelism: For MoE models, split experts across GPUs
  enable-expert-parallel: true
  
  # Pipeline Parallelism: Split model stages across GPUs
  pipeline-parallel-size: 2
```

#### Memory and Performance Tuning

```yaml
app_args:
  gpu-memory-utilization: 0.90      # GPU memory fraction to use
  max-model-len: 32768              # Maximum sequence length
  max-num-seqs: 256                 # Maximum concurrent sequences
  block-size: 16                    # KV cache block size
  swap-space: 4                     # CPU swap space in GB
  cpu-offload-gb: 0                 # CPU offload memory
```

#### Framework-Specific Examples

#### Real-World Configuration Examples

**vLLM Configuration (Large Model with Tensor Parallelism):**

```yaml
deployment:
  docker_image: "vllm/vllm-openai:v0.10.1+gptoss"
  container_name: "vllm"
  port: 8080
  docker_params:
    gpus: "all"                           # Use all available GPUs
    shm-size: "1000g"                     # Large shared memory for multi-GPU
    ipc: "host"                           # Host IPC for performance
    network: "host"                       # Host networking
    volume:
      - "/opt/dlami/nvme/:/vllm-workspace/"  # Mount model storage
  app_args:
    model: "openai/gpt-oss-120b"          # 120B parameter model
    trust-remote-code: true               # Allow custom model code
    max-model-len: 32768                  # 32K context length
    gpu-memory-utilization: 0.90          # Use 90% of GPU memory
    tensor-parallel-size: 8               # Split across 8 GPUs
    enable-reasoning: true                # Enable reasoning mode
    reasoning-parser: "deepseek_r1"       # Reasoning output parser
    tool-call-parser: "deepseek_v3"       # Tool calling parser
    enable-auto-tool-choice: true         # Auto tool selection
```

**SGLang Configuration (Smaller Model):**

```yaml
deployment:
  docker_image: "lmsysorg/sglang:v0.4.9.post4-cu126"
  container_name: "sglang"
  port: 8080
  command: "python3 -m sglang.launch_server"  # Custom launch command
  docker_params:
    gpus: "all"
    shm-size: "1000g"
    ipc: "host"
    network: "host"
    volume:
      - "/opt/dlami/nvme/:/sgl-workspace/sglang/model"
  app_args:
    host: "0.0.0.0"                       # Bind to all interfaces
    model-path: "model/Qwen/Qwen3-14B-FP8"  # Local model path
    trust-remote-code: true
    tp-size: 1                            # Single GPU (14B model)
    mem-fraction-static: 0.90             # SGLang memory setting
    tool-call-parser: "qwen25"            # Qwen-specific parser
    reasoning-parser: "deepseek-r1"
```

### Configuration File Sections Explained

#### Docker Parameters (`docker_params`)

Maps directly to `docker run` arguments:

| Parameter | Description | Example Values |
|-----------|-------------|----------------|
| `gpus` | GPU access control | `"all"`, `"device=0,1"`, `"2"` |
| `shm-size` | Shared memory size | `"1000g"`, `"32g"` |
| `ipc` | IPC namespace | `"host"`, `"container:name"` |
| `network` | Network mode | `"host"`, `"bridge"` |
| `volume` | Volume mounts | `["/host:/container"]` |
| `environment` | Environment variables | `{"VAR": "value"}` |
| `memory` | Memory limit | `"64g"`, `"128g"` |
| `cpus` | CPU limit | `"16"`, `"32"` |

#### Application Arguments (`app_args`)

Framework-specific server arguments:

**Common vLLM Arguments:**
| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| `model` | Model identifier | HuggingFace ID or path |
| `tensor-parallel-size` | GPUs for tensor parallelism | 1, 2, 4, 8 |
| `data-parallel-size` | Data parallel replicas | 1, 2, 4 |
| `gpu-memory-utilization` | GPU memory fraction | 0.85, 0.90, 0.95 |
| `max-model-len` | Maximum sequence length | 4096, 16384, 32768 |
| `max-num-seqs` | Concurrent sequences | 128, 256, 512 |
| `trust-remote-code` | Allow custom code | true, false |
| `enable-reasoning` | Reasoning capabilities | true, false |

**Common SGLang Arguments:**
| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| `model-path` | Model path | Local or HuggingFace path |
| `tp-size` | Tensor parallel size | 1, 2, 4, 8 |
| `mem-fraction-static` | Memory allocation | 0.85, 0.90, 0.95 |
| `host` | Bind address | "0.0.0.0", "127.0.0.1" |
| `context-length` | Context window | 4096, 16384, 32768 |

#### Test Matrix Configuration

The test matrix creates comprehensive performance profiles:

```yaml
test_matrix:
  input_tokens: [1600, 6400, 12800]      # Prompt lengths
  output_tokens: [100, 400, 1000]        # Generation lengths  
  processing_num: [1, 16, 32, 64, 128]   # Concurrency levels
  random_tokens: [100, 1600, 6400]       # Caching test sizes
```

**Matrix Combinations:**
- Total test cases = `len(input_tokens) × len(output_tokens) × len(processing_num) × len(random_tokens)`
- Invalid combinations (where `random_tokens > input_tokens`) are automatically skipped
- Each combination tests different aspects:
  - **Short input + Low concurrency**: Latency optimization
  - **Long input + High concurrency**: Throughput under load
  - **Variable random tokens**: Prompt caching effectiveness

#### Test Execution Settings

```yaml
test_config:
  requests_per_process: 5     # Requests per concurrent process
  warmup_requests: 1          # Warmup before measurement
  cooldown_seconds: 5         # Wait between test scenarios
```

**Calculation Examples:**
- With `processing_num: 32` and `requests_per_process: 5`
- Total requests per test case: 32 × 5 = 160 requests
- With warmup: 32 × 1 = 32 additional warmup requests

### Configuration Best Practices

#### GPU Memory Management
```yaml
# For large models, use conservative memory settings
app_args:
  gpu-memory-utilization: 0.85    # Leave headroom for CUDA operations
  max-model-len: 16384            # Balance context vs memory usage
```

#### Multi-GPU Strategies
```yaml
# Tensor Parallelism: Best for large models
app_args:
  tensor-parallel-size: 8         # Split model across 8 GPUs

# Data Parallelism: Best for high throughput
app_args:
  data-parallel-size: 4           # 4 model replicas
  tensor-parallel-size: 2         # Each replica uses 2 GPUs
```

#### Performance Optimization
```yaml
# High-performance settings
docker_params:
  shm-size: "1000g"              # Large shared memory
  ipc: "host"                    # Host IPC mode
  network: "host"                # Host networking

app_args:
  max-num-seqs: 512              # High concurrency
  block-size: 16                 # Optimal KV cache block size
```

### Troubleshooting Configuration Issues

**Common Problems:**

1. **Out of Memory**: Reduce `gpu-memory-utilization` or `max-model-len`
2. **Slow Performance**: Increase `shm-size`, use `ipc: "host"`
3. **Model Loading Fails**: Check `trust-remote-code: true` for custom models
4. **Multi-GPU Issues**: Verify `tensor-parallel-size` matches available GPUs

**Debug Configuration:**
```yaml
# Add verbose logging
app_args:
  log-level: "DEBUG"
  
# Show generated Docker command
# Use: uv run deploy_server.py --config config.yaml --show-command
```

```yaml
deployment:
  docker_image: "vllm/vllm-openai:v0.9.2"
  container_name: "vllm-qwen3-30b"
  port: 8080
  
  # Optional: Custom command to run inside container (for non-vLLM servers)
  # command: "python3 -m sglang.launch_server"  # String format
  # command: ["python3", "-m", "sglang.launch_server"]  # List format
  
  # Universal Docker parameters - any Docker run parameter
  docker_params:
    gpus: "all"
    shm-size: "747g"
    ipc: "host"
    volume:
    environment:
      CUDA_VISIBLE_DEVICES: "0,1,2,3"
    # Any other Docker parameter: memory, cpus, ulimit, etc.
  
  # Universal application arguments - any server argument
  app_args:
    model: "Qwen/Qwen3-30B-A3B-FP8"  # or model-path for SGLang
    gpu-memory-utilization: 0.95
    max-model-len: 16384
    trust-remote-code: true
    enable-reasoning: true
    tool-call-parser: "hermes"
    reasoning-parser: "deepseek_r1"
    # Any other argument: tensor-parallel-size, max-num-seqs, etc.

test_matrix:
  input_tokens: [100, 200, 400, 800, 2000, 4000, 8000]
  output_tokens: [20, 100, 400, 1000]
  processing_num: [1, 4, 16, 32, 64, 128]
  random_tokens: [2, 10, 50, 100]

test_config:
  requests_per_process: 5
  warmup_requests: 3
  cooldown_seconds: 5
```

#### SGLang Support

The system supports SGLang and other inference servers using the `command` parameter:

```yaml
deployment:
  docker_image: "lmsysorg/sglang:v0.4.9.post4-cu126"
  container_name: "sglang-qwen3-30b"
  port: 8080
  
  # Custom command for SGLang
  command: "python3 -m sglang.launch_server"
  
  docker_params:
    gpus: "all"
    shm-size: "32g"
    volume:
      - "/cache:/root/.cache"
  
  app_args:
    model-path: "Qwen/Qwen3-30B-A3B-FP8"
    tokenizer-path: "Qwen/Qwen3-30B-A3B-FP8"
    host: "0.0.0.0"
    tp-size: 4
    context-length: 16384
```

#### Legacy Format Support

The system maintains backward compatibility with the old format:

```yaml
deployment:
  docker_image: "vllm/vllm-openai:v0.9.2"
  container_name: "vllm-qwen3-30b"
  port: 8080
  gpu_config:
    gpus: "all"
    gpu_memory_utilization: 0.95
    shm_size: "747g"
  model_config:
    model: "Qwen/Qwen3-30B-A3B-FP8"
    max_model_len: 16384
    trust_remote_code: true
  volumes:
    - "/cache:/root/.cache"
```

### Test Matrix

The automated testing runs through all combinations of:
- **Input tokens**: [100, 200, 400, 800, 2000, 4000, 8000]
- **Output tokens**: [20, 100, 400, 1000]  
- **Processing numbers**: [1, 4, 16, 32, 64, 128]
- **Random tokens**: [2, 10, 50, 100]

Test cases where `random_tokens > input_tokens` are automatically skipped to ensure valid configurations.

This creates a comprehensive performance profile across different load conditions and prompt caching scenarios.

## Command Line Options

### Testing Commands (`run_auto_test.py`)

- `--config, -c`: Path to YAML or JSON configuration file (required)
- `--output-dir, -o`: Output directory for test results (default: auto-generated timestamp under test_results/)
- `--verbose, -v`: Enable verbose output for debugging
- `--skip-deployment`: Skip Docker deployment (assume server is already running)
- `--force-rerun`: Force rerun all tests, ignoring existing results
- `--dry-run`: Show what tests would be executed without running them

Use `uv run run_auto_test.py --help` for full usage information.

### Deployment Commands (`deploy_server.py`)

- `--config, -c`: Path to YAML or JSON configuration file (required)
- `--show-command`: Show the generated Docker command without executing it
- `--no-health-check`: Skip health check after deployment
- `--stop`: Stop and remove the deployment instead of starting it
- `--status`: Check the status of the deployment
- `--verbose, -v`: Enable verbose output

Use `uv run deploy_server.py --help` for full usage information.

## Automated Testing Features

- **Docker Management**: Automatically starts, stops, and manages vLLM Docker containers
- **Health Checking**: Waits for the server to become healthy before testing
- **Warmup Requests**: Runs warmup requests before each test case to ensure consistent results
- **Cooldown Periods**: Configurable cooldown between test cases
- **Comprehensive Results**: Saves individual test results and generates summary statistics
- **Error Handling**: Continues testing even if individual test cases fail
- **Resource Cleanup**: Automatically cleans up Docker containers after testing
- **Dry Run Mode**: Preview test cases without executing them
- **Verbose Logging**: Detailed output for troubleshooting
- **Result Caching**: Automatically skips test cases with existing results
- **Force Rerun**: Option to ignore cached results and rerun all tests

## Output

The automated testing generates:
- Individual test result files for each test case
- A comprehensive results file with all test data and summary statistics
- Console output showing progress and real-time results
- Performance comparisons across different configurations
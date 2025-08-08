```bash
conda create -p /home/ec2-user/SageMaker/efs/conda_envs/vllm python=3.12 -y
conda activate vllm

pip install --upgrade uv
# uv pip install vllm --torch-backend=auto


# curl -LsSf https://astral.sh/uv/install.sh | sh

# uv venv --python 3.12 --seed

# source .venv/bin/activate

uv pip install --pre vllm==0.10.1+gptoss \
    --extra-index-url https://wheels.vllm.ai/gpt-oss/ \
    --extra-index-url https://download.pytorch.org/whl/nightly/cu128 \
    --index-strategy unsafe-best-match \
    --no-cache
    
pip install -U "huggingface_hub[cli]"

 --Optional
 pip install "flash-attn==2.8.1" --no-build-isolation
```

Download GPT-OSS models

```bash
huggingface-cli download openai/gpt-oss-120b --local-dir /home/ec2-user/SageMaker/efs/Models/gpt-oss-120b --exclude "metal/*" "original/*"

huggingface-cli download openai/gpt-oss-20b --local-dir /home/ec2-user/SageMaker/efs/Models/gpt-oss-20b --exclude "metal/*" "original/*"
```

Run the server

```bash
nohup vllm serve /home/ec2-user/SageMaker/efs/Models/gpt-oss-120b \
    --host 0.0.0.0 --port 8000 \
    --tensor-parallel-size 1 \
    --gpu-memory-utilization 0.9 \
    --max-model-len 32768 > logs/server.out 2>&1 &

nohup vllm serve /home/ec2-user/SageMaker/efs/Models/gpt-oss-20b \
    --host 0.0.0.0 --port 8000 \
    --tensor-parallel-size 8 \
    --gpu-memory-utilization 0.9 \
    --max-model-len 32768 > logs/server_gptoss-20b.out 2>&1 &
```
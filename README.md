# AgentVerify

## Setup

1. Clone this repository:

```bash
git clone https://github.com/avaljotsingh/tau-bench.git && cd ./tau-bench
```

2. Install from source (which also installs required packages):

```bash
pip install -e .
```


## Run

In the following commands, the agent-name can be one of the following: 
1. Original tau bench baseline: tool-calling 
2. Tool calling with preconditions in the form of advice: tool-calling-with-preconditions 
3. Tool calling with preconditions in the form of advice and python code generation: tool-calling-with-preconditions-and-python 
4. Symbolic multi-agent system: orchestrator 
5. With pre and post conditions: assertions-agent 


To run specific tasks, use the `--task-ids` flag. For example:

```bash
python run.py --agent-strategy <agent-name> --env retail --model none --model-provider openai --user-model none --user-model-provider openai --user-strategy llm --max-concurrency 10 --task-ids 1
```

To run a range of tasks, use the `--start-index` and `--end-index` flags. For example:
 
```bash
python run.py --agent-strategy <agent-name> --env retail --model none --model-provider openai --user-model none --user-model-provider openai --user-strategy llm --max-concurrency 10 --start-index 10 --end-index 100
```

## New commands (Tau Bench Running with VLLM Server)

VLLM Server Starting:

```python

python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-7B-Instruct \
  --host 0.0.0.0 --port 8000 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.95 \
  --trust-remote-code \
  --tool-call-parser qwen2 \
  --enable-auto-tool-choice

  ```

Tau-Bench Running:

```python

export OPENAI_API_BASE=http://localhost:8000/v1
export OPENAI_API_KEY=sk-local
export VLLM_ENABLE_AUTO_TOOL_CHOICE=1


python run.py \
  --model-provider openai \
  --model Qwen/Qwen2.5-7B-Instruct \
  --user-model Qwen/Qwen2.5-7B-Instruct \
  --user-model-provider openai \
  --agent-strategy tool-calling \
  --env airline \
  --num-trials 1 \
  --task-split test \
  --temperature 0.1
```


## Library Learning

```python
export OPENAI_API_BASE=http://localhost:8000/v1
export OPENAI_API_KEY=sk-local

export LIBGEN_AGENT_MODEL=deepseek-ai/deepseek-coder-1.3b-instruct
export LIBGEN_USER_MODEL=$LIBGEN_AGENT_MODEL

python libgen_experiment.py
```

## LibGen Experiment Runner

Run generalized library-learning experiments with structured outputs and JSON configs.

### 1) Pick/prepare a config
- Start from `configs/libgen/airline.json` (or duplicate it).
- Ensure:
  - `env`: `"airline"` or `"retail"`
  - `library.base_library_path`: absolute path to base MCP server
    - Airline: `/home/madhav/ext-madhav/tau-bench/mcp/airline_server.py`
    - Retail: `/home/madhav/ext-madhav/tau-bench/mcp/retail_server.py`
  - `input_tasks.mode`: `"latest_for_env"` or `"base_library"`
  - Keep `agent.model` and `agent.user_model` as `null` to use env vars

### 2) Recommended: vLLM (OpenAI-compatible) setup
Start vLLM (example: Llama 3.1 8B Instruct, 128k context):

```bash
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Meta-Llama-3.1-8B-Instruct \
  --max-model-len 131072 \
  --host 0.0.0.0 --port 8000
```

Export env vars:

```bash
export OPENAI_API_BASE=http://localhost:8000/v1
export OPENAI_API_KEY=sk-local
export LIBGEN_AGENT_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct
export LIBGEN_USER_MODEL=$LIBGEN_AGENT_MODEL
```

Run:

```bash
python /home/madhav/ext-madhav/tau-bench/libgen_experiment.py \
  --config /home/madhav/ext-madhav/tau-bench/configs/libgen/airline.json
```

Notes:
- With `agent.model`/`agent.user_model` null in JSON, the runner uses the `LIBGEN_*` env vars.
- `OPENAI_API_BASE` routes both libgen and env runs through your vLLM server.

### 3) Optional: TRAPI for libgen
Use TRAPI for function suggestion/definition/correction. Make sure your shell does NOT have an OpenAI-compatible base URL set.

```bash
az login
export LIBGEN_PROVIDER=azure_trapi
unset OPENAI_API_BASE
unset VLLM_BASE_URL
# optional if using managed identity:
# export DEFAULT_IDENTITY_CLIENT_ID=<your-identity-client-id>
# optional TRAPI model selection:
# export LIBGEN_AGENT_MODEL=gpt-4.1
# export LIBGEN_USER_MODEL=$LIBGEN_AGENT_MODEL

python /home/madhav/ext-madhav/tau-bench/libgen_experiment.py \
  --config /home/madhav/ext-madhav/tau-bench/configs/libgen/airline.json
```

Important:
- If `OPENAI_API_BASE` is set, libgen calls will go to your OpenAI-compatible endpoint instead of TRAPI.
- If you need TRAPI for libgen and vLLM for env in the same process, a small code switch is needed to force TRAPI regardless of `OPENAI_API_BASE`.

### 4) Outputs
Written to `experiments/libgen/<experiment_name>/`:
- `manifest.json` (config snapshot)
- `input/tasks.json` (from latest logs or warmup)
- `phases/iteration_<k>/generation` and `validation` (per-task results, metrics)
- `artifacts/functions/` (proposed functions)
- `artifacts/mcp_servers/` (MCP snapshots)
- `test/test_results.json`
- `logs/experiment.log`



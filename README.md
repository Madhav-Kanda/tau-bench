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

## Tau Bench Running

### Tau Bench Running (TRAPI):

```bash
az login
unset OPENAI_API_BASE
unset VLLM_BASE_URL

python run.py \
  --agent-strategy tool-calling \
  --env airline \
  --model gpt-4o \
  --model-provider azure \
  --user-model gpt-4o \
  --user-model-provider azure \
  --user-strategy llm \
  --num-trials 1 \
  --task-split test \
  --temperature 0.1
```

Notes:
- Ensure `OPENAI_API_BASE` is unset so requests route through TRAPI.

## Library Learning

1) Ensure your configs file [configs/libgen/airline.json] points to the correct MCP server (absolute path recommended). 

Key fields to verify for airline:
- `"env": "airline"`
- `"library.base_library_path": "mcp/airline_server.py"`
- `"input_tasks.mode": "latest_for_env"`
- Leave `"agent.model"` and `"agent.user_model"` as `null` to use env vars

Important:
- Change `"experiment_name"` in your config for each new run. The runner writes to `experiments/libgen/<experiment_name>/`. Reusing the same name will overwrite prior results in that folder.

2) Use TRAPI for LibGen (function suggestion/definition/correction):

```bash
az login
export LIBGEN_PROVIDER=azure_trapi
unset OPENAI_API_BASE
unset VLLM_BASE_URL
# optional: export DEFAULT_IDENTITY_CLIENT_ID=<your-identity-client-id>
# optional TRAPI model selection:
export LIBGEN_AGENT_MODEL=gpt-4.1
export LIBGEN_USER_MODEL=$LIBGEN_AGENT_MODEL

python libgen_experiment.py \
  --config configs/libgen/airline.json
```

Notes:
- If `OPENAI_API_BASE` is set in the shell, LibGen calls will route to your OpenAI-compatible endpoint instead of TRAPI.
- To run TRAPI for LibGen and vLLM for env in the same process, a small code change is needed to force TRAPI regardless of `OPENAI_API_BASE`.

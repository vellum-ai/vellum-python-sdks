# Chatbot (previous execution ID + SetState)

This example is a small variant of the chatbot workflow that explicitly uses `SetStateNode` to append chat history on each run. Passing a `previous_execution_id` loads the prior state so history keeps growing across executions.

## Flow

1) `AppendUserMessage` appends the incoming user message to any loaded `chat_history`.
2) `Agent` generates an assistant reply.
3) `AppendAssistantMessage` appends the assistant reply to `chat_history`.
4) `FinalOutput` returns the full `chat_history` so you can see persistence.

## Running locally (sandbox)

```bash
poetry run python -m examples.workflows.chatbot_set_state.sandbox
```

## Running interactively with state persistence

```bash
poetry run python -m examples.workflows.chatbot_set_state.chat
```

After the first run, copy the printed `previous_execution_id` to resume the conversation and see the accumulated `chat_history` emitted from `FinalOutput`.

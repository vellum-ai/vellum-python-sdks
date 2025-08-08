#!/usr/bin/env python3
"""
Trust Center Q&A Local Demo Runner (Zero-Config Monitoring)

This script runs the `trust_center_q_a` example workflow using Vellum's local SDK code
and prints a Monitoring URL so you can view the execution in Vellum.

Soon this monitoring url feature will be available in the SDK for all workflow executions!

Requirements:
- Set VELLUM_API_KEY in your environment
- Python 3.9+

Usage:
    export VELLUM_API_KEY="your-api-key"
    python3 external.py
"""
import importlib
import os
import sys
import time

# Ensure local repo src and ee are on sys.path so we pick up local SDK code
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../.."))
SRC_DIR = os.path.join(REPO_ROOT, "src")
EE_DIR = os.path.join(REPO_ROOT, "ee")
EXAMPLES_WORKFLOWS_DIR = os.path.join(REPO_ROOT, "examples", "workflows")
for path in [SRC_DIR, EE_DIR, EXAMPLES_WORKFLOWS_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Patch `vellum_ee.workflows.display.vellum` to include display data classes from `display.base`
# without removing existing exports like NodeInput/NodeInputValuePointer.
try:
    base_mod = importlib.import_module("vellum_ee.workflows.display.base")
    vellum_mod = importlib.import_module("vellum_ee.workflows.display.vellum")
    setattr(vellum_mod, "WorkflowDisplayData", base_mod.WorkflowDisplayData)
    setattr(vellum_mod, "WorkflowDisplayDataViewport", base_mod.WorkflowDisplayDataViewport)
    sys.modules["vellum_ee.workflows.display.vellum"] = vellum_mod
except Exception:
    pass

from trust_center_q_a.inputs import Inputs
from trust_center_q_a.workflow import Workflow  # type: ignore

from vellum.client.types import ChatMessage
from vellum.workflows.emitters.vellum_emitter import VellumEmitter  # local SDK emitter

print("🎯 Trust Center Q&A Local Demo (Zero-Config Monitoring)")
print("=" * 50)

# In this local demo, we:
# 1. Use local SDK modules via sys.path
# 2. Patch display module compatibility for the example
# 3. Instantiate the Trust Center Q&A workflow
# 4. Attach the local VellumEmitter for monitoring
# 5. Provide a sample user question as chat_history
# 6. Print the Monitoring URL derived from the workflow context

print("\n📋 Creating Trust Center Q&A workflow...")
# Explicitly pass the local VellumEmitter instance so the workflow uses it
workflow = Workflow(emitters=[VellumEmitter()])

print("\n🏃 Running Trust Center Q&A workflow...")
print("   (Monitoring URL will be printed automatically if enabled)")

# Minimal required inputs for this workflow
sample_question = "What security certifications does Vellum have?"
inputs = Inputs(chat_history=[ChatMessage(role="USER", text=sample_question)])

# Run the workflow - monitoring URL will be automatically printed!
result = workflow.run(inputs=inputs)

print(f"\n✅ Workflow completed! \n")


span_id = str(getattr(result, "span_id", ""))
if span_id:
    # Make sure all events are published to clickhouse before printing the link.
    print("   Preparing Monitoring URL. Waiting ~15 seconds so all events can be published to clickchouse...")
    print("   If details fail to load, refresh the page a few times until it shows up.\n")

    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    start_time = time.time()
    i = 0
    while time.time() - start_time < 15:
        dots = "." * (i % 10)
        frame = frames[i % len(frames)]
        sys.stdout.write(f"\r   {frame} Publishing events{dots:<9}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r   ✓ Events published. Generating link...       \n")

    url = workflow.context.get_monitoring_url(span_id)
    if url:
        print(f"   Monitoring URL: {url} \n")
else:
    print("   No span_id available to construct monitoring URL.\n")

print("\n🎉 Trust Center Q&A demo complete!")

#!/usr/bin/env python3
"""Pipeline checkpoint/resume system — persist progress across runs."""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime


CHECKPOINT_FILE = ".pipeline_state.json"


@dataclass
class StepState:
    """State of a single step for a single page."""
    completed: bool = False
    timestamp: str = ""
    error: str = ""


@dataclass
class PipelineState:
    """Full pipeline state persisted to disk."""
    config_path: str = ""
    started_at: str = ""
    updated_at: str = ""
    # page_num -> step_name -> StepState
    pages: dict = field(default_factory=dict)  # dict[str, dict[str, dict]]


class CheckpointManager:
    """Manages pipeline checkpoint state for resume capability."""

    def __init__(self, project_dir: str):
        self.state_path = os.path.join(project_dir, CHECKPOINT_FILE)
        self.state = PipelineState()

    def load(self) -> bool:
        """Load existing checkpoint. Returns True if found."""
        if not os.path.exists(self.state_path):
            return False
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.state = PipelineState(
                config_path=data.get("config_path", ""),
                started_at=data.get("started_at", ""),
                updated_at=data.get("updated_at", ""),
                pages=data.get("pages", {}),
            )
            return True
        except (json.JSONDecodeError, KeyError):
            return False

    def save(self) -> None:
        """Persist current state to disk."""
        self.state.updated_at = datetime.now().isoformat()
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(asdict(self.state), f, indent=2, ensure_ascii=False)

    def init_run(self, config_path: str) -> None:
        """Initialize a new run (only if no existing state)."""
        if not self.state.started_at:
            self.state.config_path = config_path
            self.state.started_at = datetime.now().isoformat()
            self.save()

    def is_completed(self, page_num: int, step_name: str) -> bool:
        """Check if a specific step for a page is already completed."""
        page_key = str(page_num)
        if page_key not in self.state.pages:
            return False
        step_data = self.state.pages[page_key].get(step_name, {})
        return step_data.get("completed", False)

    def mark_completed(self, page_num: int, step_name: str) -> None:
        """Mark a step as completed for a page and save."""
        page_key = str(page_num)
        if page_key not in self.state.pages:
            self.state.pages[page_key] = {}
        self.state.pages[page_key][step_name] = {
            "completed": True,
            "timestamp": datetime.now().isoformat(),
            "error": "",
        }
        self.save()

    def mark_failed(self, page_num: int, step_name: str, error: str) -> None:
        """Mark a step as failed for a page."""
        page_key = str(page_num)
        if page_key not in self.state.pages:
            self.state.pages[page_key] = {}
        self.state.pages[page_key][step_name] = {
            "completed": False,
            "timestamp": datetime.now().isoformat(),
            "error": error,
        }
        self.save()

    def get_summary(self) -> dict:
        """Get summary of completed/pending/failed steps."""
        summary = {"completed": 0, "failed": 0, "pending": 0}
        for page_key, steps in self.state.pages.items():
            for step_name, step_data in steps.items():
                if step_data.get("completed"):
                    summary["completed"] += 1
                elif step_data.get("error"):
                    summary["failed"] += 1
                else:
                    summary["pending"] += 1
        return summary

    def reset(self) -> None:
        """Reset checkpoint (for --no-resume)."""
        self.state = PipelineState()
        if os.path.exists(self.state_path):
            os.unlink(self.state_path)

    def print_status(self) -> None:
        """Print current checkpoint status."""
        if not self.state.started_at:
            print("  No previous checkpoint found")
            return

        summary = self.get_summary()
        print(f"  Checkpoint: {self.state_path}")
        print(f"  Started: {self.state.started_at}")
        print(f"  Last update: {self.state.updated_at}")
        print(f"  Completed: {summary['completed']}, "
              f"Failed: {summary['failed']}, "
              f"Pending: {summary['pending']}")

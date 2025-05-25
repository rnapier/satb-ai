# Scripts Directory

This directory contains analysis and debugging tools for the SATB Splitter project. These scripts are useful for development, troubleshooting, and understanding the behavior of the voice separation system.

## Analysis Tools

### `analyze_score_structure.py`
Comprehensive diagnostic tool to analyze score structure and voice distribution. Provides detailed analysis of how SATB scores are structured to inform deterministic voice mapping rules.

**Usage:** `python scripts/analyze_score_structure.py`

**Features:**
- Analyzes part structure and voice distribution
- Evaluates current heuristic system results
- Provides deterministic mapping recommendations
- Measure-by-measure variation analysis

### `demo_lyric_assignment.py`
Demonstration of the lyric assignment feature. Shows how lyrics are distributed across voices and saves processed results.

**Usage:** `python scripts/demo_lyric_assignment.py`

**Features:**
- End-to-end lyric assignment demonstration
- Before/after comparison
- Output file verification

## Debug Tools

### `debug_crescendo_analysis.py`
Analyzes how crescendos are stored in the original score vs separated parts. Searches for direction elements, crescendos, wedges, and dynamics throughout the score.

**Usage:** `python scripts/debug_crescendo_analysis.py`

### `debug_crescendo_location.py`
Finds exactly where crescendos are located in the score structure at different levels (score, part, spanner).

**Usage:** `python scripts/debug_crescendo_location.py`

### `debug_crescendo_references.py`
Analyzes spanner note references in detail to understand how crescendos are linked to specific notes and whether those references are preserved during voice separation.

**Usage:** `python scripts/debug_crescendo_references.py`

### `debug_save_load_issue.py`
Tests if spanners are lost during the save/load process by comparing in-memory scores with exported files.

**Usage:** `python scripts/debug_save_load_issue.py`

### `debug_spanner_copying.py`
Tests if spanners are being copied properly during voice separation by comparing original and processed scores.

**Usage:** `python scripts/debug_spanner_copying.py`

### `debug_which_crescendo_lost.py`
Identifies which specific crescendos are preserved vs lost during the voice separation process.

**Usage:** `python scripts/debug_which_crescendo_lost.py`

## Notes

- All scripts expect to be run from the project root directory
- Most scripts use "Crossing The Bar.musicxml" as the test file
- Debug scripts are particularly useful when troubleshooting spanner/dynamics preservation issues
- These tools were instrumental in diagnosing and fixing crescendo preservation bugs

## Running Scripts

From the project root directory:
```bash
python scripts/script_name.py
```

Make sure the required dependencies are installed:
```bash
pip install -r requirements.txt
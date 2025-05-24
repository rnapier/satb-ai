You are an AI coding assistant. Your task is to help me build a Python command-line tool called **satb-split** that takes a MuseScore `.mscz` file containing a closed-score SATB layout (2 staves, 4 voices) and produces:

1. A new `.mscz` file with four separate staves (Soprano, Alto, Tenor, Bass), each containing only one voice.
2. Four audio exports (WAV or MP3), one per part.

---

# Requirements

* **Language & Libraries**

  * Python 3.9+
  * [ms3](https://github.com/johentsch/ms3) for parsing/writing `.mscz` & `.mscx`
  * Standard `zipfile`, `os`, `argparse`, etc.
  * You MUST manage Python with `uv`.

* **Functionality**

  1. **Unzip** the input `.mscz` into a temp folder.
  2. **Parse** `score.mscx` with ms3.Score and extract note data.
  3. **Separate** notes by `staff` & `voice`:

     * Staff 1, Voice 1 → Soprano
     * Staff 1, Voice 2 → Alto
     * Staff 2, Voice 1 → Tenor
     * Staff 2, Voice 2 → Bass
  4. **Create** four new staves in the score, assign each group of notes to its own staff (all in voice 1), and remove or hide the original 2-staff layout.
  5. **Save** the modified score back to `<original_name>-exploded.mscz`.
  6. **Export Audio** by invoking the MuseScore CLI (`mscore`):

     ```bash
     mscore -o soprano.mp3 -p "Soprano" <original_name>-exploded.mscz
     mscore -o alto.mp3    -p "Alto"    <original_name>-exploded.mscz
     …  
     ```

* **CLI Interface**

  ```bash
  satb-split input.mscz \
               --output exploded.mscz \
               --audio-format mp3 \
               --parts soprano alto tenor bass
  ```

* **Error Handling & Validation**

  * Verify input file exists and is a valid `.mscz`.
  * Clean up temp files on error or success.
  * Informative logging at each major step.

* **Deliverables**

  * Complete Python source for each module.
  * `setup.py` with console entry point.
  * Unit tests covering voice separation and file I/O.
  * A brief `README.md` with install & usage instructions.

# Development plan

You will build this step by step, and ask for me to approve each step. The steps will be as follows:

* Phase 0 - Create basic stub application
  * This should have minimal functionality and avoid excessive scaffolding code.
  * Do not create each commandline option until it is actually needed.
  * At the end of this phase, the program should run using `uv` and just print basic help
* Phase 1 - Parse a mscz file using ms3 and output its contents.
* Phase 2 - Identify the notes, dynamics, and lyrics for each part and output their contents
* Phase 3 - Unify the parts as needed:
  * In closed-staff SATB, dynamics may only be applied to the Soprano part, in which case the dynamic applies to all parts.
  * Dynamics may also be applied to both Soprano and Bass. If they are the same, they apply to all parts.
  * If there are lyrics applied only to the Soprano part, they generally apply to all parts.
  * Special care may be required for situations where the parts have different lyrics.
* Phase 4 - Create a new open staff mscz file
* Phase 5 - Create MP3 file for each part

First, you will build an overall project plan and a progress checklist to keep track of where you are.
When that is approved, you will move forward.

# Behaviors

* Strongly favor using `ms3` functionality. DO NOT try to directly parse the MSCZ file.
  * Read docs/ms3.txt for full documentation on ms3.
  * DO NOT peek at implementation details like `hasattr` unless this is how the ms3 documentation suggests accessing the data.
  * WRITE SIMPLY. Do not include fall-backs. If there is an error, generate an error and terminate the program. If data is missing, use None to indicate that.
  * DO NOT use `hasattr` or `getattr` to peek into internal details. USE THE PUBLIC API.
* If you have trouble or if something does not make sense, stop and ask for help. Do not search for work-arounds.
* Use `git` to manage version control. Commit at the end of each Phase.
* Use "Crossing The Bar.mscz" for testing.
* You MUST ask permission before moving onto another phase.
* A phase is not complete until all of its features are complete.
* Strongly favor maintainability of the code. It should not be clever or use work-arounds.
* After any command that might have ambiguous completion, such as multi-line commands, add a simple command like `echo "COMMAND_COMPLETE"` to help find the end.
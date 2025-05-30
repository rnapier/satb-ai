You are an AI coding assistant. Your task is to help me build a Python command-line tool called **satb-split** that takes a MuseScore `.mscz` file containing a closed-score SATB layout (2 staves, 4 voices) and produces:

1. A new `.mscz` file with four separate staves (Soprano, Alto, Tenor, Bass), each containing only one voice.
2. Four audio exports (WAV or MP3), one per part.

---

# Requirements

* **Language & Libraries**

  * Python 3.9+
  * [music21](https://web.mit.edu/music21/) for parsing/writing music scores
  * Standard `argparse`, `pathlib`, etc.
  * You MUST manage Python with `uv`.

* **Functionality**

  1. **Parse** input `.mscz` file using music21.converter.parse()
  2. **Extract** voice data from the score structure:

     * Part 1, Voice 1 → Soprano  
     * Part 1, Voice 2 → Alto
     * Part 2, Voice 1 → Tenor
     * Part 2, Voice 2 → Bass
  3. **Separate** notes, dynamics, and lyrics by voice using music21's voice handling
  4. **Create** four new music21.stream.Part objects, assign each group of notes to its own part (all in voice 1)
  5. **Export** to MusicXML then convert back to `.mscz` using MuseScore CLI:
     ```bash
     # Export modified score to MusicXML
     score.write('musicxml', '<original_name>-exploded.xml')
     # Convert to MSCZ using MuseScore
     mscore -o <original_name>-exploded.mscz <original_name>-exploded.xml
     ```
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

  * Verify input file exists and is a valid `.mscz` or `.musicxml`.
  * Handle music21 parsing errors gracefully.
  * Informative logging at each major step.

* **Deliverables**

  * Complete Python source for each module.
  * `pyproject.toml` with console entry point.
  * Unit tests covering voice separation and file I/O.
  * A brief `README.md` with install & usage instructions.

# Development plan

You will build this step by step, and ask for me to approve each step. The steps will be as follows:

* Phase 0 - Create basic stub application using music21 ✅ COMPLETE
  * This should have minimal functionality and avoid excessive scaffolding code.
  * Do not create each commandline option until it is actually needed.
  * At the end of this phase, the program should run using `uv` and just print basic help
* Phase 1 - Parse music files using music21 and output their contents.
* Phase 2 - Identify the notes, dynamics, and lyrics for each voice and output their contents
* Phase 3 - Unify the parts as needed:
  * In closed-staff SATB, dynamics may only be applied to the Soprano part, in which case the dynamic applies to all parts.
  * Dynamics may also be applied to both Soprano and Bass. If they are the same, they apply to all parts.
  * If there are lyrics applied only to the Soprano part, they generally apply to all parts.
  * Special care may be required for situations where the parts have different lyrics.
* Phase 4 - Create a new open staff score using music21 and export to MusicXML/MSCZ
* Phase 5 - Create MP3 file for each part

First, you will build an overall project plan and a progress checklist to keep track of where you are.
When that is approved, you will move forward.

# Behaviors

* Strongly favor using `music21` functionality. DO NOT try to directly parse the MSCZ file.
  * Use music21.converter.parse() for file input
  * Use music21's Stream, Part, Voice, and Note classes for manipulation
  * DO NOT peek at implementation details like `hasattr` unless this is how the music21 documentation suggests accessing the data.
  * WRITE SIMPLY. Do not include fall-backs. If there is an error, generate an error and terminate the program. If data is missing, use None to indicate that.
  * DO NOT use `hasattr` or `getattr` to peek into internal details. USE THE PUBLIC API.
* If you have trouble or if something does not make sense, stop and ask for help. Do not search for work-arounds.
* Use `git` to manage version control. Commit at the end of each Phase.
* Use "Crossing The Bar.mscz" and "Crossing The Bar.musicxml" for testing.
* You MUST ask permission before moving onto another phase.
* A phase is not complete until all of its features are complete.
* Strongly favor maintainability of the code. It should not be clever or use work-arounds.
* After any command that might have ambiguous completion, such as multi-line commands, add a simple command like `echo "COMMAND_COMPLETE"` to help find the end.

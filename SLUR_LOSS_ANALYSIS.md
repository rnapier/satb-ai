# Slur Loss Analysis - Minimal Reproduction Approach

## 🔍 Current Situation

**Problem**: Slurs in measure 29 are not appearing in exported Alto, Tenor, Bass voices despite being present in original score.

**False Positive Tests**: Current tests detect slurs in memory but they don't appear in actual MusicXML export.

## 📋 Original Measure 29 Slurs (Confirmed in source)
- **Alto (voice 2)**: E4 → F4 slur with `<slur type="start/stop" number="1"/>`
- **Tenor (voice 5)**: B3 → A3 slur with `<slur type="start/stop" number="1"/>`
- **Bass (voice 6)**: E3 → D3 slur with `<slur type="start/stop" number="1"/>`

## 🚫 Current Output (Broken)
- Alto measure 29: NO slur notations on any notes
- Tenor measure 29: NO slur notations on any notes
- Bass measure 29: NO slur notations on any notes

## 📋 Minimal Reproduction Plan

### Step 1: Simple Music21 Test
Create minimal script to test:
1. Load original score
2. Extract just measure 29
3. Check slur preservation in basic music21 operations

### Step 2: Voice Separation Test
Test each step in current voice separation:
1. Load score → Check slurs ✓/❌
2. Copy score → Check slurs ✓/❌
3. Remove voices → Check slurs ✓/❌
4. Simplify → Check slurs ✓/❌
5. Export → Check slurs ✓/❌

### Step 3: Identify Exact Breaking Point
Find the precise operation where slurs get lost.

### Step 4: Minimal Fix
Apply the simplest possible fix at the breaking point.

## 🎯 Hypothesis
Slurs break when:
- Voice removal removes the notes that slurs reference
- Music21 can't resolve slur references after voice separation
- Export process drops broken slur references

## 📝 Simple Solution Strategy
Instead of complex spanner processing:
1. **Preserve slur references during voice operations**
2. **Ensure slurred notes remain properly linked**
3. **Fix any broken references before export**

## 🚀 Next Steps
1. Switch to code mode to implement minimal reproduction
2. Identify exact breaking point
3. Implement simplest fix
4. Test real export (not just memory)
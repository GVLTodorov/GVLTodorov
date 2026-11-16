I'm attaching two subtitle files for the same movie:
- English SRT: the original subtitles and the timing reference.
- Bulgarian SRT: a machine translation of the English.

Do two things and give me back ONE corrected Bulgarian SRT.

PART 1 – Timing
1. Match each Bulgarian cue to its English cue by meaning and context, not by
   number. (If cue counts and start times are identical, a one-to-one match is fine.)
2. Keep the Bulgarian start times.
3. Target duration = English duration + 0.5 s. If the Bulgarian cue is already
   longer, keep its length.
4. Never overlap the next cue. If the full extension doesn't fit, extend up to
   1 ms before the next cue starts.
5. Handle cases where one English cue maps to several Bulgarian cues, or the reverse.
6. Keep SRT numbering, encoding and timestamp format (HH:MM:SS,mmm).

PART 2 – Translation review
Read EVERY cue next to its English line and fix the Bulgarian:
- Wrong meaning, idioms translated literally, slang and military terms
  (LZ, chaplain, parole, deploy, etc.).
- Gender and number agreement (speaker's and addressee's gender, singular vs.
  plural "you", noun gender of the referenced object).
- Sentences split across two lines: no stray full stop or capital at the line
  break; join them naturally.
- Dialogue dashes "- " on both lines when the English has two speakers.
- Italics <i></i> wherever the English uses them.
- Natural, spoken Bulgarian at a similar length to the original. Keep the swearing
  level. Don't over-polish lines that are already correct.
Change only what's wrong; keep good lines as they are.

OUTPUT
- The complete corrected Bulgarian .srt as a downloadable file (no commentary inside it).
- A separate list of cues that couldn't get the full +0.5 s (cue number, how much
  was missing).
- A short summary of the main kinds of translation errors fixed, with a few examples.

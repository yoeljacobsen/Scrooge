# wavstat: design

A worked example of the method in the skill guide (sections 0b and 0d): written before the code, then kept true.

## What it does

`wavstat FILE.wav` prints the channel count, sample rate and length of a 16-bit PCM WAV file, and the peak and RMS level of each channel. Bad input stops with one line, `wavstat: FILE: reason`, and status 1. The file is read as a stream, a buffer at a time, so memory does not grow with the file.

## Layers, one module each, bottom up

| module | what it does | library words it uses |
|---|---|---|
| `err.sg` | the one way to stop on bad input: the error line, then `1 exit` | `f_stderr`, `fwrite`, `exit`; tested with `expect_stop` |
| `wav.sg` | open the file, check the RIFF header, read the `fmt ` chunk, skip other chunks, then give the samples a buffer at a time | `f_open_read`, `bytes_read` (streaming into one Bytes), `bytes_le16`, `bytes_le32`, `fclose` |
| `stats.sg` | the peak and RMS of each channel, one sample at a time | `to_float`, `sqrt`; compact fields in a `#record` |
| `wavstat.sg` | the command line, the loop over the buffers, the report | `arg_or`, `str_print`, `print_int`, `print_float` |

Each module has `#test_` words (`--test`); the error paths have stop tests (`expect_stop`), which check the message.

## State

- `Wav` (`#record`): the path (for messages), the open File, one 4096-byte buffer made once by the record's `_new`, the channel count, rate, bits, and the data bytes left.
- `Acc` (`#record`): per channel (up to 8) the peak, the sum of squares and the count.

Nothing is allocated inside the loop over the buffers.

## Order of work

1. `err.sg` and its stop test.
2. `wav.sg` far enough to open the file and check the header, with the end to end program printing only the format: the whole pipeline runs from the first hour.
3. The `fmt ` and `data` chunks, then `wav_read` and `wav_sample`. Each test writes the small WAV file it reads (`_test_file`: a header and frames of known values, a wrong first id, or a file cut short), so the tests say what is in their input and run from any directory. `tone.wav` (made with Python's `wave` module, 800 frames of a 440 Hz tone and a square wave) and `cut.wav` are for running the program by hand.
4. `stats.sg`, tested on numbers whose answer is known (a half-scale square wave has RMS 0.5).
5. The report.

## Signatures (the promises the checker holds)

```
die        ( path:Block reason:Block -- )   never returns
wav_open   ( path:Block -- w:Wav )
wav_read   ( w:Wav -- n:Int )               bytes now in the buffer, whole frames; 0 at the end
wav_sample ( w:Wav k:Int -- s:Int )         sample k of the buffer, -32768 .. 32767
acc_add    ( a:Acc c:Int s:Int -- )
acc_peak   ( a:Acc c:Int -- p:Int )
acc_rms    ( a:Acc c:Int -- r:Float )       a fraction of full scale
```

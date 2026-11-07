# Word banks

The reviewable Markdown files are the source of truth. `python3 scripts/wordlists.py`
validates exact counts, case, normalized uniqueness and the two excluded default
answers, then generates `desk/lib/ursketch-words.hoon`. The ordinary app build also
runs this validation. `artifacts/wordlists-verification.json` records counts and
SHA-256 hashes of the files used for the release.

| File | Entries | Direction |
| --- | ---: | --- |
| [default](../wordlists/default.md) | 2,000 | Concrete objects, animals, foods, places, activities and familiar phrases. |
| [easy](../wordlists/easy.md) | 500 | Familiar subjects with recognizable silhouettes and everyday associations. |
| [hard](../wordlists/hard.md) | 500 | Scientific concepts, emotions, idioms and more specialized objects. |
| [Urbit](../wordlists/Urbit.md) | 500 | Platform, identity, networking and Hoon terms, documented rune names and real standard-library arms. |

The default bank retains the earlier entries except `delivery van` and
`fire engine`. Banks may intentionally share words; each bank has no normalized
duplicates. A room's previous 100 assignments remain excluded when switching
banks or difficulty. Default/easy/hard/Urbit are functional choices; Milady Words
is a disabled placeholder with the requested placeholder explanation.

Urbit terminology was checked against the [official Arvo overview](https://docs.urbit.org/build-on-urbit/app-school/1-arvo),
[Hoon rune reference](https://docs.urbit.org/hoon/rune), and
[official Hoon source](https://github.com/urbit/urbit/blob/master/pkg/arvo/sys/hoon.hoon).
The last 92 entries in the Urbit bank are actual standard-library arm names.
These are technical drawing prompts, rather than 500 invented project names.

Room owners can combine the available banks. Easy/Hard difficulty substitutes
that bank for the artist's turn, with per-player overrides taking precedence.
The room's default setting uses the selected checkboxes. Changes affect future
assignments, leaving the current secret word intact.

Custom Markdown uploads accept one word/phrase per line, optionally bulleted or
numbered. Headings, fenced blocks, block quotes and table rows are ignored.
Uploads are limited to 256 KB, 101–5,000 unique entries, 64 plain-text characters
per entry and five custom lists per room. Requiring at least 101 entries keeps
strict last-100 exclusion possible. The host rechecks these limits and ownership.
Custom bank contents stay on the host; ordinary room updates carry only list
IDs/counts, not the full banks.

The four release Markdown files were posted as separate new notes named
`default`, `easy`, `hard`, and `Urbit` in On-Nomi Chuds → Notebook2. Each note was
read back and compared with its source file. The private notebook's IDs and
session credentials are not included in the repository.

# Spider-Man · Tobey Maguire

The theme follows the user's three supplied Raimi-era film references: burgundy
suit fabric, raised silver webbing, midnight blue and warm New York light.
Spider-Man leads the Connect and room-browser artwork. Green Goblin is a single
40px cameo in the theme preview, rather than a competing background character.

The unmodified supplied PNGs are copied into `desk/media/themes/spider-man/`:

- `swing.png`: Screenshot 2026-11-04 at 23-39-58 tobey maguire spider man - Google Search.png
- `peter.png`: Screenshot 2026-11-04 at 23-39-53 tobey maguire spider man - Google Search.png
- `goblin.png`: Screenshot 2026-11-04 at 23-40-39 green goblin - Google Search.png

`spider-man-badge.svg` and `spider-man-pattern.svg` are editable vector artwork.
CSS provides the photo framing and fades; the source images remain intact.
Assets are served from the player's own ship through authenticated,
content-addressed media routes, with no third-party image requests.

An initial built-in imagegen request for a cinematic masked Spider-Man backdrop
failed; no generated bitmap is used in this release. Its requested direction was:
"Tobey Maguire's Spider-Man in burgundy and navy with raised silver webbing,
crouching over New York at sunset; tiny distant Green Goblin; quiet navy space
for UI; no text or logos." The final theme uses the actual user-provided film
references instead.

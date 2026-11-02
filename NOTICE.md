# Classic control graphics

Original, unmodified reference graphics from iSketch's drawing instructions:

- https://www.isketch.net/instructions/gfx/tools.gif
- https://www.isketch.net/instructions/gfx/hint.gif
- https://www.isketch.net/instructions/gfx/done.gif

Retrieved October 27, 2026. Attribution: iSketch, https://www.isketch.net/.
The Classic theme uses these as CSS sprites behind functional urSketch controls.
The builder embeds them locally; the running app makes no request to iSketch.

`metal.svg` and `metal-small.svg` are urSketch's own vector backgrounds,
reconstructed from sampled reference colors with two light scanlines and one
dark scanline per three pixels. They are not downloaded iSketch assets.


## Intro footage and music

The owner supplied `iSketch Intro Theme (Remastered).mp4` as the reference and
source media. The shipped animation's video packets are copied intact with
its audio stored separately as `theme_song.mp3`; the original wordmark is
covered by a urSketch logo overlay. This source credit identifies the supplied
material and does not imply authorship or affiliation. The original footage
and music are not represented as newly authored urSketch artwork.

The username-screen layout and silver logo-gradient reference were supplied by
the owner in login.png. The new page is implemented in native HTML/CSS/SVG;
the two people and the reference logo image are not included. Its separate
urSketch logo variant uses the owner-selected canonical urSketch PNG with a
silver-blue gradient whose colours were sampled from that reference.

The room-browser styling reference was supplied by the owner in room browser.png.
The new HTML/CSS browser uses urSketch's existing logo and functional room data;
the reference's people, Studio and language-category controls are not included.

Character artwork: 25 user-supplied urSketch cat SVGs (6 bodies, 9 faces and
10 hats), copied unchanged into `desk/media/characters/`. Layer registration
and selector controls are implemented in the application's own code.

Fireworks audio and pencil SVG: user-supplied files, copied unchanged as
`desk/media/audio/cues/Fireworks.mp3` and `desk/media/images/pencil.svg`.

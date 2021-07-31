<div align="center">
<h1>UVP Media Player</h1>
<h3>Urban Video Project's cross-platform immersive media player</h3>
<i><a href="https://www.lightwork.org/uvp">Urban Video Project</a> is a program of <a href="https://www.lightwork.org">Light Work</a> in partnership with the <a href="https://everson.org">Everson Museum of Art.</a></i>
<hr style="height:1px">
</div>

UVP Media Player is purpose-built for use with it's accompanying web app to enable live/in-person audience interaction with immersive media/360 video presentations via audience members' mobile devices. In addition, most features also support standard 2D video playback.

# Install

Download the [latest release](https://github.com/garytyler/uvp-media-player/releases) for Linux, Mac, or Windows.

# Support

To submit questions or feedback, please [submit an issue](https://github.com/garytyler/uvp-media-player/issues).

# Build

For info on how to build this project on Linux, Windows or Mac, please see the CI [build script](https://github.com/garytyler/uvp-media-player-ci/blob/master/.github/workflows/build.yml)

# Application Environment Variables

- `VLC_ARGS`
  - Args that will be passed to vlclib on launch
- `VR_PLAYER_LOG_FILE`
  - File path to output logs to
- `VR_PLAYER_LOG_LEVELS`
  - Comma-delimited (`,`) list of Colon-delimited (`:`) name/value pairs
  - Use "`root`" for name of default logger

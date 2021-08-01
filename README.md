<div align="center">

<h1>UVP Media Player</h1>
<h3>Urban Video Project's cross-platform immersive media player</h3>
<i><a href="https://www.lightwork.org/uvp">Urban Video Project</a> is a program of <a href="https://www.lightwork.org">Light Work</a> in partnership with the <a href="https://everson.org">Everson Museum of Art.</a></i>

<h1></h1>

<a href="https://github.com/garytyler/uvp-media-player/actions">
  <img alt="Actions Status" src="https://github.com/garytyler/uvp-media-player/workflows/build/badge.svg">
</a>

<a href="https://codecov.io/gh/garytyler/uvp-media-player">
  <img src="https://codecov.io/gh/garytyler/uvp-media-player/branch/master/graph/badge.svg?token=FSRLTC94EF"/>
</a>

<img alt="GNU" src="https://img.shields.io/github/license/garytyler/uvp-media-player">

</div>

# Overview

UVP Media Player is purpose-built for use with UVP's [web app](https://github.com/garytyler/uvp-web) that facilitates live/in-person audience interaction with immersive media/360 video presentations via audience members' mobile devices. In addition, most features also support standard 2D video playback.

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

# TD Build TOX Package GitHub Action

A repository for a github action that facilitates CI operations for TouchDesigner.

SudoMagic has identified a repeatable pattern for automating the process of creating `TOX` files from a host TouchDesigner `TOE` file. This is particularly helpful if you're looking to create repeatable patterns for building out releases on GitHub using their automation pipelines.

While it's not currently practical to use the hosted images on GitHub, at SudoMagic we find that using [Self Hosted Runners](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners) is a viable alternative being able to both leverage the automation patterns from github's actions paradigm, while also ensuring that you control the hardware on which it's built.

## Behavior Overview

This action follows an automation pattern that assumes the following order of operations:

1. Pull repo and any submodules
2. Load the contents of a `json` file that holds build settings for the project.
3. Verify that the buildSettings file contains all required elements
4. Set environment variables provided by buildSettings to be used by the project `TOE` file
5. Create output directories for uploading assets
6. Start a blocking subprocess with the `TOE` file from buildSettings with a specified version of TouchDesigner
7. When the `TOE` file closes, iterate through the contents of a log file and send the contents to the git actions cloud console
8. Clean up all environment variables

## Machine Set-up and Configuration

This action's primary functionality is focused on:
* producing a repeatable pattern for starting a host `TOE` file with a specific version of TouchDesigner
* passing environment variables to that host `TOE` file
* cleaning up any left-over environment variables from that process
* echoing any log statements from the host `TOE` file to the actions log
* managing the output of the host `TOE` file so that it can be uploaded as a release by another action

Given those constraints, it is the responsibility of the host `TOE` file to handle any other operational considerations. It also the responsibility of the host `TOE` file to exit it's operation when any build automation steps are complete. 

As a reminder, you can use the following to force quit any TouchDesigner project. The following would be included after your `TOE` file had completed any operations required for it's automation steps.

```python
project.quit(force=True)
```

### Configuring your self hosted runner

This action does not attempt to install Python (currently required for the operation of this action) or TouchDesigner. Please ensure that in the configuration of your self hosted runner that both of these are installed on the operating host hardware. 


### Dependencies

* Python 3.11 or later
* TouchDesigner installed in a version specific directory i.e. `C:\Program Files\Derivative\TouchDesigner.2023.12370`

### Additional Limitations
* Currently only tested on Windows 11

## Build Settings

_Required keys_
```json
{
    "BUILD": "TRUE",
    "TD_VERSION": "2023.12230",
    "PROJECT_FILE": "./TouchDesigner/project.toe",
    "COMP_NAME": "Example Comp",
    "BUILD_CONTENTS" : "packageZip",
    "USE_TDM": false
}
```


The required keys server some specific utility in the automation process. Their behavior is outlined below.

Key | Data Type | Options | Description |
--- | --- | --- | ---|
`BUILD`             | `str` | `TRUE` or `FALSE` | A flag that can be used for controlling the build state of your host TOE file. 
`TD_VERSION`        | `str` | any               | The desired version of TouchDesigner you'd like to open the project with.
`PROJECT_FILE`      | `str` | any               | A path to the target TOE file from the root of the repository.
`COMP_NAME`         | `str` | any               | A name for the component you're creating 
`BUILD_CONTENTS`    | `str` | `packageZip` or `toxFiles` | This build action can output a single .zip file "packageZip" where the output contents are zipped together into a single file, or it can output as may single files as are produced by the host TOE file. Use `packageZip` if you'd like the content of a directory to be zipped up into a single file.
`USE_TDM`           | `bool` | `True` or `False` | SudoMagic has an early TouchDesigner Dependency Manager that's used for internal development. This is currently for SudoMagic development only.


All of the above keys will be passed to TouchDesigner as Environment Variables on start-up. You can add any additional key-value pairs that you require for your build process. All Environment variables are set-up when TouchDesigner launches, and then are garbage collected after TouchDesigner exists.


## Use

`td-build-tox-package-gh-action`

```yaml
      - name: Python TD Builder
        uses: ./
        with:
          build_settings: ./buildSettings.json
```

### Example Workflow

```yaml
name: Create realse from Main
on:
  push:
    branches:
      - main

jobs:
  Build_tox:
    runs-on: [self-hosted, Windows, TouchDesigner]
    steps:
      - name: Check out repository code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          fetch-tags: true
          submodules: true 

      - name: SudoMagic TD Package Builder
        uses: SudoMagicCode/action-build-td-tox-package@v0.0.1
        with:
          build_settings: ./buildSettings.json
          
      - name: Release
        uses: softprops/action-gh-release@v2
        if: startsWith(github.ref, 'refs/tags/')
        with:
          files: ./release/package.zip

```


## Example Repos


### A Repository that produces a .zip file
[TD TOX Builder Template](https://github.com/SudoMagicCode/td-tox-builder-template)  
This repository is intended to act as boiler plate and starting point for any automation based TouchDesigner repo. This repo pattern is built around the idea that you want to creat a single .zip file that acts as a TouchDesigner module that you want to release.

### A Repository that produces many `tox` files
[SudoMagic TouchDesigner Templates](https://github.com/SudoMagicCode/sm-td-templates)  
This repository acts generates many TOX files that are all bundled into a release. This pattern is most useful when the repo is read by another component and can fetch each of the TOX files listed.

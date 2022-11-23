# Python dev tools

The Python dev tools bundles a couple of tools that are not part of the SDK (yet).
The SDK can be found at <https://github.com/crownstone/crownstone-python-sdk>.

The dev tools are based on python libs:

* https://github.com/crownstone/crownstone-lib-python-ble
* https://github.com/crownstone/crownstone-lib-python-core
* https://github.com/crownstone/crownstone-lib-python-uart

If you are interested in creating your **own tools**, go to those repositories and study the example code there.

## Installation from PyPi

You can will be able to install these tools through pip soon:

```
pip install crownstone-devtools
```

## Installation from source

You can install these tools through pip also locally by:

```
git clone https://github.com/crownstone/crownstone-python-devtools
cd crownstone-python-devtools
pip install .
```

## Available tools

Currently, available tools are:

<details>
<summary> cs_bluenet_extract_logs_strings --sourceFilesDir dir --topDir dir --outputFile file [--help] [--verbose]</summary>

> This will extract logs to be used for the binary logger.
>
> - Parameters
>   - **sourceFilesDir**: The path with the precompiled bluenet source code files on your system (.i or .ii files)
>   - **topDir**: The full path to the `/source` directory of your bluenet repository.
>   - **outputFile**: The output file to be used by `cs_bluenet_log_client` (e.g. `extracted_logs.json`)
>   - **verbose**: Optional. More verbose output.
>   - **help**: Optional. Show help.
>
</details>

<details>
<summary> cs_bluenet_log_client --logStringsFile path --device dev [--plaintext] [--raw] [--hex] [--help] [--verbose]</summary>

> This will run a logger that parses logs from a UART device.
>
> - Parameters
>   - **logStringsFile**: The path of the file with the extracted logs on your system.
>   - **device**: The UART evice to use, e.g. `/dev/ttyACM0`.
>   - **plaintext**: Optional. Also print plaintext logs.
>   - **raw**: Optional. Show raw output (may result in interleaved print statements).
>   - **hex**: Optional. Show raw output as hex values.
>   - **verbose**: Optional. More verbose output.
>   - **help**: Optional. Show help.
>
</details>

<details>
<summary> cs_microapp_create_header [-i inputFile] outputFile </summary>

> Creates linker file to be used by microapps.
>
> - Parameters
>   - **inputFile**: Optional. The binary file to be processed to generate values for linker file.
>   - **outputFile**: Generate .ld file with default values if no inputFile is present. If inputFile is present it will calculate the appropriate values.
>   - **help**: Optional. Show help.
>
</details>

# License

## Open-source license

This software is provided under a noncontagious open-source license towards the open-source community. It's available under three open-source licenses:
 
* License: LGPL v3+, Apache, MIT

<p align="center">
  <a href="http://www.gnu.org/licenses/lgpl-3.0">
    <img src="https://img.shields.io/badge/License-LGPL%20v3-blue.svg" alt="License: LGPL v3" />
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" />
  </a>
  <a href="https://opensource.org/licenses/Apache-2.0">
    <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License: Apache 2.0" />
  </a>
</p>

## Commercial license

This software can also be provided under a commercial license. If you are not an open-source developer or are not planning to release adaptations to the code under one or multiple of the mentioned licenses, contact us to obtain a commercial license.

* License: Crownstone commercial license

# Contact

For any question contact us at <https://crownstone.rocks/contact/> or on our discord server through <https://crownstone.rocks/forum/>.

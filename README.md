<div align="center" id="top"> 
  <img src="./.github/app.gif" alt="Ene5ai Project" />

  &#xa0;

  <!-- <a href="https://ene5aiproject.netlify.app">Demo</a> -->
</div>

<h1 align="center">Ene5ai Project</h1>



<!-- Status -->

<!-- <h4 align="center"> 
	🚧  Ene5ai Project 🚀 Under construction...  🚧
</h4> 

<hr> -->

<p align="center">
  <a href="#dart-about">About</a> &#xa0; | &#xa0; 
  <a href="#sparkles-features">Features</a> &#xa0; | &#xa0;
  <a href="#rocket-technologies">Technologies</a> &#xa0; | &#xa0;
  <a href="#white_check_mark-requirements">Requirements</a> &#xa0; | &#xa0;
  <a href="#checkered_flag-starting">Starting</a> &#xa0; | &#xa0;
  <a href="#memo-license">License</a> &#xa0; | &#xa0;
  <a href="https://github.com/{{YOUR_GITHUB_USERNAME}}" target="_blank">Author</a>
</p>

<br>

## About ##

This module enables users to inspect network data and export the transform collected metrics via an API. The exposed metrics is compatible with Prometheus. It provides 2 modes: Sniff and Analyze, users can choose which suits them best. The Analyze mode will provide a report of network data provided by a input file while Sniff mode will inspect network package exchanged in real time and exposed timeseries metrics using Prometheus client API.
## Features ##

Sniff mode\
Analyze mode

## Technologies ##

The following tools were used in this project:

- [Python](https://www.python.org/)
- [stdeb](https://pypi.org/project/stdeb/)
- [Scapy](https://pypi.org/project/scapy/)
- [Prometheus](https://pypi.org/project/prometheus/)

## Starting ##

```bash
# Installation
$ sudo add-apt-repository ppa:rnd-smile/webstat
$ sudo apt-get update && sudo apt-get upgrade
$ sudo apt-get install python3-webstat

# Launch
Before running webstat, it is mandatory that the user exports a key to the environment - this is to ensure that the sniffed data is encrypted

Insert key here: 
$ sudo vim etc/environment

# Launch Sniff Mode
$ sudo webstat -m sniff

# Launch Analyze Mode 
$ sudo webstat -m analyze

# Sniff mode will enable all metrics on <http://localhost:8000/metrics>, which can further be added as a Prometheus target

```

## License ##

This project is under license from MIT. For more details, see the [LICENSE](LICENSE.md) file.


Made with :heart: by <a href="https://github.com/{{YOUR_GITHUB_USERNAME}}" target="_blank">{{Team R&D at Smile}}</a>

&#xa0;

<a href="#top">Back to top</a>

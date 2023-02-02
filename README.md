 <h1 align="center">Ene5ai Project</h1>
<br>

## About ##

This python module wrapped in a debian package enables users to inspect and export the http traffic. 

It provides 2 modes: Sniff and Analyze, users can choose which suits them best. The Analyze mode will provide an interactive terminal where the user can choose and export a report of http traffic while Sniff mode will inspect the traffic in real time and expose them to prometheus so the data can be analyzed in time series database.

## Features ##

**Sniff mode:**\
Inspects http data, aggregates them and exposes it on port 8000. The exposed metrics will be consumed by prometheus, it is a good idea to run this in background.

**Analyze mode:**\
Opens an interactive terminal with a real-time network activity report. User can choose which domain information to be exported.

## Technologies ##

The following tools were used in this project:

- [Python](https://www.python.org/)
- [stdeb](https://pypi.org/project/stdeb/)
- [Scapy](https://pypi.org/project/scapy/)
- [Prometheus](https://pypi.org/project/prometheus/)

## Installation ##

```bash
$ sudo add-apt-repository ppa:rnd-smile/webstat
$ sudo apt-get update && sudo apt-get upgrade
$ sudo apt-get install python3-webstat
```

## Launch ##
Before running webstat, it is mandatory that the user exports a key to the environment\
This is to ensure that the sniffed data is encrypted
```bash
# Insert key here: 
$ sudo vim etc/environment

# Launch Sniff Mode
$ sudo webstat -m sniff

# Launch Analyze Mode 
$ sudo webstat -m analyze

# Sniff mode will enable all metrics on <http://localhost:8000/metrics>, which can further be added as a Prometheus target

```

## License ##

This project is under license from MIT. For more details, see the [LICENSE](LICENSE.md) file.

## Credits

- Rnd Team @ Smile

&#xa0;

<a href="#top">Back to top</a>

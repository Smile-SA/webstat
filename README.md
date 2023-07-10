# Webstat

## About ##

This python module wrapped in a debian package enables users to inspect and export their http traffic. 

It provides 2 modes: Sniff and Analyze. The Analyze mode will provide an interactive terminal where the user can choose and export http traffic as metrics over Prometheus, while Sniff mode will inspect entire traffic in real time and expose it as metrics to prometheus. In the first case, users have full control over the data they want to share, in the second, extraction and metrics retrieval is automated.

## Features ##

**Sniff mode:**
Inspects http data, aggregates them and exposes it on port 8000. The exposed metrics will be consumed by prometheus, it is a good idea to run this in background.

**Analyze mode:**
Opens an interactive terminal with a real-time network activity report. User can choose which domain information to be exported as metrics for Prometheus over port 8001.

## Dependencies ##

This project mainly depends on [prometheus-client==0.15.0](https://pypi.org/project/prometheus/) 

```bash
$ pip3 install prometheus_client==0.15.0 
```

## Installation ##

```bash
$ sudo add-apt-repository ppa:rnd-smile/webstat
$ sudo apt-get update && sudo apt-get upgrade
$ sudo apt-get install python3-webstat
```

## Launch ##

```bash
# Launch Sniff Mode
$ sudo webstat -m sniff
# Sniff mode will enable all metrics on <http://localhost:8000/metrics>

# Launch Analyze Mode 
$ sudo webstat -m analyze
# Analyze mode will enable user selected metrics on <http://localhost:8001/metrics>
```

These metrics can be added to prometheus as targets.

## Remove Webstat ##

```bash
sudo apt-get purge --auto-remove python3-webstat
```
## License ##

This project is under license from MIT. For more details, see the [LICENSE](LICENSE.md) file.

## Credits

- Saifuddin Mohammad
- Hong Phuc VU
- Rnd Team @ Smile

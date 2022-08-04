from process import analyze_mode
from sniff import sniff_mode
from prometheus_client import start_http_server

mode = 1

if __name__ == '__main__':
    if mode == 0:
        analyze_mode()
    else:
        start_http_server(8000)
        sniff_mode()

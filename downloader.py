"""
Multithreaded File Downloader

The downloader accepts a URL and number of threads as input
and downloads the linked file in the local directory in
which the downloader script is run.

Inputs:
    1. url : the url to the linked file
    2. number_of_threads : the number of threads to concurrently
    download the file

Working:
The downloader makes a get request to find the content length and
then based on the number_of_threads, divides the file into discreet
parts. The start and end offsets are calculated (no overlap), and
each thread tackles one part.

Each thread sends a get request with the range of the bytes to be
received and writes them at the appropriate offset of the downloaded
file. Since the parts are non-overlapping, the request and the write
can be concurrent without the need of any locks and synchronization.

Troubleshooting:
1. Internet connection : The get requests have a timeout of 10 seconds,
so if any thread loses connection, it will timeout and a global counter
will track the number of timed out or incomplete threads.
If there is any incomplete thread, the downloaded file is deleted
and the download is deemed to be failed.

2. Thread number : If the user inputs a non-number or a negative number
as the number_of_threads, the program returns with an error.

3. Incorrect URL : If during the get request, the URL is invalid, the
program returns with an error.
"""

import threading
import sys
import os
import requests

threadLock = threading.Lock()
threads_failed = 0


def thread_handler(start, end, outfile, url):
    headers = {'Range': 'bytes=' + str(start) + '-' + str(end)}
    global threadLock
    global threads_failed
    try:
        r = requests.get(url, headers=headers, stream=True, timeout=10)
        content = r.content
    except Exception:
        with threadLock:
            threads_failed += 1
        return
    f = open(outfile, 'r+b')
    f.seek(start)
    f.write(content)
    f.close()


def download(url, number_threads):
    try:
        h = requests.head(url, timeout=10)
        header = h.headers
        content_length = int(header.get('content-length', None))
    except Exception:
        print("Connection to URL failed. Recheck internet connection or URL entered")
        return
    parts = int(content_length/number_threads)
    outfile = url.split('/')[-1]
    f = open(outfile, 'wb')
    f.write(b'\0'*content_length)
    f.close()

    threads = []
    print("Download starting")
    for i in range(number_threads):
        start = parts * i
        if i == (number_threads - 1):
            end = content_length
        else:
            end = start + parts - 1
        t = threading.Thread(target=thread_handler, args=(start, end, outfile, url), daemon=True)
        threads.append(t)
        t.start()

    for index, t in enumerate(threads):
        t.join()

    global threads_failed
    if threads_failed == 0:
        print("Download successful : " + str(outfile))
    else:
        os.remove(outfile)
        print("Download failed. Threads failed : " + str(threads_failed))


if __name__ == "__main__":
    url = sys.argv[1]
    try:
        number_threads = int(sys.argv[2])
        if number_threads <= 0:
            print("Incorrect number of threads : " + str(number_threads))
        else:
            download(url, number_threads)
    except ValueError:
        print("Incorrect number of threads : " + sys.argv[2])

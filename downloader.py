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

"""
Purpose:
Write from start byte to end byte in the outfile from the
file present at the address url. This is the main function
for each thread and the main thread ensures non overlapping
of the start and the end byte.

Parameters:
start - starting byte to request from the url
end - the last byte to request from the url
outfile - the file to write the bytes between start-end
url - the address of the file to be downloaded

Returns:
If successful, writes to the outfile and returns void
else is caught in an except clause, where global counter
threads_failed is incremented and thread returns 
unsuccessful in its execution
"""


def thread_handler(start, end, outfile, url):
    # the request header specifying the bytes required
    headers = {'Range': 'bytes=' + str(start) + '-' + str(end)}
    global threadLock
    global threads_failed
    try:
        r = requests.get(url, headers=headers, stream=True, timeout=60)
        content = r.content  # stores the requested bytes, can be timed out
    except Exception:
        with threadLock:
            threads_failed += 1
        return
    f = open(outfile, 'r+b')  # write to the outfile at start offset
    f.seek(start)
    f.write(content)
    f.close()

"""
Purpose:
Main thread that determines the size of the file to be downloaded.
Divides the file into equal parts (= number_of_threads) to be given
to each thread. 
The calculation is simple by finding the number of bytes that need 
to be in each part and then calculating the offset.
Call the threads in background mode and then wait for them to finish.

Parameters:
url - the address of the file to be downloaded
number_threads - user given number of threads for downloading the file

Returns:
If threads_failed = 0,  return download successful else delete the 
return download failed and delete the incomplete outfile prepared
by the threads.
"""


def download(url, number_threads):
    try:
        h = requests.head(url, timeout=10)
        header = h.headers
        content_length = int(header.get('content-length', None))  # size of the file
    except Exception:
        print("Connection to URL failed. Recheck internet connection or URL entered")
        return
    # size of the file part each thread has to download and write
    parts = int(content_length/number_threads)
    outfile = url.split('/')[-1]
    f = open(outfile, 'wb')
    f.write(b'\0'*content_length)  # temp file with null characters created
    f.close()

    threads = []  # store the threads to be spawned
    print("Download starting")
    for i in range(number_threads):
        # start and end store the offset and the end
        start = parts * i
        if i == (number_threads - 1):
            end = content_length
        else:
            end = start + parts - 1
        # initialize and start the thread in background
        t = threading.Thread(target=thread_handler, args=(start, end, outfile, url), daemon=True)
        threads.append(t)
        t.start()

    for index, t in enumerate(threads):
        t.join()  # terminate and collect the threads after completion

    global threads_failed
    if threads_failed == 0:  # SUCCESSFUL
        print("Download successful : " + str(outfile))
    else:  # FAILURE
        os.remove(outfile)
        print("Download failed. Threads failed : " + str(threads_failed))


if __name__ == "__main__":
    url = sys.argv[1]
    try:
        number_threads = int(sys.argv[2])
        if number_threads <= 0:  # non positive numbers of thread
            print("Incorrect number of threads : " + str(number_threads))
        else:
            download(url, number_threads)
    except ValueError:  # non number value for thread
        print("Incorrect number of threads : " + sys.argv[2])

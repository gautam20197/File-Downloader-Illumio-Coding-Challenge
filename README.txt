Multithreaded file downloader

Requirements
1. Python3
2. venv module in python3 (Virtual Environment Module)

Note: venv module should automatically be there along a
normal python3 installation

Installation Instructions:
1. Users with python3 native installed
Run ./install from the unzipped folder of the downloader.

It will create a venv (virtual environment) folder and
download all the required modules in the virtual environment,
therefore not disturbing any of the local python installations.

2. Users with conda installed
Currently the script does not support conda virtual environments,
so please install the packages from requirements.txt manually.
Remove line 18 and 20, from the downloader script, that are
responsible for activating the environment and deactivating it.

An alternate method could be for conda users to make their own
environment, but they it is upto them. The only changes would
be to update the name of the environment in downloader script.

Usage:

./downloader <URL> -c <numThreads>

It activates the virtual environment and then calls the python
script downloader.py that is responsible for downloading the file.
The file will be downloaded in the local directory where the script
is called.

Note: Please call the downloader script from where it resides in
the unzipped folder. Do not call it from any other location in your
file system.

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
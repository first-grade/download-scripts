'''Common variables and functions for downloader scripts

Contains common utilities and constants for all download scripts in this repo.
'''
import os
import shutil

BASE_REPO_PATH = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_PATH = os.path.join(BASE_REPO_PATH, 'downloads')

def clean_downloads(subfolder=None):
    '''
    Deletes all downloads.

    @param subfolder    If provided, delete only the downloads in subfolder.
    '''
    delete_path = DOWNLOAD_PATH
    if subfolder is not None:
        delete_path = os.path.join(delete_path, subfolder)

    if os.path.exists(delete_path):
        if os.path.isdir(delete_path):
            shutil.rmtree(delete_path)
        else:
            os.remove(delete_path)

def create_downloads(subfolder=None, clean=True):
    '''
    Creates the downloads path if it doesn't exists, or leads to a file instead of a folder.

    @param subfolder    Create a specific subfolder instead of working on the entire downloads
                        folder.
    @param clean        If set to `True`, also clean the directory's contents.
    '''
    if clean:
        clean_downloads(subfolder=subfolder)

    create_path = DOWNLOAD_PATH
    if subfolder is not None:
        create_path = os.path.join(create_path, subfolder)

    if os.path.exists(create_path):
        if not os.path.isdir(create_path):
            os.remove(create_path)
            os.mkdir(create_path)
    else:
        os.makedirs(create_path)

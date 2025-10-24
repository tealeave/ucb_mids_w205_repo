#!/usr/bin/python3

import sys
import os
import tarfile

def print_usage():
    "print the usage message for this utility"
    
    print("\nwalk_directory_tree.py\n")
    print("usage: walk_directory_tree directory option")
    print("option 1: print directories in alphabetical order")
    print("option 2: print directories and sizes sorted ascending")
    print("option 3: print directories and sizes sorted descending")
    print("option 4: print files in alphabetical order")
    print("option 5: print files and sizes sorted ascending")
    print("option 6: print files and sizes sorted descending\n")
    

def get_directory_size(directory):
    "given a directory, recursively walk the files in the directory, adding up the files sizes to get toal size"

    size = 0

    for root, dirs, files in os.walk(directory):

        for file in files:

            directory_file = os.path.join(root, file)

            size += os.path.getsize(directory_file)

    return(size)

def create_directory_file_list(directory):
    "given a directory, create a list of directories and their sizes, and a list of files and their sizes"
    
    directory_list = []

    file_list = []
    
    for root, dirs, files in os.walk(directory):

        for dir in dirs:
            root_directory = os.path.join(root, dir)
            directory_list.append([root_directory, get_directory_size(root_directory)])

        for file in files:
            directory_file = os.path.join(root, file)
            file_list.append([directory_file, os.path.getsize(directory_file)])
            
    return (directory_list, file_list)

def print_directories(directory_list, option):
    "given a directory list, sort either ascending or descending, and print"
    
    if option == 1:
        directory_list = sorted(directory_list, key = lambda x: x[0])
    elif option == 2:
        directory_list = sorted(directory_list, key = lambda x: x[1])
    else:
        directory_list = sorted(directory_list, key = lambda x: x[1], reverse=True)
        
    for directory in directory_list:

        directory_name = directory[0]
        directory_size = directory[1]

        if directory_size > 1024*1024*1024:
            directory_size_string = f'{directory_size / float(1024*1024*1024):.1f}G'

        elif directory_size > 1024*1024:
            directory_size_string = f'{directory_size / float(1024*1024):.1f}M'

        elif directory_size > 1024:
            directory_size_string = f'{directory_size / float(1024):.1f}K'

        else:
            directory_size_string = str(directory_size)

        print(directory_name, directory_size_string)

        
def print_files(file_list, option):
    "given a file list, sort either ascending or descending, and print"
    
    if option == 4:
        file_list = sorted(file_list, key = lambda x: x[0])
    elif option == 5:
        file_list = sorted(file_list, key = lambda x: x[1])
    else:
        file_list = sorted(file_list, key = lambda x: x[1], reverse=True)
        
    for file in file_list:

        file_name = file[0]
        file_size = file[1]

        if file_size > 1024*1024*1024:
            file_size_string = f'{file_size / float(1024*1024*1024):.1f}G'

        elif file_size > 1024*1024:
            file_size_string = f'{file_size / float(1024*1024):.1f}M'

        elif file_size > 1024:
            file_size_string = f'{file_size / float(1024):.1f}K'

        else:
            file_size_string = str(file_size)

        print(file_name, file_size_string)


if len(sys.argv) != 3:
    print_usage()
    exit(-1)
    
directory = sys.argv[1]

(directory_list, file_list) = create_directory_file_list(directory)
    
option = int(sys.argv[2])

if option in [1, 2, 3]:
    print_directories(directory_list, option)
elif option in [4, 5, 6]:
    print_files(file_list, option)
else:
    print_usage()

import os
import shutil
import time
from PIL import Image
import mimetypes
from console_progressbar import ProgressBar
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from hachoir.core import config as hachoirconfig
from datetime import datetime
from threading import Thread

def mod_date(filename):

    date_time = time.gmtime(os.path.getmtime(filename))     
    file_date = time.strftime('%Y-%m-%d', date_time)
    file_time = time.strftime('%H:%M:%S',date_time)

    file_folder = file_date[0:7]

    file_name = f'{file_date[8:10]} - ({file_time[0:2]}_{file_time[3:5]}_{file_time[6:8]})'

    return file_folder, file_name

def get_metadata(filename):
    hachoirconfig.quiet = True
    parser = createParser(filename)  
    
    if not parser:
        return None
        
    with parser:
        try:
            metadata = extractMetadata(parser)                    
        except:
            metadata = None

    return metadata

if __name__ == "__main__":
    pg = ProgressBar(len(os.listdir()))

    report = open("report.txt",'w')
    
    for i,filename in enumerate(os.listdir()):
        pg.print_progress_bar(i)
        
        filename = os.fsdecode(filename)
        
        file_ext = filename.split('.')[-1]

        if file_ext == 'AAE':
            os.remove(filename)
            report.write(f"Deleting -> {filename}\n")
            continue
        elif len(filename.split('.')) == 1:
            report.write(f"Skiping -> {filename}\n")
            continue

        mime = mimetypes.guess_type(filename)
        
        if mime[0] is None:
            report.write(f"Error -> {filename}\n")
            continue

        mime = mime[0].split('/')[0]

        if mime == 'image':
            try:
                img = Image.open(filename)._getexif()
                
                img_date = img[36867]

                if img_date == '':
                    raise RuntimeError

                img_folder = img_date[0:4] + "-" + img_date[5:7]
                img_name = img_date[8:10] + " - (" + img_date[11:13] + "_" + img_date[14:16] + "_" + img_date[17:19] + ")"
                
                try:
                    os.mkdir(img_folder)
                    shutil.move(filename, img_folder + "\\" + img_name + '.' + file_ext)
                except FileExistsError:
                    if not os.path.exists(img_folder + "\\" + img_name + '.' + file_ext):
                        shutil.move(filename, img_folder + "\\" + img_name + '.' + file_ext)
                    else:
                        mime = 'video'

                if mime != 'video':
                    continue
                
            except:
                mime = 'video'
        
        if mime == 'video':
            metadata = []
            thr = Thread(target= lambda metadata, file: metadata.append(get_metadata(file)),args=(metadata, filename))
            thr.start()
            thr.join(1)

            if not len(metadata):
                report.write(f'Error -> {filename}\n')
                continue
            
            vid_date = 0

            for line in metadata[0].exportPlaintext():
                if line.split(':')[0] == '- Creation date':
                    date_time = line.split()
                    vid_date = date_time[3]
                    vid_time = date_time[4]
                    break

            if not vid_date:
                vid_folder, vid_name = mod_date(filename)     
            else:
                vid_folder = vid_date[0:7]
                vid_name = f'{vid_date[8:10]} - ({vid_time[0:2]}_{vid_time[3:5]}_{vid_time[6:8]})'

            try:
                os.mkdir(vid_folder)
                shutil.move(filename, vid_folder + "\\" + vid_name + '.' + file_ext)
            except FileExistsError:      
                if not os.path.exists(vid_folder + "\\" + vid_name + '.' + file_ext):
                    shutil.move(filename, vid_folder + "\\" + vid_name + '.' + file_ext)
                else:
                    vid_folder, vid_name = mod_date(filename)  
                    if not os.path.exists(vid_folder + "\\" + vid_name + '.' + file_ext):
                        try:
                            os.mkdir(vid_folder)
                            shutil.move(filename, vid_folder + "\\" + vid_name + '.' + file_ext)
                        except FileExistsError:
                            shutil.move(filename, vid_folder + "\\" + vid_name + '.' + file_ext)
                    else:
                        report.write(f'Same Dates -> {filename} -> {vid_folder} {vid_name}\n')
            continue
        else:
            if filename != 'rename.py' and filename != 'report.txt':
                report.write(f"Skiping -> {filename}\n")

    report.close()
    print("\nDone")
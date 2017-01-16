# Python script to search for MPs with no embedded artwork

import os,re
import json
import urllib

from mutagen.mp3 import MP3
from mutagen import File
from mutagen.id3 import ID3, APIC, error
# audio = MP3("/Users/matt.singleton/Python/01 Sultans of Swing.mp3")
# mypath = "/Users/matt.singleton/Python"
mypath = "/Users/matt.singleton/Python/Alessandrini, Rinaldo"

def get_filepaths(directory):
    """
    This function will generate the file names in a directory
    tree by walking the tree either top-down or bottom-up. For each
    directory in the tree rooted at directory top (including top itself),
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.

# print audio.info.length, audio.info.bitrate


"""
artwork = audio.tags['APIC:'].data # access APIC frame and grab the image
with open('image.jpg', 'wb') as img:
   img.write(artwork) # write artwork to new image
"""


# Run the above function and store its results in a variable.
full_file_paths = get_filepaths(mypath)

for f in full_file_paths:
    if f.endswith(".mp3") and not os.path.basename(f)[0] == "." :
        print "Processing file :" + f
        audioid = ID3(f)
        audio = MP3(f)
        file = File(f)


        # Check to see if the file has artwork and bale
        # if it does
        artwork = ""
        for i in audio:
            if i.startswith("APIC"):
                print audio[i].desc
                artwork=audio[i].desc

        if not artwork:
            print "No APIC tag!"

            # 1st check to see if there's a Folder.jpg file in the file's directory
            # and if so use that as the image
            if  os.path.isfile(os.path.basename(f) + "/Folder.jpg"):
                audio.tags.add(
                    APIC(
                        encoding=3, # 3 is for utf-8
                        mime='image/jpeg', # image/jpeg or image/png
                        type=3, # 3 is for the cover image
                        desc=u'Cover',
                        data=open(os.path.basename(f) + "/Folder.jpg").read()
                    )
                )
                audio.save()
                continue

            # First get the Album title from the TALB tag
            try:
	            album_title = audio.tags['TALB'].text[0]
            except (KeyError,TypeError,ValueError):
                print "This MP3 has no Album Title - Skipping!"
                continue

            print "The Album title is " + album_title
            re.U | re.I
            album_title = re.sub(r' \[.*?\].*', '', album_title)
            album_title = re.sub(r' - Disc .*', '', album_title)
            print "The edited Album title is " + album_title

            url = "https://itunes.apple.com/search?"
            url_tuples = {'term':album_title,'entity':'album','country':'gb' }
            encodedurl = urllib.urlencode(url_tuples)
            encodedurl = url + encodedurl
            print encodedurl

            jsonurl = urllib.urlopen(encodedurl)

            parsed_json = json.loads(jsonurl.read())
            result_lines=parsed_json["resultCount"]
            print result_lines
            if result_lines > 0:
                print parsed_json["results"][0]["artistName"]
                print parsed_json["results"][0]["artworkUrl100"]
                artwork_url =  urllib.urlopen(parsed_json["results"][0]["artworkUrl100"])

                audio.tags.add(
                    APIC(
                        encoding=3, # 3 is for utf-8
                        mime='image/jpeg', # image/jpeg or image/png
                        type=3, # 3 is for the cover image
                        desc=u'Cover',
#                       data=open('100x100bb.jpg').read()
                        data=artwork_url.read()
                    )
                )
                audio.save()
            else:
                print "No results found for file " + f


# omegaRoom-google-classroom
This repository learns you how to download files from google classroom
 
# Step 0:


### First of all you need to make your app on Google developers and install your 
### Credentials.json *(you can call it as you like) file to connect your app with your classroom account

# Step 1: 
### install Google Client library 

```text
  pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

# Step 2:

### Create the main file I call it room.py
#### for more info visit [Google Classroom Api](https://developers.google.com/classroom)

```python

# import libraries we need
from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from apiclient import http
import os.path
import shutil
import io


# If modifying these scopes, delete the file token.json.
# set scopes from google api 
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
          "https://www.googleapis.com/auth/classroom.coursework.me",
          "https://www.googleapis.com/auth/classroom.announcements.readonly",
          "https://www.googleapis.com/auth/classroom.guardianlinks.students",
          "https://www.googleapis.com/auth/classroom.courseworkmaterials",
          "https://www.googleapis.com/auth/drive"]

# set base dir that we want to save files into it
BASE_DIR_FILES = "D:/thirdStage"


# create main class 
class OmegaRoom:
    creds = None

    def __init__(self):
        self.main()
    
    # this method get google api service
    def main(self):
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:

                self.creds.refresh(Request())
            else:

                flow = InstalledAppFlow.from_client_secrets_file('main.json', SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        
        # we need to use google classroom service to get the files and drive service to install it.
        self.room = build('classroom', 'v1', credentials=self.creds)
        self.drive = build('drive', 'v3', credentials=self.creds)

    # this method show the classes name in your account
    def getCourses(self, rangeCourses):
        
        # get the courses info
        result = self.room.courses().list(pageSize=rangeCourses).execute()
        courses = result.get("courses", [])
        
        if courses:
            return courses

        else:
            return False
    
    # this method return the classWork posts
    def getWorks(self, course_id, page_size: int = 10):
        
        # get classWorks and list it using course id that we get from the previous method
        works = self.room.courses().courseWorkMaterials()
        works = works.list(courseId=course_id, pageSize=page_size).execute()

        if works:
            works = works["courseWorkMaterial"]
            index = 0
            
            # get only classWork that have material
            for i in range(len(works)):
                if not ("materials" in works[index].keys()):
                    works.pop(index)

                else:
                    index += 1

            return works

        else:
            return False

    def downloadWorks(self, works: list, course_name: str, base_dir: str = BASE_DIR_FILES, file_type: str = "pdf"):

        # go to the base dir you want to save the files into it
        os.chdir(base_dir)

        # check if the class folder is exists
        # here we call the folder name like course name in the classroom
        if os.path.exists(course_name):
            os.chdir(course_name)

        else:
            os.mkdir(course_name)
            os.chdir(course_name)

        for work in works:
            # check if the lecture is already exists
            file_name = work["materials"][0]["driveFile"]["driveFile"]["title"]
            if (not os.path.exists(file_name)) and (file_name[-len(file_type):] == file_type):

                # get file
                request = self.drive.files().get_media(fileId=work["materials"][0]["driveFile"]["driveFile"]["id"])
                fh = io.BytesIO()

                # download file
                downloader = http.MediaIoBaseDownload(fh, request)
                done = False
                
                # show progress but it's not wrok for me idk why kkkkkk ????????????????
                while done is False:
                    status, done = downloader.next_chunk()
                    print("Download %d%%" % int(status.progress() * 100))

                # The file has been downloaded into RAM, now save it in a file
                fh.seek(0)
                with open(f'{file_name}', 'wb') as f:
                    shutil.copyfileobj(fh, f, length=131072)

                os.chdir("../")
            else:
                print(f"{file_name} is already exists")

    def getPostsMaterials(self, course_id: str, pageSize: int = None):

        # get posts from class and list them
        posts = self.room.courses().announcements()
        posts = posts.list(courseId=course_id, pageSize=pageSize).execute()["announcements"]
        index = 0

        # get the only posts that have materials include it like pdf or mp4 etc.
        for i in range(len(posts)):
            if not("materials" in posts[index].keys()):
                posts.pop(index)

            else:
                index += 1

        return posts
```

# Step 3:

### In the end we need to run our code or test it idk kkkk
### I test it in map.py, so you are ready to install any file from classroom

```python
# import our file we make it in previous step
from room import OmegaRoom

# create object from it ????
room = OmegaRoom()

# get courses and set parameter of the number of the courses you want to show.
courses = room.getCourses(11)

for i in range(len(courses)):
    print(courses)
    

# get classWork and get id from courses variable
# so here I get classWork of the course of index 8
works = room.getWorks(courses[8]["id"])

if works:
    room.downloadWorks(works, courses[8]["name"])

posts = room.getPostsMaterials(courses[4]["id"])

if posts:
    room.downloadWorks(posts, courses[4]["name"])

```

# The End

### I hope this repo will help you 
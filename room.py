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
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
          "https://www.googleapis.com/auth/classroom.coursework.me",
          "https://www.googleapis.com/auth/classroom.announcements.readonly",
          "https://www.googleapis.com/auth/classroom.guardianlinks.students",
          "https://www.googleapis.com/auth/classroom.courseworkmaterials",
          "https://www.googleapis.com/auth/drive"]

BASE_DIR_FILES = "D:/thirdStage"


class OmegaRoom:
    creds = None

    def __init__(self):
        self.main()

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

        self.room = build('classroom', 'v1', credentials=self.creds)
        self.drive = build('drive', 'v3', credentials=self.creds)

    # this method show the classes name in your account
    def getCourses(self, rangeCourses):

        result = self.room.courses().list(pageSize=rangeCourses).execute()
        courses = result.get("courses", [])

        if courses:
            return courses

        else:
            return False

    def getWorks(self, course_id):

        works = self.room.courses().courseWorkMaterials()
        works = works.list(courseId=course_id, pageSize=10).execute()

        if works:
            works = works["courseWorkMaterial"]
            index = 0

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



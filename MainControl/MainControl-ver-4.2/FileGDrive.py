# import the required libraries
from __future__ import print_function
import pickle
import os.path
import io
import shutil
import requests
from mimetypes import MimeTypes
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
  
class DriveAPI:
    global SCOPES
      
    # Define the scopes
    SCOPES = ['https://www.googleapis.com/auth/drive']
  
    def __init__(self):
        
        # Variable self.creds will
        # store the user access token.
        # If no valid token found
        # we will create one.
        self.creds = None
  
        # The file token.pickle stores the
        # user's access and refresh tokens. It is
        # created automatically when the authorization
        # flow completes for the first time.
  
        # Check if file token.pickle exists
        if os.path.exists('token.pickle'):
  
            # Read the token from the file and
            # store it in the variable self.creds
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
  
        # If no valid credentials are available,
        # request the user to log in.
        if not self.creds or not self.creds.valid:
  
            # If token is expired, it will be refreshed,
            # else, we will request a new one.
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(host='localhost',   port=8080)
  
            # Save the access token in token.pickle
            # file for future usage
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
  
        # Connect to the API service
        self.service = build('drive', 'v3', credentials=self.creds)
    def getAllFilesData(self):
        # request a list of first N files or
        # folders with name and id from the API.
        results = self.service.files().list(
            pageSize=100, fields="files(id, name, size)").execute()
        items = results.get('files', [])
  
        # print a list of files
        print("Here's a list of files: \n")
        print(*items, sep="\n", end="\n\n")
        '''
        ids=[]
        names=[]
        for file in items:
            ids.append(file['id'])
            names.append(file['name'])
        '''
        return items
    '''
    def getFileData(self,file_id):
        file = self.service.files().get(fileId=file_id).execute()
        print(file)
        fileId=file['title']
        fileSize=file['fileSize']
        fileType=file['mimeType']
        fileLink=file['selfLink']
        fileUrl=file['downloadUrl']
        fileEx=file['fileExtension']
        return fileId, fileSize, fileType, fileLink, fileUrl, fileEx
       ''' 

    def FileDownload(self, file_id, file_name):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
          
        # Initialise a downloader object to download the file
        downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
        done = False
  
        try:
            # Download the data in chunks
            while not done:
                status, done = downloader.next_chunk()
  
            fh.seek(0)
              
            # Write the received data to the file
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(fh, f)
  
            print("File Downloaded")
            # Return True if file Downloaded successfully
            return True
        except:
            
            # Return False if something went wrong
            print("Something went wrong.")
            return False
  
    def FileUpload(self, filepath):
        
        # Extract the file name out of the file path
        name = filepath.split('/')[-1]
          
        # Find the MimeType of the file
        mimetype = MimeTypes().guess_type(name)[0]
          
        # create file metadata
        file_metadata = {'name': name}
  
        try:
            media = MediaFileUpload(filepath, mimetype=mimetype)
              
            # Create a new file in the Drive storage
            file = self.service.files().create(
                body=file_metadata, media_body=media, fields='id').execute()
              
            return "File Uploaded To GDrive."
          
        except:
              
            # Raise UploadError if file is not uploaded.
            return "Can't Upload File To GDrive."
'''
obj = DriveAPI()

fileId, fileSize, fileType, fileLink, fileUrl, fileEx=obj.getFileData('1BJYpY6cF8RahpMIrbXOOKZhPW1sDZs5F')
#print(obj.FileDownload(file_id='1nV1XXkUQ1IN3JdAYUko05PdxZ44HtqyK',file_name='produc.jpg'))
print(fileId, fileSize, fileType, fileLink, fileUrl, fileEx)

print(list(obj.getAllFilesData()))
'''

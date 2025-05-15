class Config:
    SECRET_KEY = 'a-secure-random-string-123456'  # Replace with a secure key
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@localhost/boyle_lifesciences'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'  # Folder for image uploads
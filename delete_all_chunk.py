
import os



# Delete all files inside the folder
def deleteAll(folder_path):

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        os.remove(file_path)


# deleteAll("./uploads")

try:
    import os
    import sys
    from zipfile import ZipFile
    from os.path import basename
    from sys import platform
    import zipfile
    import glob
    import requests
except Exception as e:
    print("Error : {}".format(e))


_PIP = 'pip3'

class ShellExecutor(object):
    @staticmethod
    def execute(command='echo hello'):
        executor = os.popen(command).read()
        return executor
class Tree:
    @staticmethod
    def remove(target):
        for d in os.listdir(target):
            try:
                Tree.remove(target+'/'+d)
            except OSError:
                os.remove(target+'/'+d)
        os.rmdir(target)

def zipdir(path,archive):
    for root,dirs,files in os.walk(path):
        for file in files:
            archive.write(os.path.join(root,file),os.path.relpath(os.path.join(root,file),os.path.join(path,'..')))

def configureAWS():
    try:
        ACCESSID = input("ACSESS ID :")
        SECRET = input("SECRET : ")
        REGION = input("REGION: ") 
        # Linear command : aws configure set aws_access_key_id "AKIAI44QH8DHBEXAMPLE" --profile user2 && aws configure set --profile user2 && aws_secret_access_key "je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY" --profile user2 && aws configure set region "us-east-1" --profile user2 && aws configure set output "text" --profile user2
        _shell = 'aws configure set aws_access_key_id {} && aws configure set aws_secret_access_key {} && aws configure set region {}'.format(ACCESSID,SECRET,REGION)
        print(_shell)
        res = ShellExecutor.execute(command=_shell)
        print(res)
    except Exception as e:
        print("Error : {}".format(e))
        sys.exit(0)

def uploadArchiveToBucket(filename,bucketName):
    try:
        root = os.getcwd()
        _shell = "aws s3 cp {}/{} s3://{}".format(root,filename+".zip",bucketName)
        print(_shell)
        res = ShellExecutor.execute(command=_shell)
        print(res)
    except Exception as e:
        print("Error : {} ".format(e))

   

def moveZipToAWSLayer(zipfile,pythonVersion,bucketName):
    try:
        configureAWS()
        uploadArchiveToBucket(zipfile,bucketName)
        _shell = "aws lambda publish-layer-version  --layer-name {} --content S3Bucket={},S3Key={}  --description customlayer --compatible-runtimes python{}".format(zipfile,bucketName,zipfile+".zip",pythonVersion)
        print(_shell)
        res = ShellExecutor.execute(command=_shell)
        print(res)
    except Exception as e:
        print("Error : {}".format(e))
    

def installWheel(pythonVersion):
    if(len(glob.glob('wheel/*.whl')) == 0):
        print("No Wheel File found skipping wheel installation..")
    else:
        wheelFile = glob.glob('wheel/*.whl')[0]
        print("Found wheel : "+wheelFile)
        dir = "build/python/lib/python{}/site-packages".format(pythonVersion)
        _shell = "{} install wheel {} -t {}".format(_PIP,wheelFile,dir)
        print(_shell)
        res = ShellExecutor.execute(command=_shell)
        print(res)


def createOrDeleteDirectory():
    try:
        Tree.remove(target='build')
    except Exception as e:
        pass

def generateDirectory(pythonVersion):
    try:
        dir = "build/python/lib/python{}/site-packages".format(pythonVersion)
        os.makedirs(os.path.join(os.getcwd(),dir))
    
    except Exception as e:
        pass




def installPackage(packageName,pythonVersion):
    dir = "build/python/lib/python{}/site-packages".format(pythonVersion)
    checkInternetConnectivity()
    _shell = "{} install {} -t {}".format(_PIP,packageName,dir)
    print(_shell)
    res = ShellExecutor.execute(command=_shell)
    print(res)

def checkInternetConnectivity():
    res = requests.get("http://google.co.in")
    if('200' in str(res)):
        print("Ping Success")
    else:
        print("Please connet to and try again :)")
        sys.exit(0)
        

def createPackage(zipfileName,pythonVersion):
    try:
        os.chdir(os.path.join(os.getcwd(),"build"))
        archive = zipfile.ZipFile(zipfileName+'.zip','w',zipfile.ZIP_DEFLATED)
        zipdir(path='python/',archive=archive)
        archive.close()
        print("Deployment Package Created with Name {}".format(zipfileName))
        print("Creating Lambda Layer ...")
        print("Layer Name : {}".format(zipfileName))
    except Exception as e:
        print("Error : {}".format(e))




def main():
    print("AWS Layer Generator")
   
    pythonVersion = input("Enter Lambda function's python version: ")
    packageName = input("Enter the Layer Name: ")
    zipfileName = input("Zip file Name : ")



    ## if folder already exists  delete
    createOrDeleteDirectory()
    ## Create a Directory Structure.
    # Structure would be build/python/lib/python<version>/site-packages
    generateDirectory(pythonVersion)

    #install wheel first
    installWheel(pythonVersion)
    # check Platform and install dependencies
    installPackage(packageName, pythonVersion)

    # Pack all the files
    createPackage(zipfileName,pythonVersion)
    # Ship to aws 
    moveZipToAWSLayer(zipfileName ,pythonVersion,"python-layer-generator") 

if __name__ == "__main__":
    main()

    



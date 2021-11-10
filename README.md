# Meeting Scheduler

### Authors:
   Roman Nett  
   Katherine Rosas  
   Yash Khatiwala  
   Nik Pepmeyer  
   Tianze Zhu  

### Installation and Running

#### Installation

1. Make sure nodejs and npm are installed

2. Install python packages with  
      "pip install django"  
      "pip install django-cors-headers"  
      "pip install requests-toolbelt"  
      "pip install numpy"  
      "pip install pandas"  
      "pip install openpyxl"  

3. Clone git repo or pull most recent version

4. Open terminal to SD-D\scheduler\frontend

5. Run "npm install" to install node modules

#### Running

1. Open terminal to SD-D\scheduler\frontend

2. Run "npm run serve" to start frontend, all frontend pieces will work but backend calls will not return

3. Open a new terminal to SD-D\scheduler

4. Run "python manage.py runserver" to start backend, backend calls will now return

#### Details

Saving the frontend vue file while the frontend is running will cause a "hot reload", meaning the updates will automatically be ecorporated

Saving any backend files will also cause a backend "hot reload", again the updates will be encorporated

### Connecting

 - Connect to the Web App from a separate computer on the same network

#### Run the app so that it is discoverable

1. Make sure the network you are connected to is a "home" network, so your computer is discoverable

2. This can be verified by checking the "Network" url after running the frontend

3. Take the ip address being used as the frontend host from step 2.

4. Run the backend with "python manage.py runserver {ip address}:8000"

#### Connect from a separate computer

Other users on the network can now connect to the frontend by going to {ip address}:8080
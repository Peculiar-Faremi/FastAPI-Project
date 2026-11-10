FROM python:3.13.15
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
#sh is a shell command that allows you to run commands in a shell environment. In this case, it is used to run the uvicorn server with the specified parameters.
#The CMD instruction specifies the command to run when the container starts. It runs uvicorn with the app.main:app module, binds it to all network interfaces
#c tells the shell to read commands from the command string. The --host option specifies the host address to bind to, and the --port option specifies the port number to listen on. 
#The ${PORT:-8000} syntax allows you to specify a default port of 8000 if the PORT environment variable is not set.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
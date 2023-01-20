import subprocess

# targets for poetry run

def test():
    subprocess.run(['python', '-u', '-m', 'unittest', 'discover'])
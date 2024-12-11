import subprocess
import sys
import os

def create_virtual_environment(env_name='venv'):
    # Check if the virtual environment already exists
    if os.path.exists(env_name):
        print(f"Virtual environment '{env_name}' already exists.")
    else:
        # Create a virtual environment
        subprocess.check_call([sys.executable, '-m', 'venv', env_name])
        print(f"Virtual environment '{env_name}' created.")

def upgrade_pip(env_name='venv'):
    # Construct the path to the python executable within the virtual environment
    if os.name == 'nt':  # Windows
        python_executable = os.path.join(env_name, 'Scripts', 'python.exe')
    else:  # Unix or MacOS
        python_executable = os.path.join(env_name, 'bin', 'python')

    # Upgrade pip using the python -m pip approach
    subprocess.check_call([python_executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    print("Pip upgraded.")

def install_dependencies(env_name='venv', requirements_file='requirements.txt'):
    # Manually set environment variables to activate the virtual environment
    if os.name == 'nt':  # Windows
        python_executable = os.path.join(env_name, 'Scripts', 'python.exe')
        pip_executable = os.path.join(env_name, 'Scripts', 'pip.exe')
        os.environ['PATH'] = os.pathsep.join([os.path.join(env_name, 'Scripts'), os.environ['PATH']])
    else:  # Unix or MacOS
        python_executable = os.path.join(env_name, 'bin', 'python')
        pip_executable = os.path.join(env_name, 'bin', 'pip')
        os.environ['PATH'] = os.pathsep.join([os.path.join(env_name, 'bin'), os.environ['PATH']])

    # Read the requirements file and install each dependency individually
    with open(requirements_file, 'r') as file:
        for line in file:
            package = line.strip()
            if package and not package.startswith('#'):  # Ignore empty lines and comments
                try:
                    subprocess.check_call([pip_executable, 'install', package])
                    print(f"Installed {package}")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to install {package}: {e}")

    print(f"Dependencies installation attempted from '{requirements_file}'.")

if __name__ == '__main__':
    env_name = 'venv'  # You can change this to your desired environment name
    requirements_file = 'requirements.txt'  # Ensure this file exists in your project directory

    create_virtual_environment(env_name)
    upgrade_pip(env_name)
    install_dependencies(env_name, requirements_file)

import subprocess
import webbrowser

def execute_cli_command(container_name_or_id,  cli_command):
    # Build the command to execute inside the container
    command = f'docker exec -it {container_name_or_id} {cli_command}'

    # Execute the command using subprocess
    subprocess.run(command, shell=True)

subprocess.run("docker-compose up -d",shell=True)
subprocess.run("flexmeasures db upgrade",shell=True)
# Example usage
container_name_or_id = 'flexmeasures-tutorial-fm'
cli_command = ['flexmeasures db upgrade', "flexmeasures add account --name  gepee","flexmeasures add user --username gepee --email projects.gepee@gmail.com --account-id 1 --roles=admin"]
for cmd in cli_command:
    execute_cli_command(container_name_or_id, cmd)
    print(cmd)
webbrowser.open("http://localhost:5000")



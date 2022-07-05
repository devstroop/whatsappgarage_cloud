from whatsapp import docker_client

def init():
    docker_client.containers.get('')
    docker_client.containers.run("selenium/standalone-chrome", detach=True)
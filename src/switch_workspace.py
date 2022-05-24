from i3ipc import Connection
from subprocess import Popen, PIPE


def main():
    # Connect to Sway, get all workspace names
    sway = Connection()
    workspaces = sway.get_workspaces()
    workspace_names: [str] = [i.name for i in workspaces]

    # Open `wofi` with the list of workspaces
    proc = Popen(["/usr/bin/wofi", "-d", "--insensitive"],
                 stdout=PIPE,
                 stdin=PIPE,
                 stderr=PIPE,
                 universal_newlines=True)
    selected_workspace = proc.communicate("\n".join(workspace_names))[0]

    # Switch to workspace
    sway.command(f"workspace {selected_workspace}")


if __name__ == '__main__':
    main()

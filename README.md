# Trivial Editor demo release
An online code editor for the trivial language. Can currently be run locally by cloning this repository. 

## Instructions to Run Locally
1. Navigate to the `/backend` folder in the terminal and run the following command to start the backend
    ```console
    $ python server_run.py
    ```
2. Navigate to the `/frontend` folder in the terminal and run the following commands to start the front end run the cite locally
    ```console
    $ npm install -g http-server
    $ http-server
    ```
3. Open any of the local urls output by the ```http-server``` command in a browser window
4. Write trivial code in the editor and view the output in the console displayed!

## Resources Used
*Ace Code Editor*, an opensource code-editor component for web projects. Provides a formatted editor with syntax highlighting abilities, implemented in javascript. <br>[link: https://ace.c9.io/]

*Building a Code Editor For The Web* by "Coder Archive", A youtube video series on building a simple online code editor using the *Ace Code Editor* component. Followed pretty closely for the front-end of *trivial-editor*. <br> [link: https://www.youtube.com/watch?v=loNrxXOd2C0&list=PLa1xgJ2RrCxa3sld2GIiuKcmQbCqxc9rP]

*http-server* A Node.js package used to run the front end of the site. Creates a static http-server, useful for local development. <br>[link: https://www.npmjs.com/package/http-server]

*Flask* A Python framework used for the back-end of this project. This is how the trivial language processing was configured and connected to the front-end. <br>[link: https://flask.palletsprojects.com/en/stable/]
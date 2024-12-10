// retrieve elements
const consoleLogList = document.querySelector(".editor__console-logs");
const executeCodeBtn = document.querySelector(".editor__run");
const resetCodeBtn = document.querySelector(".editor__reset");

//setup ace
var editor = ace.edit("editorCode");
var defaultCode = 'console.log("Hello World!")'; 
var consoleMessages = [];

var editorLib = {
    clearConsoleScreen() {
        consoleMessages.length = 0;

        // Remove all elements in the log list
        while (consoleLogList.firstChild) {
            consoleLogList.removeChild(consoleLogList.firstChild);
        }
    },
    printToConsole() {
        consoleMessages.forEach(log => {
            const newLogItem = document.createElement('li');
            const newLogText = document.createElement('pre');

            newLogText.className = log.class;
            newLogText.textContent = `> ${log.message}`;

            newLogItem.appendChild(newLogText);

            consoleLogList.appendChild(newLogItem);
        })
    },
    init(){
        //configure ace 

        //set theme
        editor.setTheme("ace/theme/dracula");

        //set language 
        editor.session.setMode("ace/mode/javascript");

        //set options
        editor.setOptions({
            enableBasicAutocompletion: true,
            enableLiveAutocompletion: true, 
        })

        //set defalutCode
        editor.setValue(defaultCode); 
    }
}

//Events
executeCodeBtn.addEventListener('click', () => {
    //clear the console
    editorLib.clearConsoleScreen(); 
    //get input from code editor
    const userCode = editor.getValue();

    //run the user code
    try {
        new Function(userCode)();
    } catch (err) {
        console.error(err); 
    }

    //print to the console
    editorLib.printToConsole();
})

resetCodeBtn.addEventListener('click', () => {
    //clear editor
    editor.setValue(defaultCode);

    //clear the console
    editorLib.clearConsoleScreen(); 
})

editorLib.init();
import {run} from './parser.js';
// retrieve elements
const consoleLogList = document.querySelector(".editor__console-logs");
const executeCodeBtn = document.querySelector(".editor__run");
const resetCodeBtn = document.querySelector(".editor__reset");

//setup ace
var editor = ace.edit("editorCode");
var defaultCode = 'print("hello trivial")'; 
//var consoleMessages = [];

//new stuff for trivial
var textToPrint = []; 

var editorLib = {
    clearConsoleScreen() {
        textToPrint.length = 0;

        // Remove all elements in the log list
        while (consoleLogList.firstChild) {
            consoleLogList.removeChild(consoleLogList.firstChild);
        }
    },
    /* printToConsole() {
        consoleMessages.forEach(log => {
            const newLogItem = document.createElement('li');
            const newLogText = document.createElement('pre');

            newLogText.className = log.class;
            newLogText.textContent = `> ${log.message}`;

            newLogItem.appendChild(newLogText);

            consoleLogList.appendChild(newLogItem);
        })
    }, */
    printTrivialConsole(){{
        //this accesses a global array that is populated by the user input, creates an html element for each element in that array and adds that 
        //element to the html list defined in the index.html file line 24, this is where that element is then displayed as text 
        
        //display text in console box
        textToPrint.forEach(element => {
            const newLogItem = document.createElement('li');
            const newLogText = document.createElement('pre');
            newLogText.textContent = `> ${element}`;
            newLogItem.appendChild(newLogText);
            consoleLogList.appendChild(newLogItem);
        });
    }},
    init(){
        //configure ace 

        //set theme
        editor.setTheme("ace/theme/dracula");

        //set language 
        editor.session.setMode("ace/mode/python"); // changes mode, can be js or py

        //set options
        editor.setOptions({
            // will look into, none make sense for trivial
            // enableBasicAutocompletion: true,
            // enableLiveAutocompletion: true, 
        })

        //set defalutCode
        editor.setValue(defaultCode); 
    }
}

//Events
executeCodeBtn.addEventListener('click', async () => {
    //clear the console
    editorLib.clearConsoleScreen(); 
    //get input from code editor
    const userCode = editor.getValue();

    //run the user code
    try {
        console.log(userCode); //this just outputs what user code is in the debug console
        //NEED: function that takes the userCode and runs it as trivial code, likely need to add the trivial source code files to the project then
        //take the user input from text>>tokens>>parsedtokens(Ast)>>evaluatedAst(output)
        //this function needs to return at LEAST the output of the code, should also find way to output errors but not necessary
        //this output should be an array of strings, 1 for each line of output 
        const result = await run(userCode);
        console.log(result);

        //example of code that takes string of input, splits on each new line, and pushes each line to an array
        const lines = result.split("\n"); //split userCode string by new line character
        lines.forEach(line => {
            textToPrint.push(line); //this is a global array that is accessed by the print to trivial console function
        });
    } catch (err) {
        textToPrint.push(err)
        console.error(err); 
    }

    //print to the console
    //editorLib.printToConsole();
    editorLib.printTrivialConsole(); 
    //NEED: function that takes output of the run function(as an array of strings, 1 for each line in the output) and displays it in the console box 
    //as formatted output, fine for to fudge it by simply printing plain text output instead of storing any sort of type information like a real console


})

resetCodeBtn.addEventListener('click', () => {
    //clear editor
    editor.setValue(defaultCode);

    //clear the console
    editorLib.clearConsoleScreen(); 
})

editorLib.init();
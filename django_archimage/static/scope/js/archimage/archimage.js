function SendCommand(command,arguments) {
    $.ajax({
         type:"POST",
         url:"/api/execute/",
         data: {
                'command': command,
                'args': arguments,
                'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value
                },
    });
};

// Paddle hookups:
$(document).ready(function () {
$("[id*='paddle']").mousedown(function(){
    SendCommand($(this).data("downcommand"),null); // Send the command to start moving
    });
$("[id*='paddle']").mouseup(function(){
    SendCommand($(this).data("upcommand"),null); // Send the command to start moving
    });
$("[id*='stop']").mousedown(function(){
    SendCommand($(this).data("downcommand"),null); // Send the command to start moving
    });       
});

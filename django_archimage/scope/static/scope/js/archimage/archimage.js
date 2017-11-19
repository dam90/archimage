// Use this to hit the api:
// "command" is required, arguments is optional
function SendCommand(command,arguments) {
    $.ajax({
         type:"POST",
         url:"/api/execute/",
         data: {
                'command': command,
                'args': arguments,
                'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value
                }
    });
};


// Mount Monitor Poll
(function poll() {
  setTimeout( function() {
    if ($('#toggle-monitor').prop('checked')){
    $.ajax({
         type:"POST",
         url:"/api/execute/",
         data: {
                'command': 'get_all',
                'args': null,
                'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value
                },
          dataType: 'json',
          success: function (result) {
              // update the display
              $('#pointing_readout').text(JSON.stringify(result.response, null, 4));
              // poll again
              poll();
            }
          });
    } else {
      // poll again
      $('#pointing_readout').text('Monitoring Disabled');
      poll();
    }
  }, 1000);
})();


// Paddle controls: 
// - commands delivered via data-downcommand and data-upcommand (press and release), 
// - id='paddle_something' to match contains jsquery for 'paddle'
$(function(){
    $("[id*='paddle']").bind('touchstart mousedown', function() {
        SendCommand($(this).data("downcommand"),null); // Send the command to start moving
    });
    $("[id*='paddle']").bind('touchend mouseup', function() {
        SendCommand($(this).data("upcommand"),null); // Send the command to start moving
    });
    $("[id*='stop']").bind('touchstart mousedown', function() {
        SendCommand($(this).data("downcommand"),null); // Send the command to start moving
    });
});

// Serial connection toggle
$(function(){
    $('#toggle-connection').change(function() { // TOGGLE: Connection
        if ($(this).prop('checked')) { // connect
              SendCommand('connect',null);
            } else { // disconnect
              SendCommand('disconnect',null);
            }
        });
})

// Helper functions: 
$(function(){
    $("#align_level_south").mousedown(function(){
        SendCommand('init_align',null); // Send the command to start moving
        });
    $("#clear_tracking_rates").mousedown(function(){
        SendCommand('clear_track_rates',null); // Send the command to start moving
        });
});

// Home: 
$(function(){
    $("#home_setup").mousedown(function(){
        SendCommand('home_setup',null); // Send the command to start moving
        });
    $("#home_find").mousedown(function(){
        SendCommand('find_home',null); // Send the command to start moving
        });
});

// Park: 
$(function(){
    $("#park_set").mousedown(function(){
        SendCommand('set_park',null); // Send the command to start moving
        });
    $("#park").mousedown(function(){
        SendCommand('home_park',null); // Send the command to start moving
        });
});

// Archiamge flag toggles
$(function() {

  $('#toggle-tracking').change(function() { // TOGGLE: Track
    if ($(this).prop('checked')) { // activate track
      SendCommand('enable_track',null);
    } else { // disable track
      SendCommand('disable_track',null);
    }
  });

  $('#toggle-configuration').change(function() { // TOGGLE: Mount Configuration
    if ($(this).prop('checked')) { // it's equatorial
      SendCommand('set_equatorial',null);
      $('#toggle-german').bootstrapToggle('enable'); // Enable german equatorial toggle if alt/az
    } else { // else it's alt/az
      $('#toggle-german').prop('checked',false).change(); // Turn off german equatorial if alt/az
      $('#toggle-german').bootstrapToggle('disable'); // Disable german equatorial toggle if alt/az
      SendCommand('set_altaz',null);
      SendCommand('disable_german_equatorial',null)
    }
  });

  $('#toggle-ieca').change(function() { // TOGGLE: IECA
    if ($(this).prop('checked')) { // activate IECA
      SendCommand('enable_ieca',null);
    } else { // disable IECA
      SendCommand('disable_ieca',null);
    }
  });

  $('#toggle-pec').change(function() { // TOGGLE: PEC
    if ($(this).prop('checked')) { // activate PEC
      SendCommand('enable_pec',null);
    } else { // disable PEC
      SendCommand('disable_pec',null);
    }
  });

  $('#toggle-horrizon').change(function() { // TOGGLE: Horrizon Limit
    if ($(this).prop('checked')) { // activate Horrizon Limit
      SendCommand('enable_horrizon_limit',null);
    } else { // disable Horrizon Limit
      SendCommand('disable_horrizon_limit',null);
    }
  });

  $('#toggle-german').change(function() { // TOGGLE: German Equatorial
    if ($(this).prop('checked')) { // activate german equatorial
      SendCommand('enable_german_equatorial',null);
    } else { // deactivate german equatorial
      SendCommand('disable_german_equatorial',null);
    }
  });

})
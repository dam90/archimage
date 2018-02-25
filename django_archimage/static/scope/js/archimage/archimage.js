
// Use this to hit the api:
// "command" is required, arguments is optional
// args is a "stringify-ed" json object
function SendCommand(command,arguments) {
  var jqXHR = $.ajax({
   type:"POST",
   url:"/api/execute/",
   data: {
    'command': command,
    'args': arguments,
    'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value
  },
  dataType: 'json'
});
};

// mouse clicked?
var is_clicked = false
$(document).mousedown(function(e) {
  is_clicked = true
});
$(document).mouseup(function(e) {
  is_clicked = false
});

// -----------------------------------------------------------------------------------------------------
//                                     Misc Mount Controls
// -----------------------------------------------------------------------------------------------------
// show-hide shortcuts
$(function(){
  $('#toggle-shortcuts').change(function() { // TOGGLE: Connection
    if ($(this).prop('checked')) { // show
      $('#collapseExample').collapse('show')
    } else { // hide
      $('#collapseExample').collapse('hide')
    }
  });
})
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

// -----------------------------------------------------------------------------------------------------
//                                     Polling Example
// -----------------------------------------------------------------------------------------------------
// Mount Monitor Poll
(function poll() {
  setTimeout( function() {
    if ($('#toggle-monitor').prop('checked')){
      $('#monitor-display').show();
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
              $('#pointing_readout').text(JSON.stringify(result.response.pointing, null, 4));
              $('#tracking_readout').text(JSON.stringify(result.response.tracking, null, 4));
              $('#target_readout').text(JSON.stringify(result.response.target, null, 4));
              $('#status_readout').text(JSON.stringify(result.response.status, null, 4));
              // poll again
              poll();
            }
          });
    } else {
      // poll again
      //$('#pointing_readout').text('Monitoring Disabled');
      $('#monitor-display').hide();
      poll();
    }
  }, 1000);
})();

// -----------------------------------------------------------------------------------------------------
//                                      Paddle Controls
// -----------------------------------------------------------------------------------------------------
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
// jog speed slider
$(function(){
  var paddleslider = $('#paddle-speed-slider').bootstrapSlider({
    tooltip: 'always',
    tooltip_position: 'bottom',
    precision: 2,
    data: 'slider',
    formatter: function(value) {
      //$('#paddle-speed-header').text('Speed: ' + value);
      return value;
    }
  });
  $("#paddle-speed-slider").bind('touchend mouseup', function() {
        //slide = $("#paddle-speed-slider").bootstrapSlider();
        speed = paddleslider.bootstrapSlider('getValue');
        SendCommand('set_speed',JSON.stringify({slew_speed_ds:speed}));
        $('#paddle-speed-header').text('Speed: ' + speed + ' deg/s');
      });
});

// -----------------------------------------------------------------------------------------------------
//                              Location Input Shtuff
// -----------------------------------------------------------------------------------------------------
// Location Stuff
$(function(){

  $("#location-btn").bind('touchstart mousedown', function() {
      // Set latitude
      var lat = parseFloat($("#latitude-input").val())
      var lon = parseFloat($("#longitude-input").val())
      console.log('Setting latitude to ' + lat)
      console.log('Setting longitude to ' + lon)
      SendCommand('set_location',JSON.stringify({lat_dd:lat,lon_dd:lon}))

    });
});

// -----------------------------------------------------------------------------------------------------
//                              GOTO Target Specification Shtuff
// -----------------------------------------------------------------------------------------------------
$(function(){
  change_goto_coordinates()
  check_goto_coordinates()
  $("#goto-target-btn").bind('touchstart mousedown',submit_goto_target);
  $('#toggle-goto-angle-format').change(update_goto);
  $('#goto-coordinate-id').change(update_goto);
});

function submit_goto_target(){
  if($('#goto-coordinate-id').val()=="ra-dec"){ //celestial pointing
    if ($("#toggle-goto-angle-format").prop('checked')) { // degrees
      var ra_dd = parseFloat($("#goto-ra-degrees").val());
      var dec_dd = parseFloat($("#goto-dec-degrees").val());
    } else { // sexasigmal
      var ra_h = parseFloat($("#goto-ra-hours").val());
      var ra_m = parseFloat($("#goto-ra-minutes").val());
      var ra_s = parseFloat($("#goto-ra-seconds").val());
      var ra_dd = ra_h*15 + ra_m/4 + ra_s/240;
      var dec_d = parseFloat($("#goto-dec-degrees").val());
      var dec_m = parseFloat($("#goto-dec-minutes").val());
      var dec_s = parseFloat($("#goto-dec-seconds").val());
      var dec_dd = dec_d + dec_m/60 + dec_s/3600
    }
    SendCommand('point_radec',JSON.stringify({ra_deg:ra_dd,dec_deg:dec_dd}))
  } else { //topocentric pointing
    if ($("#toggle-goto-angle-format").prop('checked')) { // degrees
      var alt_dd = parseFloat($("#goto-alt-degrees").val());
      var az_dd = parseFloat($("#goto-az-degrees").val());
    } else { // sexasigmal
      var alt_d = parseFloat($("#goto-alt-degrees").val());
      var alt_m = parseFloat($("#goto-alt-minutes").val());
      var alt_s = parseFloat($("#goto-alt-seconds").val());
      var alt_dd = alt_d + alt_m/60 + alt_s/3600
      var az_d = parseFloat($("#goto-az-degrees").val());
      var az_m = parseFloat($("#goto-az-minutes").val());
      var az_s = parseFloat($("#goto-az-seconds").val());
      var az_dd = az_d + az_m/60 + az_s/3600
    }
    SendCommand('point_altaz',JSON.stringify({alt_deg:alt_dd,az_deg:az_dd}))
  }
  return
}

// wrapper for all the display updating
function update_goto(){
  change_goto_coordinates()
  check_goto_coordinates()
  return
}
// display inputs for the selected coordniate SYSTEM
function change_goto_coordinates(){
  if($('#goto-coordinate-id').val()=="ra-dec"){
    $('#goto-topo').hide()
    $('#goto-celestial').show()
  } else {
    $('#goto-celestial').hide()
    $('#goto-topo').show()
  }
}
// display inputs for the selected coordniate FORMAT
function check_goto_coordinates(){
  if($('#goto-coordinate-id').val()=="ra-dec"){ //celestial pointing
    if ($("#toggle-goto-angle-format").prop('checked')) { // degrees
      // hour angle
      $("#goto-ra-degrees-form").show();
      $("#goto-ra-minutes-form").hide();
      $("#goto-ra-seconds-form").hide();
      $("#goto-ra-hours-form").hide();
      // declination
      $("#goto-dec-degrees-form").show();
      $("#goto-dec-minutes-form").hide();
      $("#goto-dec-seconds-form").hide();
    } else { // sexasigmal
      // hour angle
      $("#goto-ra-degrees-form").hide();
      $("#goto-ra-hours-form").show();
      $("#goto-ra-minutes-form").show();
      $("#goto-ra-seconds-form").show();
      // declination
      $("#goto-dec-degrees-form").show();
      $("#goto-dec-minutes-form").show();
      $("#goto-dec-seconds-form").show();
    }
  } else { //topocentric pointing
    if ($("#toggle-goto-angle-format").prop('checked')) { // degrees
      // azimiuth
      $("#goto-az-degrees-form").show();
      $("#goto-az-minutes-form").hide();
      $("#goto-az-seconds-form").hide();
      // altitude
      $("#goto-alt-degrees-form").show();
      $("#goto-alt-minutes-form").hide();
      $("#goto-alt-seconds-form").hide();
    } else { // sexasigmal
      // azimiuth
      $("#goto-az-degrees-form").show();
      $("#goto-az-minutes-form").show();
      $("#goto-az-seconds-form").show();
      // altitude
      $("#goto-alt-degrees-form").show();
      $("#goto-alt-minutes-form").show();
      $("#goto-alt-seconds-form").show();
    }
  }
  return
}

// -----------------------------------------------------------------------------------------------------
//                              Coordinate Specification Shtuff
// -----------------------------------------------------------------------------------------------------
$(function(){
  $("#pointing-btn").bind('touchstart mousedown',submit_pointing);
  $('#toggle-angle-format').change(check_coordinates);
  $('#coordinate-id').change(check_coordinates);
});

function submit_pointing(){
  var degrees = 0.0
  var hours = 0.0
  var minutes = 0.0
  var seconds = 0.0
  var coord = $('#coordinate-id').val();

  if ($("#toggle-angle-format").prop('checked')) { // degrees
    degrees = parseFloat($("#degrees").val())
  } else { // sexasigmal
    minutes = parseFloat($("#minutes").val())
    seconds = parseFloat($("#seconds").val())
    if($('#coordinate-id option:selected').text()=='Hour Angle'){ // hours
      hours = parseFloat($("#hours").val())
      degrees = hours*15 + minutes/4 + seconds/240
    } else { //degrees
      d = parseFloat($("#degrees").val())
      degrees  = d + minutes/60 + seconds/3600
    }
  }
  key = coord + '_dd'
  SendCommand('set_pointing_'+coord,JSON.stringify({[key]:degrees}))
  return
}

function check_coordinates(){
  if ($("#toggle-angle-format").prop('checked')) { // degrees
    $("#minutes-form").hide();
    $("#seconds-form").hide();
    $("#hours-form").hide();
    $("#degrees-form").show();
  } else { // sexasigmal
    if($('#coordinate-id').val()=='ha'){
      $("#degrees-form").hide();
      $("#hours-form").show();
    } else {
      $("#hours-form").hide();
      $("#degrees-form").show();
    }
    $("#minutes-form").show();
    $("#seconds-form").show();
  }
  return
}

// -----------------------------------------------------------------------------------------------------
//                                     Simulator Controls
// -----------------------------------------------------------------------------------------------------
$(function(){
  var sim_ra_position_slider = $('#simulator-ra-position-slider').bootstrapSlider({
    tooltip: 'always',
    tooltip_position: 'bottom',
    precision: 2,
    data: 'slider',
    formatter: function(value) {
      //$('#paddle-speed-header').text('Speed: ' + value);
      return value;
    }
  });
  $("#simulator-ra-position-slider").bind('touchmove mousemove touchend mouseup', function() {
    if (is_clicked) {
      ra = sim_ra_position_slider.bootstrapSlider('getValue')
      SendCommand('set_virtual_ra',JSON.stringify({ra_dd:ra}));
    }
  });
  var sim_dec_position_slider = $('#simulator-dec-position-slider').bootstrapSlider({
    tooltip: 'always',
    tooltip_position: 'bottom',
    precision: 2,
    data: 'slider',
    formatter: function(value) {
      return value;
    }
  });
  $("#simulator-dec-position-slider").bind('touchmove mousemove touchend mouseup', function() {
    if (is_clicked) {
      dec = sim_dec_position_slider.bootstrapSlider('getValue');
      SendCommand('set_virtual_dec',JSON.stringify({dec_dd:dec}));
    }

  });
});


// -----------------------------------------------------------------------------------------------------
//                                     Moount Flag Controls
// -----------------------------------------------------------------------------------------------------
// Archiamge flag toggles
$(function() {

  $('[id^=toggle-tracking]').change(function() { // TOGGLE: Track
    if ($(this).prop('checked')) { // activate track
      $(this).bootstrapToggle('On');
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

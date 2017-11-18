$(function() {

  $('#toggle-tracking').change(function() { // TOGGLE: Track
    if ($(this).prop('checked')) { // activate track
      SendCommand('enable_track',null)
    } else { // disable track
      SendCommand('disable_track',null)
    }
  })

  $('#toggle-configuration').change(function() { // TOGGLE: Mount Configuration
    if ($(this).prop('checked')) { // it's equatorial
      SendCommand('set_equatorial',null)
      $('#toggle-german').bootstrapToggle('enable'); // Enable german equatorial toggle if alt/az
    } else { // else it's alt/az
      $('#toggle-german').prop('checked',false).change(); // Turn off german equatorial if alt/az
      $('#toggle-german').bootstrapToggle('disable'); // Disable german equatorial toggle if alt/az
      SendCommand('set_altaz',null)
      SendCommand('disable_german_equatorial',null)
    }
  })

  $('#toggle-ieca').change(function() { // TOGGLE: IECA
    if ($(this).prop('checked')) { // activate IECA
      SendCommand('enable_ieca',null)
    } else { // disable IECA
      SendCommand('disable_ieca',null)
    }
  })

  $('#toggle-pec').change(function() { // TOGGLE: PEC
    if ($(this).prop('checked')) { // activate PEC
      SendCommand('enable_pec',null)
    } else { // disable PEC
      SendCommand('disable_pec',null)
    }
  })

  $('#toggle-horrizon').change(function() { // TOGGLE: Horrizon Limit
    if ($(this).prop('checked')) { // activate Horrizon Limit
      SendCommand('enable_horrizon_limit',null)
    } else { // disable Horrizon Limit
      SendCommand('disable_horrizon_limit',null)
    }
  })

  $('#toggle-german').change(function() { // TOGGLE: German Equatorial
    if ($(this).prop('checked')) { // activate german equatorial
      SendCommand('enable_german_equatorial',null)
    } else { // deactivate german equatorial
      SendCommand('disable_german_equatorial',null)
    }
  })
})
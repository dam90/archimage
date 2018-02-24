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
      poll();
    }
  }, 1000);
})();

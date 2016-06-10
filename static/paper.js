$(document).on('change', '.btn-file :file', function() {
  var input = $(this),
      numFiles = input.get(0).files ? input.get(0).files.length : 1,
      label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
  input.trigger('fileselect', [numFiles, label]);
});

$(document).ready( function() {
    $('.btn-file :file').on('fileselect', function(event, numFiles, label) {
        
        var input = $(this).parents('.input-group').find(':text'),
            log = numFiles > 1 ? numFiles + ' files selected' : label;
        
        if( input.length ) {
            input.val(log);
        } else {
            if( log ) alert(log);
        }
        
    });

    function runEffect() {
        // get effect type from
        var selectedEffect = "blind";

        // most effect types need no options passed by default
        var options = {};

        // run the effect
        $( "#effect" ).toggle( selectedEffect, options, 500 );
    };
    var open = false;
    // set effect from select menu value
    $( "#button" ).click(function() {
        runEffect();
        if(!open){
            $(this).text("取消");
            open = true;
        }
        else{
            $(this).text("上傳");
            open = false;
        }
    });
});

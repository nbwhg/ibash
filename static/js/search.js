$('#searchform').submit(function () {
    if($('#searchform input:last').val().length <= 0) {
        return false;
    }
})

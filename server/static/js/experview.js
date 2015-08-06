setupCheckBoxes = function() {
//    alert('mi');
    $("#ratlist_hdn").val('mimo');
    var nrats = parseInt($("#nrats_hdn").val());
    var rats = new Array();
    for (i=1; i<=nrats; i++) {
        if ($("#selectedrats_"+i).prop("checked")) {
            rats.push(i);
        }        
    }
    $('#ratlist_hdn').val(rats.join(','));
};

oriCheckBoxes = function() {
//    alert('xu');
    var nrats = parseInt($("#nrats_hdn").val());
    for (i=1; i<=nrats; i++) {
        $("#selectedrats_"+i).change(setupCheckBoxes);        
    }
};

$(document).ready(function() {
    setupCheckBoxes();
    oriCheckBoxes();
});
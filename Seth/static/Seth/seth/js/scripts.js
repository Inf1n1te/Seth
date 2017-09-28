$(".btn").mouseup(function(){
    $(this).blur();
})

$(document).ready(function() {
    $('#parent').on('change',function(){
      $('.child').prop('checked',$(this).prop('checked'));
    });
    $('.child').on('change',function(){
      $('#parent').prop('checked',$('.child:checked').length == $('.child').length);
    });
});

jQuery(document).ready(function($) {
    $(".clickable-row").click(function() {
        window.location = $(this).data("href");
    });
});

jQuery(document).ready(function($) {
    $('[data-toggle="tooltip"]').tooltip();

    var changeSlider = function(data) {
      $('[id^="gradeid_"]').each(function(index) {
        var grade = $(this).attr("data-grade")
        if(+grade > +data.to) {
          $(this).removeClass("success warning error")
          $(this).addClass("success")
        }
        else if(+grade >= +data.from) {
          $(this).removeClass("success warning error")
          $(this).addClass("warning")
        }
        else if(+grade < +data.from) {
          $(this).removeClass("success warning error")
          $(this).addClass("error")
        }
      });
    };

    $("#colorslider").ionRangeSlider({
                                    min: 1,
                                    max: 10,
                                    from: 5,
                                    to: 5.5,
                                    step: 0.1,
                                    type: 'double',
                                    grid: true,
                                    grid_num: 9,
                                    onChange: changeSlider
                                });

    $('[id^="gradeid_"]').each(function(index) {
        if($(this).attr("data-grade") > 5.5) {
            $(this).addClass("success")
        }
        else if($(this).attr("data-grade") >= 5) {
            $(this).addClass("warning")
        }
        else if($(this).attr("data-grade") < 5) {
            $(this).addClass("error")
        }
    });
});
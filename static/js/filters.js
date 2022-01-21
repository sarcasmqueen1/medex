$(function () {


function cd(start, end) {
        $('#Date span').html(start.format('YYYY-MM-DD') + ' - ' + end.format('YYYY-MM-DD'));
    }
    $('#Date').daterangepicker({
        startDate: start,
        endDate: end,

    },cd);

    cd(start,end);


var instance,
    min = 10,
    max = 100




$('#range').ionRangeSlider({
    type: "double",
    skin: "big",
    grid: true,
    grid_num: 4,
    min: min,
    max: max,
    step: 0.001,
    onStart: updateInputs,
    onChange: updateInputs
});
instance = $('#range').data("ionRangeSlider");


function updateInputs (data) {
	from = data.from;
    to = data.to;
    min = data.min;
    max = data.max;

    $('#input1').prop("value", from);
    $('#input2').prop("value", to);
}

$('#input1').on("input", function () {
    var val = $(this).prop("value");

    // validate
    if (val < min) {
        val = min;
    } else if (val > to) {
        val = to;
    }

    instance.update({
        from: val
    });
});

$('#input2').on("input", function () {
    var val = $(this).prop("value");
    // validate
    if (val < from) {
        val = from;
    } else if (val > max) {
        val = max;
    }

    instance.update({
        to: val
    });
});
//change subcategories if category change
$('#numerical_filter').change(function () {
    var entity =$(this).val(), values = df[entity] || [];
    var min =values['min']
    var max =values['max']

    $('#input1').prop("value", min);
    $('#input2').prop("value", max);
    instance.update({
        min: min,
        max: max,
        from: min,
        to: max
    });

});
        $(".range").ionRangeSlider({
            type: "double",
            skin: "big",
            grid: true,
            grid_num: 4,
            step: 0.001,
        });



    $("#clean").click(function(){
        $("#demo").empty();
        $("#demo2").empty();
    });

    $("#Add").click(function() {
        var visit =$("#measurement_filter").val();

        var mag =$("#categorical_filter").val();
        var e2 =$('#subcategory_filter').val();
        var mm = mag + " is: <br>" + e2
        mm = mm.replace(/,/g,"<br>")
        // if categorical filter than do nothin

        document.getElementById("demo0").innerHTML = '<p>Filter by visit as on:'+ visit +'</p><input type="hidden" value='+visit+'>'
        $( "#measurement_filter").change();

        if (mag != 'Search entity'){
        document.getElementById("demo").innerHTML = document.getElementById("demo").innerHTML + '<br>' +"  <button class='btn btn-outline-primary text-left' style='display: block; width: 100%; word-wrap: break-word; white-space: normal;'  ><span onclick='remove(this)'  class='close' > x </span><input type='hidden' name='filter' value='" + mm +"'><input type='hidden' name='cat' value='" + mag+"'>" + mm +"</button>";
        $("#categorical_filter").val('Search entity').change();

        }

        var ed = $("#numerical_filter").val();
        var mag2 = $("#range").val();
        var result = mag2.split(";");
        var fieldvalue ='<div class="fd-box2" ><span onclick="(this).closest(".fd-box2").remove()"   class="close" > x </span><input type="hidden" name="name" value="'+ed+'">'+ ed +'<input type="text" class="range" name="loan_term"  data-min="' + min + '" data-max="' + max + '" data-from="'+ result[0] +'" data-to="'+result[1]+ '"/></div>'
        if (ed != 'Search entity'){
        $(fieldvalue).appendTo($('#demo2'));
        $("#numerical_filter").val('Search entity').change();
        }
        $(".range").ionRangeSlider({
            type: "double",
            skin: "big",
            grid: true,
            grid_num: 4,
            step: 0.001,
        });

    });


});
var curtemp = new TimeSeries();
var settemp = new TimeSeries();
var settempm = new TimeSeries();
var settempp = new TimeSeries();
var pterm = new TimeSeries();
var iterm = new TimeSeries();
var dterm = new TimeSeries();
var pidval = new TimeSeries();
var avgpid = new TimeSeries();
var lastreqdone = 1;
var timeout;

function refreshinputs() {
  $.getJSON({
    url: "/allstats",
    timeout: 500,
    success: function ( resp ) {
      $("#inputSetTemp").val( resp.settemp );
      $("#inputWeekdaySleep").val( resp.weekday_sleep_time );
      $("#inputWeekdayWake").val( resp.weekday_wake_time );
      $("#inputWeekendSleep").val( resp.weekend_sleep_time );
      $("#inputWeekendWake").val( resp.weekend_wake_time );
    }
  });
}

function resettimer() {
  clearTimeout(timeout);
  timeout = setTimeout(refreshinputs, 30000);
}

function onresize() {
    var h;
    if ($(window).height()*.50 > 450 ) {
      h = 450;
    } else {
      h = $(window).height()*.50;
    }

    $("#chart").attr("width", $("#fullrow").width()-30);
    $("#chart").attr("height", h);
    $("#pidchart").attr("width", $("#fullrow").width()-30);
    $("#pidchart").attr("height", h);

    if ($(document).width() < 600) {
      $("#toggleadv").html("Adv Stats");
    } else {
      $("#toggleadv").html("Advanced Stats");
    }
}

$(document).ready(function(){
  resettimer();
  $(this).mousemove(resettimer);
  $(this).keypress(resettimer);

  onresize();
  $(window).resize(onresize);

  createTimeline();

  $(".adv").hide();
  $("#toggleadv").click(function(){
    $(".adv").toggle();
  });

  refreshinputs();

  $("#inputSetTemp").change(function(){
    $.post(
      "/settemp", 
      { settemp: $("#inputSetTemp").val() } 
    );
  });

  $("#inputWeekdaySleep").change(function(){
    $.post(
      "/setsleep",
      { 
          sleep: $("#inputWeekdaySleep").val(),
          weekday: "True"
      }
    );
  });

  $("#inputWeekendSleep").change(function(){
    $.post(
      "/setsleep",
      { 
          sleep: $("#inputWeekendSleep").val(),
          weekday: "False"
      }
    );
  });

  $("#inputWeekdayWake").change(function(){
    $.post(
      "/setwake",
      { 
          wake: $("#inputWeekdayWake").val(),
          weekday: "True"
      }
    );
  });

  $("#inputWeekendWake").change(function(){
    $.post(
      "/setwake",
      { 
          wake: $("#inputWeekendWake").val(),
          weekday: "False"
      }
    );
  });

  $("#btnTimerDisable").click(function(){
    $.post("/scheduler",{ scheduler: "False" });
    $("#inputWeekdayWake").hide();
    $("#labelWeekdayWake").hide();
    $("#inputWeekdaySleep").hide();
    $("#labelWeekdaySleep").hide();
    $("#inputWeekendWake").hide();
    $("#labelWeekendWake").hide();
    $("#inputWeekendSleep").hide();
    $("#labelWeekendSleep").hide();
    $("#btnTimerDisable").hide();
    $("#btnTimerEnable").show();
  });

  $("#btnTimerEnable").click(function(){
    $.post("/scheduler",{ scheduler: "True" });
    $("#inputWeekdayWake").show();
    $("#labelWeekdayWake").show();
    $("#inputWeekdaySleep").show();
    $("#labelWeekdaySleep").show();
    $("#inputWeekendWake").show();
    $("#labelWeekendWake").show();
    $("#inputWeekendSleep").show();
    $("#labelWeekendSleep").show();
    $("#btnTimerDisable").show();
    $("#btnTimerEnable").hide();
  });

  $("#schedDisabledWakeup").click(function(){
    $.post("/sched_disabled_op",{ op: "wakeup" });
      $("#schedDisabledWakeup").removeClass("btn-outline-primary").addClass("btn-primary")
      $("#schedDisabledGotosleep").removeClass("btn-primary").addClass("btn-outline-primary")
  });

  $("#schedDisabledGotosleep").click(function(){
    $.post("/sched_disabled_op",{ op: "gotosleep" });
      $("#schedDisabledGotosleep").removeClass("btn-outline-primary").addClass("btn-primary")
      $("#schedDisabledWakeup").removeClass("btn-primary").addClass("btn-outline-primary")
  });

});

setInterval(function() {
  if (lastreqdone == 1) {
    $.getJSON({
      url: "/allstats",
      timeout: 500,
      success: function ( resp ) {
        if (resp.sched_enabled == true) {
         $("#inputWeekdayWake").show();
         $("#inputWeekdaySleep").show();
         $("#inputWeekendWake").show();
         $("#inputWeekendSleep").show();
         $("#btnTimerSet").show();
         $("#btnTimerDisable").show();
         $("#btnTimerEnable").hide();
        } else {
         $("#inputWeekdayWake").hide();
         $("#inputWeekdaySleep").hide();
         $("#inputWeekendWake").hide();
         $("#inputWeekendSleep").hide();
         $("#btnTimerSet").hide();
         $("#btnTimerDisable").hide();
         $("#btnTimerEnable").show();
        }
        if (resp.is_awake == true) {
         $("#targetTimer").show();
         $("#awakeTime").show();
         $("#awakeTimer").show();
        } else {
         $("#targetTimer").hide();
         $("#awakeTime").hide();
         $("#awakeTimer").hide();
        }
        if (resp.sched_disabled_op === "wakeup") {
          $("#schedDisabledWakeup").removeClass("btn-outline-primary").addClass("btn-primary")
          $("#schedDisabledGotosleep").removeClass("btn-primary").addClass("btn-outline-primary")
        } else {
          $("#schedDisabledGotosleep").removeClass("btn-outline-primary").addClass("btn-primary")
          $("#schedDisabledWakeup").removeClass("btn-primary").addClass("btn-outline-primary")
        }
        curtemp.append(new Date().getTime(), resp.tempf);
        settemp.append(new Date().getTime(), resp.settemp);
        settempm.append(new Date().getTime(), resp.settemp-4);
        settempp.append(new Date().getTime(), resp.settemp+4);
        pterm.append(new Date().getTime(), resp.pterm);
        iterm.append(new Date().getTime(), resp.iterm);
        dterm.append(new Date().getTime(), resp.dterm);
        pidval.append(new Date().getTime(), resp.pidval);
        avgpid.append(new Date().getTime(), resp.avgpid);
        $("#curtemp").html(resp.tempf.toFixed(2));
        $("#timesincetarget").html(resp.time_outside_target_temp.split(".")[0]);
        $("#timesinceawake").html(resp.time_since_awake.split(".")[0]);
        $("#awaketime").html(String(resp.awake_time).split(".")[0]);
        $("#pterm").html(resp.pterm.toFixed(2));
        $("#iterm").html(resp.iterm.toFixed(2));
        $("#dterm").html(resp.dterm.toFixed(2));
        $("#pidval").html(resp.pidval.toFixed(2));
        $("#avgpid").html(resp.avgpid.toFixed(2));
      },
      complete: function () {
        lastreqdone = 1;
      }
    });
    lastreqdone = 0;
  }
}, 100);

function createTimeline() {
  var chart = new SmoothieChart({grid:{verticalSections:3},minValueScale:1.05,maxValueScale:1.05});
  chart.addTimeSeries(settemp, {lineWidth:1,strokeStyle:'#ffff00'});
  chart.addTimeSeries(settempm, {lineWidth:1,strokeStyle:'#ffffff'});
  chart.addTimeSeries(settempp, {lineWidth:1,strokeStyle:'#ffffff'});
  chart.addTimeSeries(curtemp, {lineWidth:3,strokeStyle:'#ff0000'});
  chart.streamTo(document.getElementById("chart"), 500);

  var pidchart = new SmoothieChart({grid:{verticalSections:3},minValueScale:1.05,maxValueScale:1.05});
  pidchart.addTimeSeries(pterm, {lineWidth:2,strokeStyle:'#ff0000'});
  pidchart.addTimeSeries(iterm, {lineWidth:2,strokeStyle:'#00ff00'});
  pidchart.addTimeSeries(dterm, {lineWidth:2,strokeStyle:'#0000ff'});
  pidchart.addTimeSeries(pidval, {lineWidth:2,strokeStyle:'#ffff00'});
  pidchart.addTimeSeries(avgpid, {lineWidth:2,strokeStyle:'#ff00ff'});
  pidchart.streamTo(document.getElementById("pidchart"), 500);
}

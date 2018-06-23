var mh;
var socket;
var colorWheel1;
var pin = '';
var number_bak = 0;
var socket_open = false;
var selected_color = 1;

$(document).ready(function(){
  // Init Slider
  init();

  // confirm button
  $('#b_sendcode').click(function(){
    arr = {
      action: "compare_code",
      arg: {pin:pin}
    };
    socket.send(JSON.stringify(arr));
    playClick1();
  });

  // change code button
  $('#b_changecode').click(function(){
    arr = {
      action: "change_code",
      arg: {pin:pin}
    };
    socket.send(JSON.stringify(arr));
  });

  // clear button
  $('#b_reset_code').click(function(){
    reset_code();
  });

  $('#b_lock_safe').click(function(){
    arr = {
      action: "lock"
    };
    socket.send(JSON.stringify(arr));
  })

  // Kamerabutton
  $('#b_snapshot').click(function(){
    takeCameraPicture();
    playClick1();
  });

  $('button').click(function(){
    playClick1();
  });

  $('.pp_number').click(function(){
    add_pin($(this).attr('number'));
  });





  /*
  // Event, wenn das Video fertig ist - dann weiter
  $('video').bind('ended', function (e) {
    // do something
    console.log('ready');
    $(this).fadeOut(100,function(){
        $('#container_slider').fadeIn();
        init();
    });
  });
  */

  $('#chk_pinview').click(function(){
      if ($(this).prop('checked') == true)
      {

        $('#pinpad').show();
        $('#knopp').hide();
      } else {
        $('#pinpad').hide();
        $('#knopp').show();
      }
  });

  $('#chk_color').click(function(){
      if ($(this).prop('checked') == true){
        selected_color = 2;
      } else {
        selected_color = 1;
      }
      get_rgb(selected_color);
  });

  $('.sl').click(function(){
      selected_color = $(this).attr('selection');
  });

  // timer zum Holen des State
  tick();

});

function select_color(which){
  $('.selected_color').css('border','');
    $('div[choice='+which+']').css('border','1px solid yellow');
}

function ts()
{
  var now = new Date();
  return(now.getTime());
}


function reset_code()
{

  $('.dial').val(0).trigger('change');
  $('#pinfield').html('').css('color','black');
  pin = '';
}

function add_pin(number)
{
  var s_pin = pin.toString();
  var s_number = number.toString();
  pin = s_pin + s_number;
  $('#pinfield').html(pin);
}

function playClick()
{
  $("#click").trigger('play');
}

function playClick1()
{
  $("#click1").trigger('play');
}

function lock_safe(){
  arr = {
    action: "lock",
  };
  socket.send(JSON.stringify(arr));
}

function set_colorwheel(rgb)
{
  colorWheel1.color.rgb = rgb;
  return true;
}

function init() {

  // Socket öffnen
  socket = new WebSocket("ws://" + window.location.hostname + ":8000");
  mh = new messagehandler();
  socket.onconnect = function() {
    console.log("connected to websocket");
  };
  // Eventhandler Socket
  socket.onmessage = function(event) {
    console.log("message:" + event.data);
    mh.handle(event.data);
  };

  // erst wenn offen ist kann der Colorpicker initialisiert werden, sonst geht eine Message eher raus als der Port offen ist.
  socket.onopen = function(){
    socket_open = true;
  };

  var width = window.innerWidth || (window.document.documentElement.clientWidth || window.document.body.clientWidth);
  var height = window.innerHeight || (window.document.documentElement.clientHeight || window.document.body.clientHeight);
  var sliderheight = height -50;
  var height_knopp = height / 3;

  // Slider initialisieren
  $('.slick').slick({
    dots: true,
    infinite: true,
    speed: 200,
    slidesToShow: 1,
    centerMode: true,
    arrows: true,
    adaptiveHeight: false,

    //prevArrow:"<img class='a-left control-c prev slick-prev' src='arrow-left-thin.svg'>",
    //nextArrow:"<img class='a-right control-c next slick-next' src='arrow-right-thin.svg'>"
  });



  //$('.slick_inn').css('height',sliderheight + 'px');

  $('.slick').on('swipe', function(event, slick, direction){
    console.log("current page:" +slick.currentSlide);
    if(slick.currentSlide == 1){
      get_rgb(selected_color);
    }
    if(slick.currentSlide == 2){
      takeCameraPicture();
    }
  // left
  });


  // Verschiebesperre
  $(function() {
    $('*[draggable!=true]','#knopp').unbind('dragstart');

    // Init Knob
    $(".dial").knob({
      //        'width':"60%",
              'min':0,
              'max':99,
      //        'displayPrevious':true,
      //        'cursor':true,
      //        'thickness':0.3,
      'value':0, 'opacity': 0.5,
      'release' : function (v) { add_pin(v); playClick();  },
      //'change' : function (v) { playClick(); },



    });
  });

  $("#knopp").on("draggable mouseenter mousedown touchstart",function(event){
      event.stopPropagation();
  });


  //$('#knopp').css('margin-top',sliderheight / 2 - height_knopp / 2 + 'px').css('width',height_knopp + 'px').css('height',height_knopp + 'px');
  //$('#knopp').css('width',height_knopp + 'px').css('height',height_knopp + 'px');
  //$('#pinfield').css('margin-top',sliderheight / 4 - 20 + 'px').css('margin-left',width / 2  + 'px');



//});

  //$('#page3').css('background-image','url("DCIM/temp.jpg")').css('background-size','100%');

  colorWheel1 = new iro.ColorPicker("#colorpicker1", {
    width: 500,
    height: 500,
    markerRadius: 12,
    sliderHeight: 50,
    borderWidth: 2,
  });

  colorWheel1.on("color:change", function(color, changes) {
    //change_rgb(1,color.rgb);
    var rgb = color.rgb.r +','+ color.rgb.g +','+ color.rgb.b
    //$('#box1').html(draw_box('rgb('+rgb+')',6,'rgba(0,0,250,0.1)'));
  });



  colorWheel1.on("input:end",function(color){
    store_rgb(selected_color,color.rgb)
  });

};

/*
function draw_box(edgecolor, strokewidth, fillcolor){
  var svg = '<svg width="200" height="140" id="box1">';
      svg += '<rect x="5" y="15" width="120" height="120" style="fill:'+fillcolor+';stroke:'+edgecolor+'; stroke-width:'+strokewidth+'" />';
      svg += '<polygon points="5,15 63,0 183,0 125,15" style="fill:'+fillcolor+'; stroke:'+edgecolor+'; stroke-width:'+strokewidth+'" />';
      svg += '<polygon points="125,135 125,15 183,0 183,110" style="fill:'+fillcolor+'; stroke:'+edgecolor+'; stroke-width:'+strokewidth+'" />';
      svg += ' </svg>';
      return(svg);
}
*/

function change_rgb(which,rgb)
{
  var arr = {
    action: "change_ledcolor"+which,
    arg: rgb
  };
  if(socket_open){socket.send(JSON.stringify(arr));}
}

function store_rgb(which,rgb)
{
  var arr = {
    action: "store_ledcolor"+which,
    arg: rgb
  };
  if(socket_open){socket.send(JSON.stringify(arr));}
}

function get_rgb(which)
{
  var arr = {
    action: "get_ledcolor",
    arg: which
  };
  if(socket_open){socket.send(JSON.stringify(arr));}
}

function takeCameraPicture()
{

  var arr = {
    action: "cameraPicture",
    arg: ts()
  };
  if(socket_open){socket.send(JSON.stringify(arr));}
}


function get_state()
{
  var arr = {
    action: "get_state"
  };
  // darf erst gesendet werden, wenn socket auch wirklich da ist
  if(socket_open){socket.send(JSON.stringify(arr));}
  //console.log(socket)
}

function tick()
{
  var intervall = 5000;
  //get_state();
  window.setTimeout("tick();", intervall);
}

class messagehandler {
  /*
  constructor() {
    this.items = {
      div1: document.getElementById('testDiv1'),
      div2: document.getElementById('testDiv2'),
      div3: document.getElementById('testDiv3'),
      body: document.body,
      testimage: document.getElementById('testImage')
    };
    this.options = {
      "backgroundcolor": "style",
      "textcolor": "style",
      "text": "innerHTML",
      "backgroundimage": "style",
      "src": "src",
      "display": "style"
    };
    this.styleOptions = {
      "backgroundcolor": "backgroundColor",
      "textcolor": "color",
      "backgroundimage": "backgroundImage",
      "display": "display"
    };
  };
  */
  handle(msg) {
    var event = JSON.parse(msg);
    //for (var event in rootEvent) {
    //console.log(event);
    switch (event.action) {
      case "html":
        if (this.options.hasOwnProperty(event.option) && this.items.hasOwnProperty(event.item)) {
          // wenn option style
          if (this.options[event.option] == "style") {
            if (this.styleOptions.hasOwnProperty(event.option))
              this.items[event.item]["style"][this.styleOptions[event.option]] = event.value;
            else console.log("style option wrong");
          } else {
            // Sonst in ein HTML Element schreiben
            this.items[event.item][this.options[event.option]] = event.value;
          };
        } else console.log("item or option wrong");
        return;
      case "text":
        console.log(event.value);
        this.items[event.item][this.options[event.option]] = event.value;
      case "result_compare_code":
        if(event.value == 0){
          // Blinkern weil falsch und Wert löschen
          $('#pinfield').css('color','red')
            .fadeIn(100).fadeOut(100)
            .fadeIn(100).fadeOut(100)
            .fadeIn(100).fadeOut(100)
            .fadeIn(100).fadeOut(100)
            .fadeIn(100,function(){
            reset_code();
          });

        }else{
          reset_code();
          $('#pinfield').css('color','lime').html('Door is opening...');
          // Schloss fährt auf -> Zahleneingabe weg und Animation zeigen.
        }
      case "result_change_password":
        if(event.value == 1){
          $('#pinfield').html('Passwort geändert');
          reset_code();
        }

      case "result_get_rgb":
        if(event.value != undefined){
          set_colorwheel(event.value);
        }

      case "result_camerapicture":
        if(event.value == 1){
          var filename = event.filename;
          $('#cameraimage').html('<img src="'+filename+'" alt="'+filename+'" />');
          //$('#page3').css('background-image','url("'+filename+'")').css('background-size','100%');
        }
        return;
      case "unlocked":
        $('#b_lock_safe').css('display', 'block');
    };
  };
};

var mh;
var socket;
var colorWheel1;
var pin = '';
var number_bak = 0;
var socket_open = false;
var selected_color = 1;

var current_state = -1; // Status zum Steuern der Anazeige

$(document).ready(function() {
  // Init Slider
  // init();

  // confirm button
  $('#b_sendcode').click(function() {
    var arr = {
      action: "compare_code",
      arg: {
        pin: pin
      }
    };
    socket.send(JSON.stringify(arr));
    reset_code();
    //playClick1();
  });
  
  // change code button
  $('#b_newpin').click(function() {
    
    $('#container_isopen').fadeOut(500,function(){
      $('#container_isopen_change_pin').fadeIn(500);
    });
  });

  // change code button
  $('#b_changecode').click(function() {
    var arr = {
      action: "change_code",
      arg: {
        pin: pin
      }
    };
    socket.send(JSON.stringify(arr));
    reset_code();
  });// change code button
  
  $('#b_resetcode').click(function() {
    var arr = {
      action: "change_code",
      arg: {
        pin: '1234'
      }
    };
    socket.send(JSON.stringify(arr));
    reset_code();
  });

  // clear button
  $('#b_reset_code').click(function() {
    reset_code();
  });

  $('#b_lock_safe').click(function() {
    lock_safe();
  })

  /*
  // Kamerabutton
  $('#b_snapshot').click(function() {
    alert('test');
    //takeCameraPicture();
    //playClick1();
  });
*/
  $('button').click(function() {
    playClick1();
  });  
  
  $('button#b_snapshot').click(function() {
    takeCameraPicture();
  });

  $('.pp_number').click(function() {
    add_pin($(this).attr('number'));
  });

  
  // Event, wenn das Video fertig ist - dann weiter
  $('video').bind('ended', function (e) {
    console.log('ready');
    $(this).fadeOut(100,function(){
        $('.swiper-container').fadeIn();
        //$('main').show();
        init();
    });
  });
  

  $('#chk_pinview').click(function() {
    var arr;
    if ($(this).prop('checked') == true) {
      arr = {
        action: "pinView",
        arg: {
          view: "pad"
        }
      };
      $('#pinpad1').show();
      $('#knopp').hide();
    } else {
      arr = {
        action: "pinView",
        arg: {
          view: "knopp"
        }
      };
      $('#pinpad1').hide();
      $('#knopp').show();
    }
    socket.send(JSON.stringify(arr));
  });

  $('#chk_color').click(function() {
    if ($(this).prop('checked') == true) {
      selected_color = 2;
    } else {
      selected_color = 1;
    }
    get_rgb(selected_color);
  });

  $('.sl').click(function() {
    selected_color = $(this).attr('selection');
  });

  // timer zum Holen des State oder zum öffnen des sockets
  setInterval(tick, 10000);
  tick();
});

function select_color(which) {
  $('.selected_color').css('border', '');
  $('div[choice=' + which + ']').css('border', '1px solid yellow');
}

function ts() {
  var now = new Date();
  return (now.getTime());
}

function reset_code() {
  $('.dial').val(0).trigger('change');
  $('.pinfield').html('').css('color', 'black');
  pin = '';
}

function add_pin(number) {
  var s_pin = pin.toString();
  var s_number = number.toString();
  pin = s_pin + s_number;
  $('.pinfield').html(pin);
}

function playClick() {
  $("#click").trigger('play');
}

function playClick1() {
  $("#click1").trigger('play');
}

function lock_safe() {
  var arr = {
    action: "lock",
  };
  socket.send(JSON.stringify(arr));
  reset_code();
}

function set_colorwheel(rgb) {
  colorWheel1.color.rgb = rgb;
  return true;
}

function open_socket() {
  console.log('trying to open Websocket Port 8000')
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

  // erst wenn socket offen ist kann eine Message verschickt werden
  socket.onopen = function() {
    socket_open = true;
    console.log('websocket is open');
    get_state();
  };
  // wenn geschlossen wurde, darf per Timer nochmal das Öffnen probiert werden
  socket.onclose = function() {
    socket_open = false;
    console.log('websocket is closed')
  };
}

function init() {
  var width = window.innerWidth || (window.document.documentElement.clientWidth || window.document.body.clientWidth);
  var height = window.innerHeight || (window.document.documentElement.clientHeight || window.document.body.clientHeight);
  var sliderheight = height - 50;
  var height_knopp = height / 3;

  // Slider initialisieren

  mySwiper = new Swiper ('.swiper-container', {
      // Optional parameters
      direction: 'horizontal',
      loop: false,
      noSwiping: true,

      // If we need pagination
      pagination: {
        el: '.swiper-pagination',
        clickable: true,
      },

      // Navigation arrows
      navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
      },
      
      

      on: {
        slideChangeTransitionEnd: function(){
          //console.log("acticeIndex:"+this.activeIndex);
          console.log("realIndex:"+this.realIndex);
          switch (this.realIndex){
            case 0:
              get_state();
              break;
            case 1:
              get_rgb(selected_color);
              break;
            case 2:
              takeCameraPicture();
              break;
            default:
              break;
          }
        },
        init: function () {
          // Events der Elemente
          get_state();
        },
      },
      // And if we need scrollbar
      // scrollbar: {
      //   el: '.swiper-scrollbar',
      // },
    })

  // $('.slick').slick({
  //   dots: true,
  //   infinite: true,
  //   speed: 200,
  //   slidesToShow: 1,
  //   centerMode: true,
  //   arrows: true,
  //   adaptiveHeight: false,
  //
  //   //prevArrow:"<img class='a-left control-c prev slick-prev' src='arrow-left-thin.svg'>",
  //   //nextArrow:"<img class='a-right control-c next slick-next' src='arrow-right-thin.svg'>"
  // });

  //$('.slick_inn').css('height',sliderheight + 'px');

  // $('.slick').on('swipe', function(event, slick, direction) {
  //   console.log("current page:" + slick.currentSlide);
  //   if (slick.currentSlide == 1) {
  //     get_rgb(selected_color);
  //   }
  //   if (slick.currentSlide == 2) {
  //     takeCameraPicture();
  //   }
  //   // left
  // });

  // Verschiebesperre
  // $('*[draggable!=true]', '#knopp').unbind('dragstart');
  // Init Knob
  $(".dial").knob({
    'min': 0,
    'max': 99,
    'value': 0,
    'opacity': 0.5,
    'release': function(v) {
      add_pin(v);
      playClick();
    },
  });

  $("#knopp").on("draggable mouseenter mousedown touchstart", function(event) {
    event.stopPropagation();
  });

  colorWheel1 = new iro.ColorPicker("#colorpicker1", {
    width: 500,
    height: 500,
    markerRadius: 12,
    sliderHeight: 50,
    borderWidth: 2,
  });

  colorWheel1.on("input:end", function(color) {
    store_rgb(selected_color, color.rgb)
  });

};

function store_rgb(which, rgb) {
  var arr = {
    action: "store_ledcolor" + which,
    arg: rgb
  };
  if (socket_open) {
    socket.send(JSON.stringify(arr));
  }
}

function get_rgb(which) {
  var arr = {
    action: "get_ledcolor",
    arg: which
  };
  if (socket_open) {
    socket.send(JSON.stringify(arr));
  }
}

function light(on) {
  var arr = {
    action: (on) ? "ledon" : "ledoff"
  };
  if (socket_open) {
    socket.send(JSON.stringify(arr));
  }
}

function takeCameraPicture() {
  var arr = {
    action: "cameraPicture",
    arg: ts()
  };
  if (socket_open) {
    socket.send(JSON.stringify(arr));
  }
}

function get_state() {
  var arr = {
    action: "get_state"
  };
  if (socket_open) {
    socket.send(JSON.stringify(arr));
  }
}

function tick() {
  if (socket_open == false) {
    open_socket();
  }
}

class messagehandler {
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
        return;
      case "result_compare_code":
        if (event.value == 0) {
          // Blinkern weil falsch und Wert löschen
          $('.pinfield').css('color', 'red')
            .fadeIn(100).fadeOut(100)
            .fadeIn(100).fadeOut(100)
            .fadeIn(100).fadeOut(100)
            .fadeIn(100).fadeOut(100)
            .fadeIn(100, function() {
              reset_code();
            });

        } else {
          reset_code();
          
        }
        return;
        
      case "result_change_password":
        if (event.value == 1) {
          //$('.pinfield').val('Passwort geändert');
          $('.messagefield').html('Pin was changed successfully');
          $('#container_isopen_change_pin').fadeOut(500,function(){
            $('#container_isopen_message').fadeIn(200,function(){
              $('#container_isopen_message').fadeOut(3000,function(){
                $('#container_isopen').fadeIn(500,function(){
                  reset_code();
                });
              });
            });
          });
        }
        return;
        
      case "result_get_rgb":
        if (event.value != undefined) {
          set_colorwheel(event.value);
        }
        return;
        
      case "state":
        if (event.value != undefined) {
          current_state = parseInt(event.value);
          console.log("state",current_state);
          $("div.container_page1").hide(); // erstmal alles verstecken
          switch(current_state){
            
            case 0: $("div#container_authorisation").show()
              console.log('Safe is closed');
              break;
            case 1: $("div#container_inprogress").show();
              $("#l_progress1").html("Boltwork is opening...");
              break;
            case 2: $("div#container_inprogress").show();
              $("#l_progress1").html("Boltwork is closing...");
              break;
            case 3: $("div#container_inprogress").show();
              $("#l_progress1").html("Boltwork is closing...");
              break;
            case 4: $("div#container_inprogress").show();
              $("#l_progress1").html("Safe Door is opening...");
              break;
            case 5: $("div#container_inprogress").show();
              $("#l_progress1").html("Safe Door is closing...");
              break;
            case 6: $("div#container_inprogress").show();
              $("#l_progress1").html("Safe is unlocked...");
              break;
            case 7: $("div#container_inprogress").show();
              $("#l_progress1").html("Safedoor initializing...");
              break;
            case 8: $("div#container_isopen").show();
              //$("#l_progress1").html("Safedoor is open...");
              break;
            //case 9: $("div#container_inprogress").show();
            case 9: $("div#container_authorisation").show();
              $("#l_progress1").html("Error while moving the Safedoor");
              break;
          } 
        }
        return;
        
      case "result_camerapicture":
        if (event.value == 1) {
          var filename = event.filename;
          $('#cameraimage').html('<img src="' + filename + '" alt="' + filename + '" />');
          //$('#page3').css('background-image','url("'+filename+'")').css('background-size','100%');
        }
        return;
      case "unlocked":
        $('#b_lock_safe').css('display', 'block');
        return;
    };
  };
};

var mh;
var socket;
var colorWheel;

window.onload = function() {
  console.log("ready");
  startup();
};

function startup() {
  socket = new WebSocket("ws://" + window.location.hostname + ":8000");
  mh = new messagehandler();
  socket.onconnect = function() {
    console.log("connected to websocket");
  };
  socket.onmessage = function(event) {
    console.log("message:" + event.data);
    mh.handle(event.data);
  };
  colorWheel = new iro.ColorPicker("#colorWheelDemo", {
    // width: 320,
    // height: 320,
    // padding: 4,
    // sliderMargin: 24
    // markerRadius: 8,
    // color: "rgb(68, 255, 158)",
    // CSS: {} // apply colors to any elements
  });
  colorWheel.on("color:change", function(color, changes) {
    console.log(color.rgb);
    arr = {
      action: "ledcolor",
      arg: color.rgb
    };
    socket.send(JSON.stringify(arr));
  });
  document.getElementById('b_snapshot').onclick = function(){
    takeCameraPicture();
  };
};

class messagehandler {
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
      default:
        // console.log("action not supported");
        return;
    };
  };
};


function testfunction(arg) {
  var arr1 = {
    action: "html",
    option: "text",
    item: "div1",
    value: "hallowelt"
  };
  var arr2 = {
    action: "html",
    option: "backgroundcolor",
    item: "div2",
    value: "darkgrey"
  };
  var arr3 = {
    action: "html",
    option: "textcolor",
    item: "div3",
    value: "navy"
  };
  var arr4 = {
    action: "ledon"
  };
  var arr5 = {
    action: "ledoff"
  };
  var arr6 = {
    action: "ledcolor",
    arg: {
      r: 50,
      g: 100,
      b: 10
    }
  };
  var arr7 = {
    action: "cameraPicture",
    arg: {
      
    }
  };
  socket.send(JSON.stringify(eval(arg)));
};

function takeCameraPicture()
{
  var arr = {
    action: "cameraPicture",
    arg: {
      
    }
  };
  socket.send(JSON.stringify(arr));
}

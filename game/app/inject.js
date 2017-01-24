/**
 * This script uses various hacks to interact with the game. It is injected into the active browser
 * window and provides a simple HTTP API for playing the game and more specifically, for framing it
 * as an reinforcement learning task.
 */

var remote = require('electron').remote;
var express = remote.require("express");

remote.app.log("Starting game...");
document.getElementById('nick').value = 'deepsnek';
document.onkeydown({keyCode: 13});

var engine = {
    quit: function () {
        remote.app.quit();
    },
    done: function () {
        var el = document.querySelector("#playh .nsi .nsi");
        var text = el.innerText.trim()
        return text == "Play Again";
    },
    ready: function () {
        return !(!(document.querySelector(".nsi span span")))
    },
    get_score: function () {
        try {
            var el = document.querySelector(".nsi span span");
            var text = el.parentElement.children[1].innerText;
            return parseInt(text);
        } catch (e) { return 0; }
    },
    get_image: function () {
        var el = document.querySelector("canvas.nsi");
        var data = el.toDataURL().replace(/^data:image\/\w+;base64,/, "");
        return new Buffer(data, 'base64')
    },
    key_press: function (keyCode, duration, callback) {
        document.onkeydown({'keyCode': keyCode});
        setTimeout(function () {
            document.onkeyup({'keyCode': keyCode});
            callback();
        }, duration)
    }
}

setInterval(function () {
    if (engine.done()) {
        remote.app.log("Detected game over, exiting in 30 seconds....");
        setTimeout(function () {
            remote.app.log("Autoexiting...");
            engine.quit();
        }, 30000);
    }
}, 10000);

setTimeout(function () {
    if (!engine.ready()) {
        remote.app.log("Game didn't start in time, exiting...");
        engine.quit();
    } else {
        remote.app.log("Game running...");
    }
}, 10000)

remote.app.log("Starting server on port " + PORT_NUM + "...");
var server = express();
server.listen(PORT_NUM);

server.use(function (req, res, next) {
    remote.app.log("GET " + req.originalUrl);
    next()
});

server.get("/quit", function (req, res) {
    res.status(202).send();
    engine.quit()
})

server.get("/done", function (req, res) {
    res.status(202).send(String(engine.done()));
    if (engine.done()) engine.quit();
});

server.get("/ready", function (req, res) {
    res.status(202).send(String(engine.ready()));
});

server.get("/state", function (req, res) {
    var img = engine.get_image();
    res.writeHead(200, {
        'Content-Type': 'image/png',
        'Content-Length': img.length
    });
    res.end(img); 
})

server.get("/score", function (req, res) {
    res.send(String(engine.get_score()));
})

server.get("/action/:command/:duration", function (req, res) {
    var keyCode = false;
    if (req.params.command == "left") keyCode = 37;
    if (req.params.command == "right") keyCode = 39;
    if (req.params.command == "speed") keyCode = 32;
    engine.key_press(keyCode, parseInt(req.params.duration), function () {
        res.send(String(engine.get_score()));
    });
})

remote.app.log("Listening...");

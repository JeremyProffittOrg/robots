/* R2-FABLE control page.
 *
 * Plain JavaScript, no build step and no dependencies, so the page works from
 * the Pi's own access point with no internet.
 *
 * The joystick canvas produces x and y in -1..1.  They are sent to the server
 * at 20 Hz while a finger is down and at 5 Hz while it is not, which doubles as
 * the keep-alive the server's watchdog is looking for.
 */

(function () {
  "use strict";

  var DRIVE_HZ = 20;
  var IDLE_HZ = 5;

  var socket = null;
  var connected = false;
  var reconnectDelay = 500;

  var stick = { x: 0.0, y: 0.0, active: false, pointerId: null };
  var lastSent = { x: null, y: null, at: 0 };

  var canvas = document.getElementById("joystick");
  var context = canvas.getContext("2d");
  var linkState = document.getElementById("link-state");
  var batteryPill = document.getElementById("battery");
  var readout = document.getElementById("drive-readout");
  var capSlider = document.getElementById("cap");
  var capValue = document.getElementById("cap-value");
  var headSlider = document.getElementById("head-duty");
  var headValue = document.getElementById("head-duty-value");
  var enableBox = document.getElementById("enable");
  var soundsBox = document.getElementById("sounds");
  var stopButton = document.getElementById("stop");
  var driveNote = document.getElementById("drive-note");
  var stanceState = document.getElementById("stance-state");
  var stanceReason = document.getElementById("stance-reason");
  var stancePose = document.getElementById("stance-pose");
  var stanceBlocks = document.getElementById("stance-blocks");
  var stanceFault = document.getElementById("stance-fault");
  var clearFaultButton = document.getElementById("clear-fault");
  var stanceButtons = Array.prototype.slice.call(document.querySelectorAll("[data-stance]"));
  var headButtons = Array.prototype.slice.call(document.querySelectorAll("[data-head],[data-nudge]"));

  /* Interlock view from the last status frame.  Nothing is allowed until the
     server has reported a fresh stance status from the KB2040. */
  var driveAllowed = false;
  var headAllowed = false;
  var stanceHeld = 0;

  /* ---------------------------------------------------------------- socket */

  function send(message) {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
      return true;
    }
    return false;
  }

  function connect() {
    var scheme = window.location.protocol === "https:" ? "wss" : "ws";
    socket = new WebSocket(scheme + "://" + window.location.host + "/ws");

    socket.onopen = function () {
      connected = true;
      reconnectDelay = 500;
      setLink("link up", true);
    };

    socket.onclose = function () {
      connected = false;
      stanceHeld = 0;
      renderStance(null);
      setLink("link down", false);
      window.setTimeout(connect, reconnectDelay);
      reconnectDelay = Math.min(reconnectDelay * 2, 5000);
    };

    socket.onerror = function () {
      setLink("link error", false);
    };

    socket.onmessage = function (event) {
      var message;
      try {
        message = JSON.parse(event.data);
      } catch (error) {
        return;
      }
      if (message.type === "hello") {
        onHello(message);
      } else if (message.type === "status") {
        onStatus(message);
      } else if (message.type === "notice") {
        setLink(message.text, false);
      }
    };
  }

  function setLink(text, up) {
    linkState.textContent = text;
    linkState.className = "pill " + (up ? "pill-up" : "pill-down");
  }

  function onHello(message) {
    capSlider.min = Math.round(message.speed_cap_min * 100);
    capSlider.max = Math.round(message.speed_cap_max * 100);
    capSlider.value = Math.round(message.speed_cap * 100);
    capValue.textContent = capSlider.value + "%";
    headSlider.value = Math.round(message.head_duty * 100);
    headValue.textContent = headSlider.value + "%";
    buildSoundButtons(message.sounds || [], message.audio_backend);
  }

  function onStatus(message) {
    var link = message.link || {};
    if (link.connected && link.fresh) {
      setLink("controller ok", true);
    } else if (link.connected) {
      setLink("controller quiet", false);
    } else {
      setLink(link.error ? "no controller" : "controller down", false);
    }

    var battery = message.battery || {};
    if (battery.volts !== null && battery.volts !== undefined) {
      var percent = Math.round((battery.charge || 0) * 100);
      batteryPill.textContent = battery.volts.toFixed(2) + " V  " + percent + "%";
      batteryPill.className = "pill " + (battery.critical ? "pill-down" : "pill-up");
    } else {
      batteryPill.textContent = "battery --";
      batteryPill.className = "pill";
    }

    enableBox.checked = !!message.enabled;
    renderStance(message.stance || null);

    var commanded = link.commanded || [0, 0, 0, 0];
    readout.textContent =
      "x " + stick.x.toFixed(2) + "   y " + stick.y.toFixed(2) +
      "   L " + commanded[0] + " R " + commanded[1] + " C " + commanded[2] +
      " H " + commanded[3];
  }

  /* ---------------------------------------------------------------- stance */

  function stanceLabel(target) {
    return target === 2 ? "Two feet" : "Three feet";
  }

  function releaseStance() {
    if (stanceHeld !== 0) {
      stanceHeld = 0;
      send({ type: "stance", target: 0 });
    }
  }

  /* Grey out every control the interlock forbids and say why.  A stance
     button stays enabled only while it may start, or while it is the held
     control of the change in progress. */
  function renderStance(stance) {
    var available = !!(stance && stance.available);
    var moving = available && (stance.state === "RETRACTING" || stance.state === "DEPLOYING");
    driveAllowed = available && !!stance.drive_allowed;
    headAllowed = available && !!stance.head_allowed;

    stanceState.textContent = available ? stance.label + (stance.phase && stance.phase !== "NONE" ? " · " + stance.phase : "") : "stance unknown";
    stanceState.className = "pill " + (!available || stance.state === "FAULT" ? "pill-down" : (driveAllowed ? "pill-up" : ""));
    stanceReason.textContent = stance ? stance.reason : "no connection to the robot";
    if (available) {
      stancePose.textContent =
        "actuator " + (stance.position_mm === null ? "invalid" : stance.position_mm.toFixed(1) + " mm") +
        "   lock " + stance.lock_label +
        "   pack " + (stance.pack_volts === null ? "--" : stance.pack_volts.toFixed(2) + " V");
    } else {
      stancePose.textContent = "actuator --   lock --   pack --";
    }

    var blocks = [];
    stanceButtons.forEach(function (button) {
      var target = Number(button.getAttribute("data-stance"));
      var can = available && (target === 2 ? stance.can_two_foot : stance.can_three_foot);
      var why = available ? (target === 2 ? stance.two_foot_block : stance.three_foot_block) : "no stance status";
      var ownChange = moving && stanceHeld === target;
      button.disabled = !(can || ownChange);
      if (button.disabled && stanceHeld === target) {
        releaseStance();
      }
      if (button.disabled && why) {
        blocks.push(stanceLabel(target) + ": " + why);
      }
    });
    if (stance && stance.needs_release) {
      blocks.push("release the stance control, then press again");
    }
    stanceBlocks.textContent = blocks.join("  ·  ");

    stanceFault.textContent = available && stance.state === "FAULT" ? "Fault " + stance.fault + ": " + stance.reason : "";
    clearFaultButton.disabled = !(available && stance.state === "FAULT");

    canvas.classList.toggle("disabled", !driveAllowed);
    driveNote.textContent = driveAllowed ? "" : "Driving is allowed only on three feet with the shoulder lock seated.";
    if (!driveAllowed && stick.active) {
      releaseStick();
    }
    headButtons.forEach(function (button) {
      button.disabled = !headAllowed;
      if (!headAllowed) {
        button.classList.remove("pressed");
      }
    });
  }

  stanceButtons.forEach(function (button) {
    var target = Number(button.getAttribute("data-stance"));
    button.addEventListener("pointerdown", function (event) {
      if (button.disabled) {
        return;
      }
      event.preventDefault();
      button.setPointerCapture(event.pointerId);
      if (stick.active) {
        releaseStick();
      }
      stanceHeld = target;
      button.classList.add("pressed");
      send({ type: "stance", target: target });
    });
    ["pointerup", "pointercancel", "lostpointercapture"].forEach(function (name) {
      button.addEventListener(name, function () {
        button.classList.remove("pressed");
        if (stanceHeld === target) {
          releaseStance();
        }
      });
    });
  });

  clearFaultButton.addEventListener("click", function () {
    send({ type: "clear_fault" });
  });

  /* -------------------------------------------------------------- joystick */

  function drawStick() {
    var size = canvas.width;
    var centre = size / 2;
    var outer = centre - 10;
    var knob = 34;

    context.clearRect(0, 0, size, size);

    context.fillStyle = "#eef1f7";
    context.beginPath();
    context.arc(centre, centre, outer, 0, Math.PI * 2);
    context.fill();

    context.strokeStyle = "#c7cedd";
    context.lineWidth = 2;
    context.beginPath();
    context.arc(centre, centre, outer, 0, Math.PI * 2);
    context.stroke();
    context.beginPath();
    context.arc(centre, centre, outer * 0.5, 0, Math.PI * 2);
    context.stroke();
    context.beginPath();
    context.moveTo(centre - outer, centre);
    context.lineTo(centre + outer, centre);
    context.moveTo(centre, centre - outer);
    context.lineTo(centre, centre + outer);
    context.stroke();

    var x = centre + stick.x * (outer - knob);
    var y = centre - stick.y * (outer - knob);

    context.fillStyle = stick.active ? "#1e3a8a" : "#1d4ed8";
    context.beginPath();
    context.arc(x, y, knob, 0, Math.PI * 2);
    context.fill();
    context.strokeStyle = "#0b0f19";
    context.lineWidth = 3;
    context.stroke();
  }

  function setFromEvent(event) {
    var box = canvas.getBoundingClientRect();
    var centreX = box.left + box.width / 2;
    var centreY = box.top + box.height / 2;
    var radius = box.width / 2 - (10 / canvas.width) * box.width;

    var dx = (event.clientX - centreX) / radius;
    var dy = (centreY - event.clientY) / radius;

    var length = Math.sqrt(dx * dx + dy * dy);
    if (length > 1.0) {
      dx /= length;
      dy /= length;
    }
    stick.x = dx;
    stick.y = dy;
    drawStick();
  }

  function releaseStick() {
    stick.active = false;
    stick.pointerId = null;
    stick.x = 0.0;
    stick.y = 0.0;
    drawStick();
    send({ type: "drive", x: 0.0, y: 0.0 });
  }

  canvas.addEventListener("pointerdown", function (event) {
    event.preventDefault();
    if (!driveAllowed || stanceHeld !== 0) {
      return;
    }
    stick.active = true;
    stick.pointerId = event.pointerId;
    canvas.setPointerCapture(event.pointerId);
    setFromEvent(event);
  });

  canvas.addEventListener("pointermove", function (event) {
    if (!stick.active || event.pointerId !== stick.pointerId) {
      return;
    }
    event.preventDefault();
    setFromEvent(event);
  });

  ["pointerup", "pointercancel", "pointerleave"].forEach(function (name) {
    canvas.addEventListener(name, function (event) {
      if (event.pointerId !== stick.pointerId) {
        return;
      }
      event.preventDefault();
      releaseStick();
    });
  });

  /* ------------------------------------------------------------- transmit */

  function transmit() {
    var now = Date.now();
    var period = stick.active || stanceHeld !== 0 ? 1000 / DRIVE_HZ : 1000 / IDLE_HZ;
    if (now - lastSent.at < period) {
      return;
    }
    lastSent.at = now;
    if (stanceHeld !== 0) {
      /* Hold-to-run: the server drops the request if this stops for 0.5 s. */
      send({ type: "stance", target: stanceHeld });
    }
    if (stick.active || lastSent.x !== stick.x || lastSent.y !== stick.y) {
      if (send({ type: "drive", x: stick.x, y: stick.y })) {
        lastSent.x = stick.x;
        lastSent.y = stick.y;
      }
    } else {
      send({ type: "ping" });
    }
  }

  window.setInterval(transmit, 1000 / DRIVE_HZ);

  /* -------------------------------------------------------------- controls */

  capSlider.addEventListener("input", function () {
    capValue.textContent = capSlider.value + "%";
    send({ type: "cap", value: Number(capSlider.value) / 100 });
  });

  headSlider.addEventListener("input", function () {
    headValue.textContent = headSlider.value + "%";
    send({ type: "head_duty", value: Number(headSlider.value) / 100 });
  });

  enableBox.addEventListener("change", function () {
    send({ type: "enable", value: enableBox.checked });
  });

  stopButton.addEventListener("click", function () {
    stick.x = 0.0;
    stick.y = 0.0;
    stick.active = false;
    drawStick();
    enableBox.checked = false;
    stanceHeld = 0;
    send({ type: "stance", target: 0 });
    send({ type: "stop" });
    send({ type: "enable", value: false });
  });

  Array.prototype.forEach.call(document.querySelectorAll("[data-head]"), function (button) {
    var direction = Number(button.getAttribute("data-head"));
    function press(event) {
      event.preventDefault();
      button.classList.add("pressed");
      send({ type: "head", direction: direction });
    }
    function release(event) {
      event.preventDefault();
      button.classList.remove("pressed");
      send({ type: "head", direction: 0 });
    }
    button.addEventListener("pointerdown", press);
    button.addEventListener("pointerup", release);
    button.addEventListener("pointercancel", release);
    button.addEventListener("pointerleave", release);
  });

  Array.prototype.forEach.call(document.querySelectorAll("[data-nudge]"), function (button) {
    button.addEventListener("click", function () {
      send({ type: "nudge", direction: Number(button.getAttribute("data-nudge")) });
    });
  });

  Array.prototype.forEach.call(document.querySelectorAll("[data-rgb]"), function (button) {
    button.addEventListener("click", function () {
      var parts = button.getAttribute("data-rgb").split(",");
      send({
        type: "lights",
        r: Number(parts[0]),
        g: Number(parts[1]),
        b: Number(parts[2])
      });
    });
  });

  function buildSoundButtons(names, backend) {
    soundsBox.textContent = "";
    if (!names.length) {
      var empty = document.createElement("p");
      empty.className = "readout";
      empty.textContent = backend
        ? "no clips found; run scripts/generate_audio.py"
        : "no audio back end on the Pi";
      soundsBox.appendChild(empty);
      return;
    }
    names.forEach(function (name) {
      var button = document.createElement("button");
      button.className = "btn";
      button.type = "button";
      button.textContent = name;
      button.addEventListener("click", function () {
        send({ type: "sound", name: name });
      });
      soundsBox.appendChild(button);
    });
  }

  /* Stop driving if the page is hidden: a phone that locks must not leave the
     robot running until the server watchdog notices. */
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) {
      releaseStance();
      releaseStick();
      send({ type: "head", direction: 0 });
    }
  });

  window.addEventListener("pagehide", function () {
    releaseStance();
    send({ type: "stop" });
  });

  drawStick();
  renderStance(null);
  connect();
})();

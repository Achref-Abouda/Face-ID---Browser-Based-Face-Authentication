const { steps, stepCopy, apiUrl } = window.CAPTURE_CONFIG;
let stepIndex = window.CAPTURE_CONFIG.stepIndex;

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const flash = document.getElementById("flash");
const statusLine = document.getElementById("status-line");
const instructionTitle = document.getElementById("instruction-title");
const instructionHint = document.getElementById("instruction-hint");
const stepTrack = document.getElementById("step-track");

const CAPTURE_INTERVAL_MS = 1100;
let capturing = false;
let intervalHandle = null;

function renderInstruction() {
  const step = steps[stepIndex];
  const copy = stepCopy[step];
  instructionTitle.textContent = copy.title;
  instructionHint.textContent = copy.hint;

  [...stepTrack.children].forEach((tick, i) => {
    tick.classList.toggle("done", i < stepIndex);
    tick.classList.toggle("active", i === stepIndex);
  });
}

function setStatus(message, kind) {
  statusLine.textContent = message || "";
  statusLine.classList.remove("ok", "err");
  if (kind) statusLine.classList.add(kind);
}

function flashFrame() {
  flash.classList.remove("flashing");
  // force reflow so the animation can restart
  void flash.offsetWidth;
  flash.classList.add("flashing");
}

async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 800, facingMode: "user" },
      audio: false,
    });
    video.srcObject = stream;
    await video.play();
    intervalHandle = setInterval(captureAndSend, CAPTURE_INTERVAL_MS);
  } catch (err) {
    setStatus("Camera access denied or unavailable. Allow camera access and reload.", "err");
  }
}

function grabFrameDataUrl() {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  // Mirror the capture to match what the user sees in the preview.
  ctx.translate(canvas.width, 0);
  ctx.scale(-1, 1);
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL("image/jpeg", 0.85);
}

async function captureAndSend() {
  if (capturing) return;
  capturing = true;
  try {
    const image = grabFrameDataUrl();
    const res = await fetch(apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image }),
    });
    const data = await res.json();

    if (data.done) {
      clearInterval(intervalHandle);
      flashFrame();
      setStatus("Done.", "ok");
      window.location.href = data.redirect;
      return;
    }

    if (data.ok) {
      flashFrame();
      setStatus(data.message, "ok");
      if (typeof data.next_index === "number") {
        stepIndex = data.next_index;
        renderInstruction();
      }
    } else {
      setStatus(data.message, "err");
    }
  } catch (err) {
    setStatus("Connection issue — retrying…", "err");
  } finally {
    capturing = false;
  }
}

renderInstruction();
startCamera();

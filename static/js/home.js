const nameInput = document.getElementById("name");
const loginBtn = document.getElementById("login-btn");
const signupBtn = document.getElementById("signup-btn");

function syncButtons() {
  const hasName = nameInput.value.trim().length > 0;
  loginBtn.disabled = !hasName;
  signupBtn.disabled = !hasName;
}

nameInput.addEventListener("input", syncButtons);
syncButtons();

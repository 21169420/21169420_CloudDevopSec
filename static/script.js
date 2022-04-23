const loggedInLinks = document.querySelectorAll(".logged-in-links");
const loggedOutLinks = document.querySelectorAll(".logged-out-links");
const loggedInLnksBox = document.querySelector(".login-box");

const displayUi = (user) => {
  if (user) {
    loggedInLinks.forEach((item) => (item.style.display = "none"));
    loggedOutLinks.forEach((item) => (item.style.display = "block"));
  } else {
    loggedInLinks.forEach((item) => (item.style.display = "block"));
    loggedOutLinks.forEach((item) => (item.style.display = "none"));
  }
};

const userRestric = (user) => {
  if (user) {
    if (
      window.location.pathname == "/login" ||
      window.location.pathname == "/signup"
    ) {
      window.location.href = "http://127.0.0.1:8080/profile";
    }
  } else {
    if (
      window.location.pathname == "/profile" ||
      window.location.pathname == "/createEvCar"
    ) {
      window.location.href = "http://127.0.0.1:8080/login";
      console.log("test");
    }
  }
};

("use strict");
window.addEventListener("load", function () {
  console.log("Hello World!");
  firebase.auth().onAuthStateChanged(
    function (user) {
      if (user) {
        console.log(`Signed in as ${user.displayName} (${user.email})`);
        user.getIdToken().then(function (token) {
          document.cookie = "token=" + token + ";path=/";
        });
        displayUi(user);
        userRestric(user);
      } else {
        console.log(window.location.href);
        console.log(window.location.pathname == "/login");
        console.log(window.location.pathname == "/profile");
        document.cookie = "token=;path=/";
        displayUi();
        userRestric();
      }
    },
    function (error) {
      console.log(error);
      alert("Unable to log in: " + error);
    }
  );
});

const auth = firebase.auth();
const database = firebase.database();

function register() {
  const email = this.document.getElementById("email-sign-in").value;
  const fullName = this.document.getElementById("name").value;
  const password = this.document.getElementById("password-sign-in").value;
  if (validate_email(email) == false || validate_password(password) == false) {
    alert("email or password out of line");
    return;
  }
  if (
    validate_field(email) == false ||
    validate_field(password) == false ||
    validate_field(fullName) == false
  ) {
    alert("one or more field is out of line");
    return;
  }
  auth
    .createUserWithEmailAndPassword(email, password)
    .then(function (user) {
      let uid = user.uid;
      let currentUser = firebase.auth().currentUser;

      let database_ref = database.ref();

      let user_data = {
        email: email,
        name: fullName,
        date_now: Date.now(),
      };

      database_ref.child("Users/" + uid).set(user_data);
      alert("you're signed in...");
      window.location.replace("/");

      return currentUser.updateProfile({
        displayName: fullName,
      });
    })
    .catch((error) => {
      const error_code = error.code;
      const error_message = error.message;
      alert(error_message);
    });
}

function login() {
  const email = this.document.getElementById("email").value;
  const password = this.document.getElementById("password").value;
  if (validate_email(email) == false || validate_password(password) == false) {
    alert("email or password out of line");
    return;
  }
  if (validate_field(email) == false || validate_field(password) == false) {
    alert("one or more field is out of line");
    return;
  }
  auth
    .signInWithEmailAndPassword(email, password)
    .then(function (user) {
      let uid = user.uid;

      let database_ref = database.ref();

      let user_data = {
        email: email,
        date_now: Date.now(),
      };

      database_ref.child("Users/" + user.uid).update(user_data);
      alert("you're logged in...");
      window.location.replace("/");
    })
    .catch((error) => {
      const error_code = error.code;
      const error_message = error.message;
      alert(error_message);
    });
}

function validate_email(email) {
  let expression = /^[^@]+@\w+(\.\w+)+\w$/;
  if (expression.test(email) == true) {
    return true;
  } else {
    return false;
  }
}

function validate_password(password) {
  if (password < 8) {
    return false;
  } else {
    return true;
  }
}

function validate_field(field) {
  if (field == null) {
    return false;
  }
  if (field.length <= 0) {
    return false;
  } else {
    return true;
  }
}
function signout() {
  firebase
    .auth()
    .signOut()
    .then(() => {
      // Sign-out successful.
      window.location.replace("/");
    })
    .catch((error) => {
      // An error happened.
    });
}

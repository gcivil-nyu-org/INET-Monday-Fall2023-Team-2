// From https://www.w3schools.com/howto/howto_js_tabs.asp

// Open Active posts tab by default
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("default-open").click();
});

// Open a tab on click
function openTab(evt, tabName) {
  var i, tabcontent, tablinks;

  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  tablinks = document.getElementsByClassName("tablink");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" current", "");
  }

  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " current";
}

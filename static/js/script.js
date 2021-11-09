
  document.addEventListener('DOMContentLoaded', function() {
    var sidenavs = document.querySelectorAll('.sidenav');
    var sidenavsInstance = M.Sidenav.init(sidenavs, {edge: "right"});
  });


$(document).ready(function () {
    $(".sidenav").sidenav({edge: "right"});
    $(".collapsible").collapsible();
});


/*
    vanilla JavaScript for MaterializeCSS initialization
*/

// document.addEventListener('DOMContentLoaded', function () {
//     let sidenavs = document.querySelectorAll(".sidenav");
//     let sidenavsInstance = M.Sidenav.init(sidenavs, {edge: "right"});
//     let collapsibles = document.querySelectorAll(".collapsible");
//     let collapsiblesInstance = M.Collapsible.init(collapsibles);
// });
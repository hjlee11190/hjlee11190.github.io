/*
* Greedy Navigation
*
* http://codepen.io/lukejacksonn/pen/PwmwWV
*
*/

var $nav = $('#site-nav');
var $btn = $('#site-nav button');
var $vlinks = $('#site-nav .visible-links');
var $vlinks_persist_tail = $vlinks.children("*.persist.tail");
var $hlinks = $('#site-nav .hidden-links');

var breaks = [];

function updateNav() {

  var availableSpace = $btn.hasClass('hidden') ? $nav.width() : $nav.width() - $btn.width() - 30;

  // The visible list is overflowing the nav
  if ($vlinks.width() > availableSpace) {

    while ($vlinks.width() > availableSpace && $vlinks.children("*:not(.persist)").length > 0) {
      // Record the width of the list
      breaks.push($vlinks.width());

      // Move item to the hidden list
      $vlinks.children("*:not(.persist)").last().prependTo($hlinks);

      availableSpace = $btn.hasClass("hidden") ? $nav.width() : $nav.width() - $btn.width() - 30;

      // Show the dropdown btn
      $btn.removeClass("hidden");
    }

    // The visible list is not overflowing
  } else {

    // There is space for another item in the nav
    while (breaks.length > 0 && availableSpace > breaks[breaks.length - 1]) {
      // Move the item to the visible list
      if ($vlinks_persist_tail.children().length > 0) {
        $hlinks.children().first().insertBefore($vlinks_persist_tail);
      } else {
        $hlinks.children().first().appendTo($vlinks);
      }
      breaks.pop();
    }

    // Hide the dropdown btn if hidden list is empty
    if (breaks.length < 1) {
      $btn.addClass('hidden');
      $btn.removeClass('close');
      $hlinks.addClass('hidden');
    }
  }

  // Keep counter updated
  $btn.attr("count", breaks.length);

  // update masthead height and the body top padding
  var mastheadHeight = $('.masthead').height();
  $('body').css('padding-top', mastheadHeight + 'px');

  // NOTE: the sidebar used to get `padding-top: mastheadHeight` here, back when
  // it was `position: fixed` and therefore had to clear the fixed masthead on
  // its own. It is `position: sticky` now (see _sass/layout/_sidebar.scss), so
  // it sits inside the flow below the body padding already set above -- adding
  // the padding here too pushed the profile down by a full masthead height.

}

// Window listeners

$(window).on('resize', function () {
  updateNav();
});
screen.orientation.addEventListener("change", function () {
  updateNav();
});

$btn.on('click', function () {
  $hlinks.toggleClass('hidden');
  $(this).toggleClass('close');
});

updateNav();
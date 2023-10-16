var scrollToBottom = function() {
  var scrollInterval = 2500; // Time between scrolls in milliseconds

  function scroll() {
    var prevHeight = 0;

    // Store the current scroll height before scrolling
    prevHeight = document.documentElement.scrollHeight;

    // Scroll to the bottom of the page
    window.scrollTo(0, document.documentElement.scrollHeight);

    // After scrolling, check if the scroll height remains the same, indicating you've reached the bottom
    if (document.documentElement.scrollHeight === prevHeight) {
      // If reached the bottom, wait for a moment and then scroll again
      setTimeout(function() {
        scroll();
      }, scrollInterval);
    } else {
      // If not at the bottom yet, keep scrolling
      setTimeout(scroll, scrollInterval);
    }
  }

  // Start scrolling
  scroll();
};


var insertJQuery = function() {
	var script = document.createElement('script');
	script.src = "https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js";
	document.getElementsByTagName('head')[0].appendChild(script);
};
var outputLikes = function() {
  var separator = ',';
  var results = [];

  // Select all video title and author elements with the specified ID
  var titleElements = document.querySelectorAll('#video-title');
  var authorElements = document.querySelectorAll('a[dir="auto"][spellcheck="false"]');

  // Ensure the elements are found and have the same length
  if (titleElements.length) {
    for (var i = 0; i < titleElements.length; i++) { // Start from the second element
      var videoTitle = titleElements[i].textContent.trim();
      var videoAuthor = authorElements[i+1].textContent.trim();
      results.push(videoTitle + separator + videoAuthor);
    }
  } else {
    console.log("Error: Number of titles and authors does not match.");
    return;
  }

  console.log(results.join('\n'));
};

outputLikes();

outputLikes();
// Start the scrolling loop
scrollToBottom();
insertJQuery();
outputLikes();
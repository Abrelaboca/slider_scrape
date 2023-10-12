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
    var separator = '\t';
    var results = [];

    // Define the XPath expressions for video titles and durations
    var titleXPath = "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-rich-grid-renderer//h3/a/yt-formatted-string";
    var durationXPath = "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-rich-grid-renderer//ytd-playlist-thumbnail/a/yt-formatted-string";

    // Evaluate the XPath expressions to get the title and duration elements
    var titleElements = document.evaluate(titleXPath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
    var durationElements = document.evaluate(durationXPath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);

    // Ensure the number of titles and durations match
    if (titleElements.snapshotLength !== durationElements.snapshotLength) {
        console.log("Error: Number of titles and durations does not match.");
        return;
    }

    // Iterate through the elements and extract titles and durations
    for (var i = 0; i < titleElements.snapshotLength; i++) {
        var videoTitle = titleElements.snapshotItem(i).textContent.trim();
        var videoDuration = durationElements.snapshotItem(i).textContent.trim();
        results.push(videoTitle + separator + videoDuration);
    }

    console.log(results.join('\n'));
};

// Start the scrolling loop
scrollToBottom();
insertJQuery();
outputLikes();
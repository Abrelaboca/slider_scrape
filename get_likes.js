var scrollToBottom = function() {
	var prevHeight = 0;
	var interval = setInterval(function () {
		prevHeight = document.body.scrollHeight;
		window.scrollTo(0, prevHeight);
		if(document.body.scrollHeight > prevHeight) {
			clearInterval(interval);
		}
	}, 2500);
};

var insertJQuery = function() {
	var script = document.createElement('script');
	script.src = "https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js";
	document.getElementsByTagName('head')[0].appendChild(script);
};

var outputLikes = function() {
	var separator = '\t';
	var results = ['User' + separator + 'Track' + separator + 'URL'];
	$(".badgeList__item").each(
		function() {
			var user = $(this).find(".playableTile__usernameHeadingContainer").first().text();
			var track = $(this).find(".playableTile__descriptionContainer a").first();
			var trackTitle = $.trim(track.text());
			var trackUrl = track[0].href;
			var record = $.trim(user) + separator + trackTitle + separator + trackUrl;
			results.push(record);
		});
	console.log(results.join('\n'));
};

try {
	scrollToBottom();
	insertJQuery();
	setTimeout(function() { outputLikes(); }, 3000);
}
catch(err) {
  console.log("Error while scraping data!\n" + err.message);
}
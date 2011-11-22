/* Modified version of CSS3 snow effect by Natalie Downe which can
 * be found at: natbat.net/2010/Jan/15/css3snow/
 */

function Snow() {
	/* Define the number of snowflakes to be used in the animation */
	this.SNOWFLAKES = 20;
	this.snowRunning = false;

	/*
		Receives the lowest and highest values of a range and
		returns a random integer that falls within that range.
	*/
	this.randomInteger = function(low, high) {
		return low + Math.floor(Math.random() * (high - low));
	}

	/*
	   Receives the lowest and highest values of a range and
	   returns a random float that falls within that range.
	*/
	this.randomFloat = function(low, high) {
		return low + Math.random() * (high - low);
	}

	this.randomItem = function(items) {
		return items[this.randomInteger(0, items.length - 1)]
	}

	/* Returns a duration value for the falling animation.*/
	this.durationValue = function(value) {
		return value + 's';
	}

	this.createASnowflake = function(is_first) {
		var flakes = ['2746', '2745', '2744', '2733'];
		var superFlakes = ['2746', '2745', '2744', 'fc7', '274b', '2749', '2747', '2746', '273c', '273b', '2734', '2733', '2732', '2731', '2725'];
		var sizes = ['tiny', 'tiny', 'tiny', 'small', 'small', 'small', 'small', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'large', 'massive'];
	
		/* Start by creating a wrapper div, and an empty span  */
		var snowflakeElement = document.createElement('div');
		snowflakeElement.className = 'snowflake ' + this.randomItem(sizes);
	
		var snowflake = document.createElement('span');
		snowflake.innerHTML = '&#x' + this.randomItem(flakes) + ';';
	
		snowflakeElement.appendChild(snowflake);
	
		/* Randomly choose a spin animation */
		var spinAnimationName = (Math.random() < 0.5) ? 'clockwiseSpin' : 'counterclockwiseSpin';

		/* Randomly choose a side to anchor to, keeps the middle more dense and fits liquid layout */
		var anchorSide = (Math.random() < 0.5) ? 'left' : 'right';

		/* Figure out a random duration for the fade and drop animations */
		var fadeAndDropDuration = this.durationValue(this.randomFloat(5, 20));

		/* Figure out another random duration for the spin animation */
		var spinDuration = this.durationValue(this.randomFloat(4, 8));
	
		// how long to wait before the flakes arrive
		var flakeDelay = is_first ? 0 : this.durationValue(this.randomFloat(0, 1));
	
		snowflakeElement.style.webkitAnimationName = 'fade, drop';
		snowflakeElement.style.webkitAnimationDuration = fadeAndDropDuration + ', ' + fadeAndDropDuration;
		snowflakeElement.style.webkitAnimationDelay = flakeDelay;
	
		/* Position the snowflake at a random location along the screen, anchored to either the left or the right*/
		snowflakeElement.style[anchorSide] = this.randomInteger(5, 40) + '%';
	
		snowflake.style.webkitAnimationName = spinAnimationName;
		snowflake.style.webkitAnimationDuration = spinDuration;
	

		/* Return this snowflake element so it can be added to the document */
		return snowflakeElement;
	}
	
	this.start = function() {
		/* Fill the empty container with freshly driven snow */
		var first = true;
		for (var i = 0; i < this.SNOWFLAKES; i++) {
			document.body.appendChild(this.createASnowflake(first));
			first = false;
		}
		
		this.snowRunning = true;
	}
	
	this.stop = function() {
		$(".snowflake*").remove();
		
		this.snowRunning = false;
	}
}

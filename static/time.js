function startTime() {
	var today = new Date();
	var h = today.getHours();
	var m = today.getMinutes();
	var s = today.getSeconds();
	var am_or_pm = checkAorP(h);
	h = checkTime(lessThan12(h));
	m = checkTime(m);
	s = checkTime(s);
	document.getElementById('time').innerHTML = h + ":" + m + ":" + s + " " + am_or_pm;
	t = setTimeout('startTime()', 500);
}

function lessThan12(h) {
	if (h == 0) {
		h = 12;
	}
	if (h > 12) {
		h -= 12;
	}
	return h;
}

function checkTime(t) {
	if (t < 10) {
		t = "0" + t;
	}
	return t;
}

function checkAorP (h) {
	var am_or_pm = "AM"
	if (h >= 12) {
		am_or_pm = "PM"
	}
	return am_or_pm;
}
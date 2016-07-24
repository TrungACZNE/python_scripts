javascript:(function() {
    var d = document, s = document.body.style;
    if (d.__margin === undefined && d.__width === undefined) {
      d.__margin = s.getPropertyValue("margin");
      d.__width = s.getPropertyValue("width");
      s.setProperty("margin", "auto");
      s.setProperty("width", "900px");
    } else {
      var width = s.getPropertyValue("width");
      width = parseInt(width.slice(0, width.length - 2));
      if (width > 500) {
        width = width - 100;
        s.setProperty("width", width + "px");
      } else {
        s.setProperty("margin", d.__margin);
        s.setProperty("width", d.__width);
        d.__margin = d.__width = undefined;
      }
    }
})()
